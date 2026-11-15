import { test, expect } from "@playwright/test";
import type { ChatResponse, ComparisonResponse, ReportResponse } from "../../src/api";
import { analyze, catalog, citationIdentity, navigate, visibleCitations } from "./helpers";

test("dashboard through research brief (explicit explorer detour for QA-01)", async ({ page, request }) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  const records = await catalog(request);
  expect(records.map(record => record.investigation_id).sort())
    .toEqual(["psi-98", "psi-99", "psi-bass-ii", "psi-flex"]);
  const selected = ["psi-98", "psi-bass-ii"].map(id => records.find(record => record.investigation_id === id)!);

  await test.step("open dashboard and browse a source-verified investigation", async () => {
    await page.goto("/");
    await expect(page.getByRole("note", { name: "Fixture demo mode" })).toBeVisible();
    await expect(page.locator(".metric-card").filter({ hasText: "INDEXED INVESTIGATIONS" })
      .locator(".metric-value")).toHaveText(String(records.length));
    await page.getByRole("button", { name: "Explore investigations" }).click();
    await page.getByRole("button", { name: `View investigation ${selected[0].title} (${selected[0].investigation_id})`, exact: true }).click();
    await expect(page).toHaveURL(/#investigation\/psi-98$/);
    await expect(page.locator(".detail-content .record-id")).toHaveText("psi-98");
    await expect(page.locator(".citation-list")).toContainText("verified");
    await expect(page.locator(".info-row").filter({ has: page.getByText("Oxygen", { exact: true }) }))
      .toContainText("Not reported");
    await page.reload();
    await expect(page.locator(".detail-content .record-id")).toHaveText("psi-98");
  });

  const analysis = await analyze(page);
  const ordered = [...analysis.matches].sort((a, b) => b.relevance_score - a.relevance_score || a.investigation_id.localeCompare(b.investigation_id));
  expect(analysis.matches).toEqual(ordered);
  expect(analysis.matches.map(match => match.investigation_id).sort()).toEqual(records.map(record => record.investigation_id).sort());
  for (const [index, match] of analysis.matches.entries()) {
    const card = page.locator(".match-card").nth(index);
    await expect(card.getByRole("heading", { level: 3 })).toHaveText(match.title);
    expect(match.score_breakdown.parameter_similarity).toBeNull();
    await expect(card).toContainText("Parameters (30%) Unavailable");
    match.citations.forEach(citation => citationIdentity(citation, records.filter(record => record.investigation_id === match.investigation_id)));
    await visibleCitations(card, match.citations);
  }

  await test.step("QA-01 detour: return to Explorer because ranked matches cannot open details", async () => {
    test.info().annotations.push({ type: "blocker", description: "QA-01: explicit Explorer detour; strict path is tested separately" });
    await navigate(page, "Investigation Explorer");
    for (const record of selected) {
      await page.getByRole("button", { name: `View investigation ${record.title} (${record.investigation_id})`, exact: true }).click();
      await expect(page.locator(".detail-content .record-id")).toHaveText(record.investigation_id);
      await page.getByRole("button", { name: "Select for comparison", exact: true }).click();
      await page.getByRole("button", { name: "Back to Investigation Explorer", exact: true }).click();
    }
  });

  await navigate(page, "Compare");
  const comparisonPending = page.waitForResponse("**/api/compare");
  await page.getByRole("button", { name: "Compare 2 selected", exact: true }).click();
  const comparisonResponse = await comparisonPending;
  expect(comparisonResponse.status()).toBe(200);
  expect(comparisonResponse.request().postDataJSON()).toEqual({ investigation_ids: selected.map(record => record.investigation_id) });
  const comparison: ComparisonResponse = await comparisonResponse.json();
  expect(comparison.investigations.map(record => record.investigation_id)).toEqual(selected.map(record => record.investigation_id));
  for (const record of comparison.investigations) {
    const scope = page.getByRole("region", { name: `Sources for ${record.title}` });
    await expect(scope).toContainText(record.investigation_id);
    record.citations.forEach(citation => citationIdentity(citation, selected.filter(item => item.investigation_id === record.investigation_id)));
    await visibleCitations(scope, record.citations);
  }
  await expect(page.getByRole("row").filter({ has: page.getByRole("rowheader", { name: "conditions", exact: true }) }))
    .toContainText("Not reported");

  await navigate(page, "AI Research Assistant");
  await page.getByLabel("Research question", { exact: true }).fill("What does Saffire report about flammability and combustion?");
  const chatPending = page.waitForResponse("**/api/chat");
  await page.getByRole("button", { name: "Ask", exact: true }).click();
  const chatResponse = await chatPending;
  expect(chatResponse.status()).toBe(200);
  expect(chatResponse.request().postDataJSON()).toMatchObject({ scenario_id: analysis.scenario_id, investigation_ids: selected.map(record => record.investigation_id) });
  const chat: ChatResponse = await chatResponse.json();
  expect(chat.answer_status).toBe("grounded");
  expect(chat.evidence.length).toBeGreaterThan(0);
  for (const evidence of chat.evidence) {
    expect(selected.map(record => record.investigation_id)).toContain(evidence.investigation_id);
    const citation = chat.citations.find(item => item.source_id === evidence.source_id && item.quote_or_supported_excerpt === evidence.excerpt);
    expect(citation).toBeDefined();
    expect(citation).toMatchObject({ source_url: evidence.source_url, page_number: evidence.page_number, section: evidence.section });
    await expect(page.locator(".chat-answer")).toContainText(evidence.excerpt);
  }
  chat.citations.forEach(citation => citationIdentity(citation, selected));
  await visibleCitations(page.locator(".chat-answer"), chat.citations);
  await expect(page.locator(".chat-answer")).toContainText("not a NASA-reported fact");

  await navigate(page, "Research Brief");
  const briefPending = page.waitForResponse("**/api/reports");
  await page.getByRole("button", { name: "Generate brief", exact: true }).click();
  const briefResponse = await briefPending;
  expect(briefResponse.status()).toBe(200);
  const body = briefResponse.request().postDataJSON();
  expect(body).toEqual({ scenario_id: analysis.scenario_id, investigation_ids: selected.map(record => record.investigation_id), include_measurements: true, format: "html" });
  const brief: ReportResponse = await briefResponse.json();
  expect(brief.ranked_investigations).toEqual(analysis.matches.filter(match => body.investigation_ids.includes(match.investigation_id)));
  expect(brief.measurements).toEqual([]);
  brief.citations.forEach(citation => citationIdentity(citation, selected));
  await visibleCitations(page.locator(".report-card"), brief.citations);
  for (const record of selected) await expect(page.locator(".report-card")).toContainText(record.title);
  await expect(page.locator(".report-card")).toContainText("30");
  await expect(page.locator(".report-card")).toContainText("10.2 psi");
  await expect(page.locator(".report-card")).toContainText("user-entered hypothetical");
  await expect(page.locator(".report-card")).toContainText("No verified measurements");
  await expect(page.locator(".report-card")).toContainText("partial gravity");
  const repeat = await request.post("/api/reports", { data: body });
  expect(repeat.ok()).toBeTruthy();
  expect((await repeat.json()).report_id).toBe(brief.report_id);
  expect(errors).toEqual([]);
});
