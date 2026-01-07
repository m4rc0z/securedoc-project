import { test, expect } from '@playwright/test';
import * as path from 'path';

test.describe('Document Upload Flow', () => {
    test('should upload a PDF document successfully', async ({ page }) => {
        // Mock key API routes
        await page.route('**/api/documents/upload', async route => {
            const json = {
                status: 'success',
                chunks_count: 5,
                filename: 'test-document.pdf'
            };
            await route.fulfill({ json });
        });

        await page.goto('/');

        // Upload a dummy file
        // Create a dummy PDF file in memory or use a buffer? 
        // Playwright setInputFiles supports buffers
        await page.getByLabel('Upload Document').or(page.locator('input[type="file"]')).setInputFiles({
            name: 'test-document.pdf',
            mimeType: 'application/pdf',
            buffer: Buffer.from('dummy content')
        });

        // Click upload button
        const uploadButton = page.getByRole('button', { name: 'Upload PDF' });
        await expect(uploadButton).toBeEnabled();

        const uploadPromise = page.waitForResponse(res => res.url().includes('/api/documents/upload') && res.status() === 200);
        await uploadButton.click();

        // Verify loading state
        await expect(uploadButton).toBeDisabled();
        await expect(uploadButton).toHaveText('Uploading...');

        await uploadPromise;

        // Verify completion state (button re-enabled)
        await expect(uploadButton).toBeEnabled();
        await expect(uploadButton).toHaveText('Upload PDF');

        // Verify success message

        // Verify success message
        await expect(page.locator('text=Upload successful!')).toBeVisible({ timeout: 15000 });

        // Verify file input is cleared (optional, UI behavior)
    });

    test('should handle upload error', async ({ page }) => {
        // Mock error response
        await page.route('**/api/documents/upload', async route => {
            await route.fulfill({
                status: 500,
                contentType: 'application/json',
                body: JSON.stringify({ error: 'Upload failed' })
            });
        });

        await page.goto('/');

        await page.locator('input[type="file"]').setInputFiles({
            name: 'error.pdf',
            mimeType: 'application/pdf',
            buffer: Buffer.from('error content')
        });

        const uploadPromise = page.waitForResponse(res => res.url().includes('/api/documents/upload') && res.status() === 500);
        const uploadButton = page.getByRole('button', { name: 'Upload PDF' });
        await expect(uploadButton).toBeEnabled();
        await uploadButton.click();
        await uploadPromise;

        await expect(page.locator('text=Upload failed. Please try again.')).toBeVisible({ timeout: 15000 });
    });
});
