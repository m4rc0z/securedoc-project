import { test, expect } from '@playwright/test';

test.describe('System Guard - Connectivity Check', () => {

    // 1. Python Backend Health
    test('Python Backend should be healthy', async ({ request }) => {
        const response = await request.get('http://localhost:8000/health');
        expect(response.status()).toBe(200);
        const body = await response.json();
        expect(body.status).toBe('ok');
        console.log('✅ Python Backend is UP');
    });

    // 2. Java Backend Health
    test('Java Backend should be healthy', async ({ request }) => {
        const response = await request.get('http://localhost:8081/api/health'); // Updated to /api/health
        expect(response.status()).toBe(200);
        const body = await response.json();
        expect(body.status).toBe('UP');
        console.log('✅ Java Backend is UP');
    });

    // 3. Frontend Proxy Health
    test('Frontend Proxy should route to Backend', async ({ request }) => {
        // This verifies that http://localhost:4200/api/health -> http://localhost:8081/health
        const response = await request.get('http://localhost:4200/api/health');
        expect(response.status()).toBe(200); // 200 means proxy worked
        const body = await response.json();
        expect(body.status).toBe('UP');
        console.log('✅ Frontend Proxy is WORKING');
    });

    // 4. Basic Chat Flow (Smoke Test)
    test('End-to-End Chat should work', async ({ page }) => {
        await page.goto('http://localhost:4200');

        const input = page.locator('input[placeholder*="Ask a question"]');
        await expect(input).toBeVisible();
        await input.fill('System Check');
        await page.keyboard.press('Enter');

        // Wait for ANY response bubble from bot
        // We look for the div with bg-gray-200 (bot message style)
        const botMessage = page.locator('.bg-gray-200').last();
        await expect(botMessage).toBeVisible({ timeout: 10000 });

        // Check it's not an error message
        const text = await botMessage.textContent();
        console.log(`✅ Received Bot Response: "${text}"`);
        expect(text).not.toContain('Error:');
    });

});
