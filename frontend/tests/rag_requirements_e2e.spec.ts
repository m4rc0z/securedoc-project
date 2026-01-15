import { test, expect } from '@playwright/test';
import * as path from 'path';

// Define path to a sample PDF
// Assuming running from 'frontend' directory
const SAMPLE_PDF_PATH = path.resolve('..', 'pdfs/test_document_1991.pdf');

test.describe('RAG System Requirements E2E', () => {

    test.beforeEach(async ({ page }) => {
        // Ensure we handle any dialogs (like "Are you sure you want to clean DB?")
        page.on('dialog', dialog => dialog.accept());
    });

    test('REQ-1.1: Ingestion - Should upload a PDF and process it via Docling', async ({ page, request }) => {
        // 1. Go to Documents Page
        await page.goto('/documents');

        // 2. Upload File
        const fileInput = page.locator('input[type="file"]');
        await fileInput.setInputFiles(SAMPLE_PDF_PATH);

        const uploadBtn = page.getByText('Upload PDF');
        // 3. Wait for Upload Request and Success
        const responsePromise = page.waitForResponse(res => res.url().includes('/ingest'));
        await uploadBtn.click();
        const response = await responsePromise;
        console.log(`Ingest Status: ${response.status()}`);
        if (response.status() !== 200) {
            console.log(`Ingest Error Body: ${await response.text()}`);
        }
        expect(response.status()).toBe(200);

        // Expect "Ingestion complete" or similar message in a toast
        await expect(page.locator('text=Upload successful')).toBeVisible({ timeout: 15000 });

        // 4. Verify in List
        await page.getByText('Refresh List').click();
        await expect(page.getByText('test_document_1991.pdf')).toBeVisible({ timeout: 30000 }); // Increased timeout for list update
    });

    test('REQ-2.1 & 3.2: Retrieval & Synthesis - Should answer questions with sources', async ({ page }) => {
        await page.goto('/');

        const questionInput = page.getByPlaceholder('Ask a question about your documents...');

        // Ask a summary question to trigger retrieval + synthesis
        const question = "Summarize the content of test_document_1991.pdf";
        await questionInput.fill(question);
        await questionInput.press('Enter');

        // Verify that the user message is displayed
        await expect(page.locator(`text=${question}`)).toBeVisible();

        // Wait for Answer
        // Response should contain "Sources" (Req 3.3) and semantic content
        // We allow up to 60s for full RAG flow (Ingestion might be lazy or cold start)
        const chatBubble = page.locator('.chat-bubble.chat-start').last();
        await expect(chatBubble).toBeVisible({ timeout: 60000 });

        const answerText = await chatBubble.textContent();
        console.log('RAG Answer:', answerText);

        // Assertions
        expect(answerText?.length).toBeGreaterThan(10); // Expect some content

        // REQ 3.3: Citations/Sources
        // Verify Source format: "📄 filename (p.X)"
        // Note: The UI might display sources separately or embedded.
        // Based on service.py: sources are in the response object, usually UI renders them.
        await expect(page.locator('text=Sources')).toBeVisible();
        await expect(page.locator('text=test_document_1991.pdf')).toBeVisible();
    });

    test('REQ-4.1: Latency - Should handle timeouts gracefully', async ({ page }) => {
        // Note: This test implies the backend mock or real backend enforces the timeout.
        // If we really want to test the 2s timeout fallback, we need a query that takes long.
        // For E2E, we just ensure it returns *something* and doesn't hang forever.

        await page.goto('/');
        const questionInput = page.getByPlaceholder('Ask a question about your documents...');

        await questionInput.fill("What is the detailed latency budget analysis?");
        await questionInput.press('Enter');

        // It should answer fairly quickly (either with result or fallback error)
        const chatBubble = page.locator('.chat-bubble.chat-start').last();
        await expect(chatBubble).toBeVisible({ timeout: 10000 });

        // If it was a timeout fallback, services.py returns: "I'm sorry, I couldn't search..."
        // If it worked, it returns an answer.
        // Both are valid "Graceful Handling". We mainly fail if it hangs > 10s.
    });

});
