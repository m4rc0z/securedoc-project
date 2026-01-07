import { test, expect } from '@playwright/test';

test.describe('Chat Interaction Flow', () => {
    test('should send a question and receive an answer', async ({ page }) => {
        // Mock Chat API
        await page.route('**/api/chat', async route => {
            const json = {
                answer: 'This is a mock answer from the AI.',
                sources: ['Page 1', 'Page 2']
            };
            await route.fulfill({ json });
        });

        await page.goto('/');

        // Type question
        const questionInput = page.getByPlaceholder('Ask a question about your documents...');
        await questionInput.fill('what is the summary?');
        await questionInput.press('Enter');

        // Verify user message appears
        await expect(page.locator('text=what is the summary?')).toBeVisible();

        // Wait for the response to verify interception
        const response = await page.waitForResponse(res => res.url().includes('/api/chat'));
        console.log('Intercepted response status:', response.status());

        // Verify loading state (might be too fast to catch, but check for result)
        // await expect(page.locator('text=Thinking...')).toBeVisible(); 

        // Verify bot response
        await expect(page.locator('text=This is a mock answer from the AI.')).toBeVisible({ timeout: 10000 });
        await expect(page.locator('text=Sources:')).toBeVisible();
        await expect(page.locator('text=Page 1')).toBeVisible();
    });

    test('should handle empty input', async ({ page }) => {
        await page.goto('/');
        const sendButton = page.getByRole('button', { name: 'Send' });

        // Wait for hydration/initialization
        await expect(sendButton).toBeVisible();

        // Button should be disabled when input is empty
        await page.getByPlaceholder('Ask a question about your documents...').fill('');
        await expect(sendButton).toBeDisabled();

        // Should be enabled when typed
        await page.getByPlaceholder('Ask a question about your documents...').fill('hello');
        await expect(sendButton).toBeEnabled();

        // Should be diabled again if cleared
        await page.getByPlaceholder('Ask a question about your documents...').fill('   ');
        await expect(sendButton).toBeDisabled();
    });
});
