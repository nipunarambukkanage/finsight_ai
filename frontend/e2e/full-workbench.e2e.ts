import { expect, test } from '@playwright/test';

const workspaceRoutes = [
  { path: '/', label: 'dashboard', heading: 'Financial Intelligence Dashboard', navId: 'nav-dashboard' },
  { path: '/stocks', label: 'stocks workspace', heading: 'AAPL', navId: 'nav-stocks' },
  { path: '/stocks/AAPL', label: 'ticker detail workspace', heading: 'AAPL' },
  { path: '/assistant', label: 'research assistant', heading: 'FinSight Context-Aware Research Assistant', navId: 'nav-assistant' },
  { path: '/research-agent', label: 'research agent', heading: 'AI Multi-Stage Equity Research Agent', navId: 'nav-agent' },
  { path: '/workflow', label: 'workflow hub', heading: 'Autonomous Research & Strategy Workflow Hub', navId: 'nav-workflow' },
  { path: '/documents', label: 'document intelligence', heading: 'Financial Document Intelligence & Filing Comparison', navId: 'nav-documents' },
  { path: '/rag', label: 'RAG explorer', heading: 'LangChain RAG Vector Knowledge Explorer', navId: 'nav-rag' },
  { path: '/portfolio', label: 'portfolio intelligence', heading: 'Institutional Portfolio Intelligence & Risk Architecture', navId: 'nav-portfolio' },
  { path: '/sentiment', label: 'sentiment engine', heading: 'Financial Sentiment Engine', navId: 'nav-sentiment' },
  { path: '/analytics-lab', label: 'quantitative analytics lab', heading: 'Python Quantitative Analytics Laboratory', navId: 'nav-analytics' },
  { path: '/ml-lab', label: 'machine learning lab', heading: 'Responsible Time-Series Machine Learning Lab', navId: 'nav-ml' },
  { path: '/multimodal', label: 'multimodal workspace', heading: 'Vision-Language Multimodal Financial Intelligence', navId: 'nav-multimodal' },
  { path: '/voice', label: 'voice briefing workspace', heading: 'Voice AI Financial Assistant & Audio Briefings', navId: 'nav-voice' },
  { path: '/showcase', label: 'technology showcase', heading: 'Enterprise Engineering Capabilities & Technology Showcase', navId: 'nav-showcase' },
  { path: '/settings', label: 'settings workspace', heading: 'System Settings & AI Provider Failover Architecture', navId: 'nav-settings' }
];

test.describe('complete FinSight workspace coverage', () => {
  test.describe.configure({ mode: 'parallel' });

  for (const route of workspaceRoutes) {
    test(`renders the ${route.label}`, async ({ page }) => {
      await page.goto(route.path);

      await expect(page).toHaveURL(route.path === '/' ? /\/$/ : new RegExp(`${route.path}$`));
      await expect(page.locator('#main-sidebar')).toBeVisible();
      await expect(page.getByRole('heading', { name: route.heading, exact: false })).toBeVisible({ timeout: 20000 });
    });
  }

  test('keeps the primary navigation connected to every workspace', async ({ page }) => {
    await page.goto('/');

    for (const route of workspaceRoutes.filter(({ navId }) => navId && navId !== 'nav-dashboard')) {
      await page.getByTestId(route.navId!).click();
      await expect(page).toHaveURL(new RegExp(`${route.path}$`));
      await expect(page.getByRole('heading', { name: route.heading, exact: false })).toBeVisible({ timeout: 20000 });
    }
  });

  test('switches the dashboard theme without losing the route', async ({ page }) => {
    await page.goto('/');

    await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
    await page.getByRole('button', { name: 'Toggle theme' }).click();
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');
    await expect(page).toHaveURL(/\/$/);
    await page.getByRole('button', { name: 'Toggle theme' }).click();
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  });

  test('exposes stock timeframe and analytical tabs', async ({ page }) => {
    await page.goto('/stocks');
    await expect(page.getByRole('heading', { name: 'AAPL', exact: true })).toBeVisible({ timeout: 20000 });

    await page.getByRole('button', { name: '1M', exact: true }).click();
    await page.getByRole('button', { name: 'Fundamental Financials', exact: true }).click();
    await expect(page.getByText('REVENUE (TTM)', { exact: true })).toBeVisible();
    await page.getByRole('button', { name: 'Quantitative Risk & VaR', exact: true }).click();
    await expect(page.getByText('ANNUALIZED VOLATILITY', { exact: true })).toBeVisible();
  });

  test('keeps document upload and RAG query controls interactive', async ({ page }) => {
    await page.goto('/documents');
    await page.getByRole('button', { name: 'Upload Financial Filing (PDF)' }).click();
    await expect(page.getByText(/successfully parsed and 6 vector chunks indexed/)).toBeVisible();

    await page.goto('/rag');
    const query = page.locator('#rag-query-input');
    await page.getByRole('button', { name: /What are Apple's geopolitical supply chain risks/ }).click();
    await expect(query).toHaveValue("What are Apple's geopolitical supply chain risks?");
    await expect(page.locator('#rag-query-submit-btn')).toBeEnabled();
  });

  test('applies provider settings through the client control', async ({ page }) => {
    await page.goto('/settings');
    await page.locator('input[type="radio"][value="OPENAI"]').check();
    await page.getByRole('button', { name: 'Apply Provider Configuration' }).click();
    await expect(page.getByText(/Active AI Provider switched to OPENAI/)).toBeVisible();
  });

  test('switches multimodal analysis targets and preserves the prompt', async ({ page }) => {
    await page.goto('/multimodal');
    const prompt = page.locator('#multimodal-prompt-input');
    await expect(prompt).toHaveValue(/Analyze this technical candlestick chart/);
    await page.getByRole('button', { name: 'Balance Sheet Table', exact: true }).click();
    await expect(page.getByRole('button', { name: 'Balance Sheet Table', exact: true })).toBeVisible();
    await expect(page.locator('#run-multimodal-btn')).toBeEnabled();
  });
});
