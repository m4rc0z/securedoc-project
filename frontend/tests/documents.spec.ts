import { test, expect } from '@playwright/test';
import * as path from 'path';

test.describe('Document Management', () => {
    test('should upload, list, and delete a document', async ({ page, request }) => {
        // 1. Prepare: Ensure backend is reachable
        const healthCheck = await request.get('http://localhost:8081/api/documents');
        expect(healthCheck.ok()).toBeTruthy();

        // 2. Go to Documents Page
        await page.goto('http://localhost:4200/documents');
        await expect(page.getByText('Document Management')).toBeVisible();

        // 3. Upload File via UI
        // We need to use the UploadComponent which is on / and /documents? 
        // Actually UploadComponent is in AppComponent layout, so it's always visible.
        const fileInput = page.locator('input[type="file"]');
        await fileInput.setInputFiles({
            name: 'test_doc.txt',
            mimeType: 'text/plain',
            buffer: Buffer.from('This is a test document content for Playwright.')
        });

        const uploadBtn = page.getByText('Upload PDF'); // Component says Upload PDF
        await uploadBtn.click();

        // Wait for upload to finish (Toast or List update)
        // Refresh list to be sure
        await page.waitForTimeout(2000);
        await page.getByText('Refresh List').click();

        // 4. Verify Document is Listed
        await expect(page.getByText('test_doc.txt')).toBeVisible();

        // 5. Delete Document
        page.on('dialog', dialog => dialog.accept()); // Handle confirm dialog

        // Use a more specific locator for the delete button of this specific row
        // Find row containing 'test_doc.txt' then find Delete button
        const row = page.getByRole('row', { name: 'test_doc.txt' });
        const deleteBtn = row.getByRole('button', { name: 'Delete' });
        await deleteBtn.click();

        // 6. Verify Document is Gone
        await page.waitForTimeout(1000);
        await expect(page.getByText('test_doc.txt')).not.toBeVisible();
    });
});
