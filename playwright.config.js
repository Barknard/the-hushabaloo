// @ts-check
import { defineConfig, devices } from '@playwright/test';

/**
 * The suite runs against a site assembled exactly the way the Pages workflow
 * assembles it, and served from the same SUBPATH Pages serves it from.
 *
 * `reuseExistingServer` is false on purpose. Reusing a stale dev server is how a
 * suite goes green against a build that no longer exists — every run assembles
 * _site fresh from the current player and audio.
 */
export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? 'github' : 'list',

  use: {
    baseURL: 'http://127.0.0.1:4173',
    trace: 'on-first-retry',
    // The suite drives REAL playback, which means a test run blasts the book
    // through the machine's speakers. Chromium can be muted at launch; WebKit
    // has no such flag, so tests/mute.js handles every engine.
    launchOptions: { args: ['--mute-audio'] },
  },

  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'] } },
    // The twins will meet this book on a tablet, and Etta on a phone.
    { name: 'tablet',  use: { ...devices['iPad (gen 7)'] } },
    { name: 'phone',   use: { ...devices['iPhone 13'] } },
  ],

  webServer: {
    command: 'node tools/serve-site.mjs',
    url: 'http://127.0.0.1:4173/the-hushabaloo/',
    reuseExistingServer: false,
    timeout: 60000,
  },
});
