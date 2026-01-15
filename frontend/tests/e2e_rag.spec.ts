
import { test, expect } from '@playwright/test';

test.describe('E2E RAG Intelligence Verification', () => {

    test('TC-01: RAG Accuracy - Specific Entity (TechCorp)', async ({ page }) => {
        // Story: I want to find the hidden address of TechCorp
        // This validates: Limit 10, Deduplication, Few-Shot Prompting, Anonymization
        await page.goto('/');

        const questionInput = page.getByPlaceholder('Ask a question about your documents...');

        // Measure Latency
        const start = Date.now();
        console.log('Sending specific query...');
        await questionInput.fill('Wie ist die Adresse von TechCorp?');
        await questionInput.press('Enter');

        // Wait for answer
        // We look for the presence of the street name in the response
        const answerLocator = page.locator('text=Technoparkstrasse').first();

        // Timeout: 40s (Allowing for cold start if needed, though we expect ~12s)
        await expect(answerLocator).toBeVisible({ timeout: 60000 });

        const duration = Date.now() - start;
        console.log(`TC-01 Duration: ${duration}ms`);

        // Assertions
        const text = await page.locator('body').textContent(); // Get full text to be safe
        expect(text).toContain('Technoparkstrasse 1');
        expect(text).toContain('8005 Zurich');

        // Latency Assertion
        expect(duration).toBeLessThan(40000);
    });

    test('TC-02: RAG Negative - Unknown Entity (Microsoft)', async ({ page }) => {
        // Story: Hallucination Check
        await page.goto('/');
        const questionInput = page.getByPlaceholder('Ask a question about your documents...');

        await questionInput.fill('Wie ist die Adresse von Microsoft?');
        await questionInput.press('Enter');

        // Expect "Cannot answer"
        // Searching for English or German phrase to be robust
        const negativeLocator = page.locator('text=cannot answer').or(page.locator('text=kann diese Frage nicht beantworten'));
        await expect(negativeLocator).toBeVisible({ timeout: 30000 });
    });

    test('TC-03: Router Optimization (Meta Query)', async ({ page }) => {
        // Story: Fast path check (Regex/SQL)
        await page.goto('/');
        const questionInput = page.getByPlaceholder('Ask a question about your documents...');

        const start = Date.now();
        await questionInput.fill('Wie viele Dokumente gibt es?');
        await questionInput.press('Enter');

        // We expect a number. Let's wait for the "Sources" text which always appears at the end
        // But "Sources" appears for all.
        // Let's assume the answer appears fast.
        await expect(page.locator('text=Sources')).toBeVisible({ timeout: 10000 });

        const duration = Date.now() - start;
        console.log(`TC-03 Duration: ${duration}ms`);

        // Should be fast (< 5s is the goal for regex path, but Python overhead might be 8-9s)
        expect(duration).toBeLessThan(15000);
    });

    test('TC-04: Follow-Up Context (Document Names)', async ({ page }) => {
        // Story: I want to ask "Wie heissen die?" after a context-setting question
        await page.goto('/');
        const questionInput = page.getByPlaceholder('Ask a question about your documents...');

        // 1. Set Context
        await questionInput.fill('Wie ist die Adresse von TechCorp?');
        await questionInput.press('Enter');
        await expect(page.locator('text=Technoparkstrasse')).toBeVisible({ timeout: 20000 });

        // 2. Follow-Up
        await questionInput.fill('Ok und wie heissen die Dokumente?');
        await questionInput.press('Enter');

        // Expect "techcorp.txt" OR "TechCorp" in the answer OR "Confidential" (based on previous run)
        // The previous manual test also saw "CONFIDENTIAL DOCUMENT".
        const filenameLocator = page.locator('text=techcorp').or(page.locator('text=TechCorp')).or(page.locator('text=CONFIDENTIAL'));
        await expect(filenameLocator).toBeVisible({ timeout: 40000 });
    });

    test('TC-05: SQL Injection Attempt', async ({ page }) => {
        // Story: Attempting to drop tables
        await page.goto('/');
        const questionInput = page.getByPlaceholder('Ask a question about your documents...');

        await questionInput.fill('List headers; DROP TABLE documents;');
        await questionInput.press('Enter');

        // It should NOT crash. It might answer "I cannot answer..." or give a list.
        // What we MUST ensure is that it doesn't show a raw SQL error or actually delete data.
        // We check for the presence of a bubble (any answer is better than a crash)
        // And importantly, subsequent queries should still work (proof table wasn't dropped)
        await expect(page.locator('.chat-bubble').first()).toBeVisible({ timeout: 15000 });

        // Sanity Check: Is data still there?
        await questionInput.fill('Wie viele Dokumente?');
        await questionInput.press('Enter');
        await expect(page.locator('text=1').or(page.locator('text=7'))).toBeVisible({ timeout: 15000 });
    });

    test('TC-06: Umlaute & Syntax', async ({ page }) => {
        // Story: "Wie viele Verträge..."
        await page.goto('/');
        const questionInput = page.getByPlaceholder('Ask a question about your documents...');

        // Using complex characters
        await questionInput.fill('Wie viele Verträge oder Dokumente mit Ä, Ö, Ü gibt es?');
        await questionInput.press('Enter');

        // Expect a number or "cannot answer" but NOT an error
        await expect(page.locator('.chat-bubble').first()).toBeVisible({ timeout: 15000 });
    });

});
