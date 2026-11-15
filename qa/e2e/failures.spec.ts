import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
import { catalog, moonBase, navigate, visibleCitations, citationIdentity } from "./helpers";

test("missing scientific fields remain unknown in details and comparison", async ({ page, request }) => {
  const record = (await catalog(request)).find(item => item.investigation_id === "psi-98")!;
  expect(record.conditions).toMatchObject({ oxygen_pct: null, pressure: { value: null, unit: null } });
  expect(record.findings).toEqual([]);
  await page.goto("/#investigation/psi-98");
  for (const label of ["Oxygen", "Pressure", "Sensors", "Materials or fuels"]) {
    const row = page.locator(".info-row").filter({ has: page.getByText(label, { exact: true }) });
    await expect(row.locator("strong")).toHaveText("Not reported");
  }
  const comparison = await request.post("/api/compare", { data: { investigation_ids: ["psi-98", "psi-99"] } });
  expect(comparison.status()).toBe(200);
  const fields = (await comparison.json()).field_comparisons;
  for (const key of ["conditions", "sensors", "findings"]) {
    expect(fields.find((field: { field: string }) => field.field === key).status).toBe("not_comparable");
  }
});

test("no search results use zero counts without replacing dashboard totals", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator(".catalog-pill")).toContainText("4 indexed records");
  await navigate(page, "Investigation Explorer");
  await page.getByLabel("Search investigations").fill("zzzxqvnonexistent");
  const pending = page.waitForResponse(response => response.url().includes("/api/investigations?") && response.url().includes("zzzxqvnonexistent"));
  await page.getByRole("button", { name: "Apply filters" }).click();
  expect((await (await pending).json()).total).toBe(0);
  await expect(page.getByRole("heading", { name: "No indexed investigations", exact: true })).toBeVisible();
  await expect(page.locator(".record-card")).toHaveCount(0);
  await expect(page.locator(".count-badge")).toHaveText("0 records");
  await navigate(page, "Dashboard");
  await expect(page.locator(".metric-card").filter({ hasText: "INDEXED INVESTIGATIONS" }).locator(".metric-value")).toHaveText("4");
});

test("empty numeric dataset renders no chart, points, or measurement rows", async ({ page, request }) => {
  const response = await request.get("/api/measurements");
  expect(response.status()).toBe(200);
  expect((await response.json()).data).toEqual([]);
  await page.goto("/#explorer");
  await page.getByRole("tab", { name: "Verified measurements" }).click();
  await expect(page.getByRole("heading", { name: /No verified measurements indexed/ })).toBeVisible();
  await expect(page.locator(".measurement-chart, .measurement-point, .measurements-view table tbody tr")).toHaveCount(0);
  await expect(page.locator("#measurements-panel")).not.toContainText(/NaN|Infinity/);
});

test("nonempty chart preserves exact fixture observations and adds no sample points", async ({ page }) => {
  // Explicit synthetic UI probe; it does not pretend that these are NASA measurements.
  const fixture = JSON.parse(readFileSync("qa/fixtures/chart.json", "utf8"));
  await page.route("**/api/measurements?*", route => route.fulfill({ json: fixture }));
  await page.goto("/#explorer");
  await page.getByRole("tab", { name: "Verified measurements" }).click();
  await expect(page.locator(".measurement-chart")).toHaveCount(1);
  await expect(page.locator(".measurement-point")).toHaveCount(1);
  await expect(page.locator(".measurement-point title")).toHaveText("fixture-chart-study: 7.250 s; FIXTURE chart source - not NASA (fixture-chart-source)");
  await expect(page.locator(".measurements-view table tbody tr")).toHaveCount(1);
  await expect(page.getByRole("cell", { name: "7.250", exact: true })).toBeVisible();
  await expect(page.locator(".measurement-chart")).toContainText("fixture-chart-source");
  await expect(page.locator(".measurements-view")).not.toContainText(/NaN|Infinity/);
});

