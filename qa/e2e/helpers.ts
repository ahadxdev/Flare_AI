import { expect, type APIRequestContext, type Locator, type Page } from "@playwright/test";
import type { Investigation, ScenarioAnalysisResponse, SourceCitation } from "../../src/api";

export const moonBase = {
  environment: "lunar_habitat", oxygen_pct: 30,
  pressure: { value: 10.2, unit: "psi" }, material_or_fuel: null, objective: "general",
};

export async function catalog(request: APIRequestContext): Promise<Investigation[]> {
  const response = await request.get("/api/investigations?page_size=100");
  expect(response.ok()).toBeTruthy();
  expect(response.headers()["x-flare-data-mode"]).toBe("fixture-offline-demo");
  return (await response.json()).items;
}

export async function navigate(page: Page, name: string) {
  await page.getByRole("navigation", { name: "Primary navigation" })
    .getByRole("link", { name: new RegExp(`^${name}(?: \\d+ investigations)?$`) }).click();
}

export async function analyze(page: Page): Promise<ScenarioAnalysisResponse> {
  await navigate(page, "Mission Scenario");
  await page.getByLabel("Mission environment").selectOption("lunar_habitat");
  await page.getByLabel("Oxygen (%)", { exact: true }).fill("30");
  await page.getByLabel("Pressure (psi)", { exact: true }).fill("10.2");
  const pending = page.waitForResponse("**/api/scenarios/analyze");
  await page.getByRole("button", { name: "Analyze research relevance" }).click();
  const response = await pending;
  expect(response.status()).toBe(200);
  expect(response.request().postDataJSON()).toEqual(moonBase);
  const analysis = await response.json();
  expect(analysis.scenario).toEqual(moonBase);
  expect(analysis.score_type).toBe("research_relevance_not_fire_risk");
  await expect(page.locator(".match-card")).toHaveCount(analysis.matches.length);
  return analysis;
}

// Compare identity/provenance with the independent curated catalog, allowing a citation
// to locate a more specific page/excerpt than its source-level metadata.
export function citationIdentity(citation: SourceCitation, records: Investigation[]) {
  const sources = records.flatMap(record => record.sources)
    .filter(source => source.source_id === citation.source_id);
  expect(sources.length, `Unknown source ${citation.source_id}`).toBeGreaterThan(0);
  const source = sources[0];
  for (const key of ["source_id", "source_url", "document_title", "verification_status",
    "sha256", "file_size_bytes", "local_file_path", "downloaded_at", "last_verified_at", "mime_type"] as const) {
    expect(citation[key], `${citation.source_id}.${key}`).toEqual(source[key]);
  }
}

export async function visibleCitations(scope: Locator, citations: SourceCitation[]) {
  for (const citation of citations) {
    const links = scope.getByRole("link", { name: citation.document_title, exact: true });
    expect(await links.count()).toBeGreaterThan(0);
    for (const link of await links.all()) {
      await expect(link).toHaveAttribute("href", citation.source_url);
      await expect(link).toHaveAttribute("rel", "noreferrer");
    }
  }
}
