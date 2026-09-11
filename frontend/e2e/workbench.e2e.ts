import { expect, test } from '@playwright/test';

test.describe('FinSight research workbench', () => {
  test('loads the dashboard with its operating context', async ({ page }) => {
    await page.goto('/');

    await expect(page).toHaveTitle(/FinSight AI/);
    await expect(page.getByRole('heading', { name: 'Financial Intelligence Dashboard' })).toBeVisible();
    await expect(page.getByTestId('demo-mode-badge')).toContainText('Demo AI Mode Active');
    await expect(page.getByRole('navigation', { name: 'Primary navigation' })).toBeVisible();
  });

  test('moves from the dashboard to the stateful workflow hub', async ({ page }) => {
    await page.goto('/');
    await page.getByTestId('nav-workflow').click();

    await expect(page).toHaveURL(/\/workflow$/);
    await expect(page.getByRole('heading', { name: 'Autonomous Research & Strategy Workflow Hub' })).toBeVisible();
    await expect(page.getByText('LANGGRAPH STATEFUL EXECUTION PIPELINE')).toBeVisible();
    await expect(page.getByText('1. Market Data')).toBeVisible();
  });

  test('opens the sentiment workspace with a ready input', async ({ page }) => {
    await page.goto('/');
    await page.getByTestId('nav-sentiment').click();

    await expect(page).toHaveURL(/\/sentiment$/);
    await expect(page.getByRole('heading', { name: /Financial Sentiment Engine/ })).toBeVisible();
    await expect(page.getByLabel('Financial commentary')).toBeVisible();
  });
});