test("malformed numeric response is rejected rather than plotted", async ({ page }) => {
  const fixture = JSON.parse(readFileSync("qa/fixtures/chart.json", "utf8"));
  fixture.data[0].value = null;
  await page.route("**/api/measurements?*", route => route.fulfill({ json: fixture }));
  await page.goto("/#explorer");
  await page.getByRole("tab", { name: "Verified measurements" }).click();
  await expect(page.locator("#measurements-panel")).toContainText("incompatible measurements response");
  await expect(page.locator(".measurement-point")).toHaveCount(0);
});

test("empty catalog returns no ranking, citations, measurements, or invented counts", async ({ page }) => {
  await page.route("**/api/**", async route => {
    const url = new URL(route.request().url());
    url.pathname = `/__qa__/empty${url.pathname}`;
    await route.fulfill({ response: await route.fetch({ url: url.toString() }) });
  });
  await page.goto("/");
  await expect(page.locator(".metric-card").filter({ hasText: "INDEXED INVESTIGATIONS" }).locator(".metric-value")).toHaveText("0");
  await expect(page.locator(".dashboard-record")).toHaveCount(0);
  await navigate(page, "Mission Scenario");
  const pending = page.waitForResponse("**/api/scenarios/analyze");
  await page.getByRole("button", { name: "Analyze research relevance" }).click();
  const analysis = await (await pending).json();
  expect(analysis.matches).toEqual([]);
  await expect(page.getByRole("heading", { name: "No research matches available" })).toBeVisible();
  await expect(page.locator(".match-card")).toHaveCount(0);
  await navigate(page, "AI Research Assistant");
  await page.getByLabel("Research question", { exact: true }).fill("What is known about combustion?");
  const chatPending = page.waitForResponse("**/api/chat");
  await page.getByRole("button", { name: "Ask", exact: true }).click();
  const chat = await (await chatPending).json();
  expect(chat).toMatchObject({ answer_status: "insufficient_evidence", evidence: [], citations: [] });
  await expect(page.locator(".chat-answer")).toContainText("Not available in indexed sources");
  await expect(page.locator(".chat-answer .citation-list a")).toHaveCount(0);
});

test("backend down shows unavailable state and no fabricated catalog counts; retry recovers", async ({ page }) => {
  await page.route("**/api/**", route => route.abort("connectionrefused"));
  await page.goto("/");
  await expect(page.locator(".sidebar-bottom")).toContainText("API unavailable");
  await expect(page.locator(".metric-card").filter({ hasText: "INDEXED INVESTIGATIONS" })).toContainText("Could not reach");
  await expect(page.locator(".metric-value, .nav-count, .catalog-pill, .dashboard-record")).toHaveCount(0);
  await page.unroute("**/api/**");
  await page.locator(".metric-card").filter({ hasText: "API STATUS" }).getByRole("button", { name: "Retry" }).click();
  await page.locator(".metric-card").filter({ hasText: "INDEXED INVESTIGATIONS" }).getByRole("button", { name: "Retry" }).click();
  await expect(page.locator(".sidebar-bottom")).toContainText("API online");
  await expect(page.locator(".metric-card").filter({ hasText: "INDEXED INVESTIGATIONS" }).locator(".metric-value")).toHaveText("4");
});

test("unavailable source link keeps its identity and never becomes verified", async ({ page, context, request }) => {
  const records = await catalog(request);
  const source = records.find(record => record.investigation_id === "psi-bass-ii")!.sources.find(source => source.verification_status === "unavailable")!;
  await context.route(source.source_url, route => route.fulfill({ status: 503, contentType: "text/plain", body: "FIXTURE: source link unavailable" }));
  await page.goto("/#investigation/psi-bass-ii");
  const row = page.locator(".citation-list li").filter({ has: page.getByRole("link", { name: source.document_title, exact: true }) });
  await expect(row).toContainText("unavailable");
  await expect(row).not.toContainText("original file preserved");
  const popupPending = page.waitForEvent("popup");
  await row.getByRole("link").click();
  const popup = await popupPending;
  await expect(popup).toHaveURL(source.source_url);
  await expect(popup.locator("body")).toContainText("FIXTURE: source link unavailable");
  await popup.close();
  await expect(row).toContainText("unavailable");
  expect((await (await request.get("/api/investigations/psi-bass-ii")).json()).sources)
    .toContainEqual(source);
});

