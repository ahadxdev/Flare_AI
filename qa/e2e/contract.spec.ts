import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";

test("runtime OpenAPI matches the shared committed contract", async ({ request }) => {
  const contract = JSON.parse(readFileSync("api/openapi.json", "utf8"));
  // The Vite proxy intentionally exposes only API and QA paths.
  const response = await request.get("http://127.0.0.1:8011/openapi.json");
  expect(response.status()).toBe(200);
  expect(await response.json()).toEqual(contract);
});

test("frontend wire-field names and enum values match canonical OpenAPI", () => {
  const schemas = JSON.parse(readFileSync("api/openapi.json", "utf8")).components.schemas;
  const frontend = readFileSync("src/api.ts", "utf8");
  const aliases: Record<string, string> = { InvestigationSource: "Source", Measurement: "MeasurementObservation" };
  for (const match of frontend.matchAll(/export interface (\w+) \{\r?\n([\s\S]*?)\r?\n\}/g)) {
    const [, name, body] = match;
    const schema = schemas[aliases[name] || name];
    if (!schema || !schema.properties) continue; // Query-only and nested error helpers aren't response models.
    const fields = [...body.matchAll(/^  (\w+)\??:/gm)].map(field => field[1]).sort();
    expect(fields, `Canonical fields: ${name}`).toEqual(Object.keys(schema.properties).sort());
  }
  for (const name of ["ResearchArea", "InvestigationEnvironment", "DataAvailability", "SourceVerificationStatus", "ScenarioEnvironment", "ScenarioObjective"]) {
    const type = frontend.match(new RegExp(`export type ${name} =([\\s\\S]*?);`))![1];
    const values = [...type.matchAll(/"([^\"]+)"/g)].map(value => value[1]).sort();
    // Pydantic inlines Literal enums; locate the canonical property using its type name.
    const properties: Record<string, [string, string]> = {
      ResearchArea: ["Investigation", "research_area"], DataAvailability: ["Investigation", "data_availability"],
      InvestigationEnvironment: ["Investigation", "environment"],
      SourceVerificationStatus: ["Source", "verification_status"], ScenarioEnvironment: ["ScenarioRequest", "environment"],
      ScenarioObjective: ["ScenarioRequest", "objective"],
    };
    const [model, field] = properties[name];
    expect(values, `Canonical enum: ${name}`).toEqual([...schemas[model].properties[field].enum].sort());
  }
});
