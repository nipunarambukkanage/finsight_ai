import { defineConfig, devices } from '@playwright/test';

const startServer = process.env.PLAYWRIGHT_START_SERVER === '1';
const startPort = process.env.PLAYWRIGHT_PORT ?? '4174';
const resolvedBaseURL = process.env.PLAYWRIGHT_BASE_URL ?? `http://127.0.0.1:${startServer ? startPort : '5173'}`;

export default defineConfig({
  testDir: './e2e',
  testMatch: '**/*.e2e.ts',
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: resolvedBaseURL,
    channel: process.env.PLAYWRIGHT_BROWSER_CHANNEL,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure'
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    }
  ],
  ...(startServer
    ? {
        webServer: {
          command: `npm run dev -- --host 127.0.0.1 --port ${startPort}`,
          url: `http://127.0.0.1:${startPort}`,
          reuseExistingServer: false,
          timeout: 120000
        }
      }
    : {})
});