test("real LLM HTTP timeout returns evidence-only fallback with intact citations", async ({ page, request }) => {
  const records = await catalog(request);
  await page.route("**/api/chat", async route => {
    const url = new URL("/__qa__/timeout/api/chat", route.request().url());
    await route.fulfill({ response: await route.fetch({ url: url.toString() }) });
  });
  await page.goto("/#assistant");
  await page.getByLabel("Research question", { exact: true }).fill("What does Saffire report about combustion and flammability?");
  const pending = page.waitForResponse("**/api/chat");
  await page.getByRole("button", { name: "Ask", exact: true }).click();
  const response = await pending;
  expect(response.status()).toBe(200);
  const chat = await response.json();
  expect(chat.answer_status).toBe("grounded");
  expect(chat.evidence.length).toBeGreaterThan(0);
  expect(chat.limitations.join(" ")).toContain("timed out or failed");
  await expect(page.locator(".chat-answer")).toContainText("only retrieved excerpts are presented");
  for (const citation of chat.citations) citationIdentity(citation, records);
  await visibleCitations(page.locator(".chat-answer"), chat.citations);
  await expect(page.getByRole("button", { name: "Ask", exact: true })).toBeEnabled();
});

for (const [label, patch] of [
  ["oxygen exceeds 100 percent", { oxygen_pct: 101 }],
  ["negative pressure", { pressure: { value: -1, unit: "psi" } }],
  ["empty pressure unit", { pressure: { value: 10.2, unit: "" } }],
] as const) {
  test(`invalid input: ${label}`, async ({ request }) => {
    const response = await request.post("/api/scenarios/analyze", { data: { ...moonBase, ...patch } });
    expect(response.status()).toBe(422);
    const body = await response.json();
    expect(body.error.code).toBe("VALIDATION_ERROR");
    expect(body.error.details.length).toBeGreaterThan(0);
  });
}

test("missing optional scenario numeric inputs remain null", async ({ request }) => {
  const response = await request.post("/api/scenarios/analyze", { data: {
    environment: "lunar_habitat", objective: "general", oxygen_pct: null,
    pressure: { value: null, unit: null }, material_or_fuel: null,
  } });
  expect(response.status()).toBe(200);
  expect((await response.json()).scenario).toMatchObject({ oxygen_pct: null, pressure: { value: null, unit: null } });
});

test("invalid scenario error is visible and corrected browser input can be submitted", async ({ page }) => {
  await page.goto("/#scenario");
  await page.getByLabel("Oxygen (%)", { exact: true }).fill("101");
  const pending = page.waitForResponse("**/api/scenarios/analyze");
  await page.getByRole("button", { name: "Analyze research relevance" }).click();
  const rejected = await pending;
  expect(rejected.status()).toBe(422);
  const { error } = await rejected.json();
  expect(error.code).toBe("VALIDATION_ERROR");
  await expect(page.getByRole("alert")).toContainText(error.message);
  await expect(page.locator(".match-card")).toHaveCount(0);
  await page.getByLabel("Oxygen (%)", { exact: true }).fill("30");
  const corrected = page.waitForResponse("**/api/scenarios/analyze");
  await page.getByRole("button", { name: "Analyze research relevance" }).click();
  expect((await corrected).status()).toBe(200);
  await expect(page.getByRole("alert")).toHaveCount(0);
  await expect(page.locator(".match-card")).toHaveCount(4);
});

test("unknown investigation, stale scenario, and empty selection return contract errors", async ({ request, page }) => {
  const missing = await request.get("/api/investigations/qa-missing-id");
  expect(missing.status()).toBe(404);
  expect((await missing.json()).error.code).toBe("NOT_FOUND");
  await page.goto("/#investigation/qa-missing-id");
  await expect(page.getByRole("heading", { name: "Investigation not found", exact: true })).toBeVisible();
  const stale = await request.post("/api/reports", { data: { scenario_id: "qa-stale", investigation_ids: ["psi-98"], include_measurements: true, format: "html" } });
  expect(stale.status()).toBe(404);
  expect((await stale.json()).error.code).toBe("NOT_FOUND");
  const empty = await request.post("/api/compare", { data: { investigation_ids: [] } });
  expect(empty.status()).toBe(422);
  expect((await empty.json()).error.code).toBe("VALIDATION_ERROR");
});
