import { defineConfig, devices } from "@playwright/test";

// Set FLARE_QA_PYTHON to the interpreter with requirements-dev.txt installed.
const python = process.env.FLARE_QA_PYTHON || "python";
export default defineConfig({
  testDir: "./qa/e2e",
  timeout: 30_000,
  expect: { timeout: 5_000 },
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [["list"], ["html", { open: "never" }], ["json", { outputFile: "test-results/qa-results.json" }]],
  use: {
    baseURL: "http://127.0.0.1:5178",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command: `"${python}" qa/server.py`,
      url: "http://127.0.0.1:8011/__qa__/info",
      reuseExistingServer: false, timeout: 60_000,
    },
    {
      command: 'node node_modules/vite/bin/vite.js --config qa/vite.config.ts',
      url: "http://127.0.0.1:5178", reuseExistingServer: false, timeout: 60_000,
    },
  ],
});
