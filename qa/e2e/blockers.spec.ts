// These are strict release gates. Leave failures visible until the owners fix them.
import { test, expect } from "@playwright/test";
import { analyze, catalog, moonBase } from "./helpers";

test("QA-01 exact journey: ranked evidence opens details by stable ID", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Explore investigations" }).click();
  await page.getByRole("button", { name: /View investigation.*\(psi-98\)$/ }).click();
  await expect(page.locator(".detail-content .record-id")).toHaveText("psi-98");
  const analysis = await analyze(page);
  const match = analysis.matches[0];
  const card = page.locator(".match-card").first();
  await expect.soft(card).toContainText(match.investigation_id);
  const control = card.getByRole("button", { name: /detail|view|open/i })
    .or(card.locator('a[href^="#investigation/"]'));
  await expect(control).toHaveCount(1);
  await control.click();
  await expect(page.locator(".detail-content .record-id")).toHaveText(match.investigation_id);
});

test("QA-03 pressure with an omitted unit is rejected", async ({ request }) => {
  const response = await request.post("/api/scenarios/analyze", {
    data: { ...moonBase, pressure: { value: 10.2 } },
  });
  expect(response.status()).toBe(422);
});

test("QA-02 citations expose stable source IDs in investigation details", async ({ page, request }) => {
  const records = await catalog(request);
  const record = records.find(item => item.investigation_id === "psi-98")!;
  await page.goto("/#investigation/psi-98");
  await expect(page.locator(".detail-content .record-id")).toHaveText(record.investigation_id);
  for (const source of record.sources) {
    const row = page.locator(".citation-list li").filter({ has: page.getByRole("link", { name: source.document_title, exact: true }) });
    await expect(row).toContainText(source.source_id);
  }
});

test("QA-03 invalid pressure units are rejected at HTTP boundary", async ({ request }) => {
  const response = await request.post("/api/scenarios/analyze", {
    data: { ...moonBase, pressure: { value: 10.2, unit: "bananas" } },
  });
  expect(response.status()).toBe(422);
  expect((await response.json()).error.code).toBe("VALIDATION_ERROR");
});

test("QA-04 generated brief retains visible investigation IDs", async ({ page, request }) => {
  const analysis = await request.post("/api/scenarios/analyze", { data: moonBase });
  const { scenario_id } = await analysis.json();
  const response = await request.post("/api/reports", { data: {
    scenario_id, investigation_ids: ["psi-98", "psi-bass-ii"], include_measurements: true, format: "html",
  } });
  expect(response.status()).toBe(200);
  const brief = await response.json();
  // Render the returned export in the browser; API IDs alone cannot prove export traceability.
  await page.setContent(brief.content);
  for (const id of ["psi-98", "psi-bass-ii"]) {
    await expect(page.locator("body")).toContainText(new RegExp(`(?<![A-Za-z0-9_-])${id}(?![A-Za-z0-9_-])`));
  }
});
