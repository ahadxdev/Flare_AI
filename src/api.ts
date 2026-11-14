export type ResearchArea =
  | "prevention"
  | "detection"
  | "suppression"
  | "fundamentals"
  | "related"
  | "other";

export type Investigation = {
  investigation_id: string;
  title: string;
  acronym: string | null;
  research_area: ResearchArea;
  objectives: string[];
  materials_or_fuels: string[];
  environment: "microgravity" | "normal_gravity" | "other" | "unknown";
  conditions: {
    oxygen_pct: number | null;
    pressure: { value: number | null; unit: string | null };
    other: string[];
  };
  hardware: string[];
  sensors: string[];
  variables_measured: string[];
  findings: string[];
  data_availability: "metadata_only" | "documents" | "numeric_dataset" | "unknown";
  sources: Citation[];
  last_verified_at: string | null;
};

export type Citation = {
  source_id: string;
  document_title: string;
  source_url: string;
  page_number: number | null;
  section: string | null;
  quote_or_supported_excerpt: string | null;
};

export type InvestigationPage = {
  items: Investigation[];
  page: number;
  page_size: number;
  total: number;
};

export type ScenarioRequest = {
  environment: "lunar_habitat" | "mars_habitat" | "spacecraft" | "spacesuit" | "custom";
  oxygen_pct: number | null;
  pressure: { value: number | null; unit: string | null };
  material_or_fuel: string | null;
  objective:
    | "material_flammability"
    | "fire_detection"
    | "fire_suppression"
    | "combustion_fundamentals"
    | "general";
};

export type ScenarioMatch = {
  investigation_id: string;
  title: string;
  relevance_score: number;
  score_breakdown: {
    objective_match: number;
    parameter_similarity: number;
    measurement_usefulness: number;
    context_hardware: number;
  };
  match_reasons: string[];
  limitations: string[];
  citations: Citation[];
};

export type ScenarioAnalysis = {
  scenario_id: string;
  score_type: "research_relevance_not_fire_risk";
  scenario: ScenarioRequest;
  matches: ScenarioMatch[];
  research_gaps: string[];
  limitations: string[];
};

export type Measurement = {
  measurement_id: string;
  investigation_id: string;
  variable: string;
  value: number;
  unit: string;
  source_id: string;
  conditions: Record<string, string | number | null>;
};

export type Report = {
  report_id: string;
  title: string;
  brief: string;
  citations: Citation[];
  limitations: string[];
  research_gaps: string[];
};

type APIErrorBody = { error?: { code?: string; message?: string } };

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as APIErrorBody;
    throw new Error(
      body.error?.message ?? `Request failed with status ${response.status}`,
    );
  }
  return (await response.json()) as T;
}

export const api = {
  investigations(params: URLSearchParams = new URLSearchParams()) {
    return request<InvestigationPage>(`/api/investigations?${params}`);
  },
  investigation(id: string) {
    return request<Investigation>(`/api/investigations/${encodeURIComponent(id)}`);
  },
  analyze(scenario: ScenarioRequest) {
    return request<ScenarioAnalysis>("/api/scenarios/analyze", {
      method: "POST",
      body: JSON.stringify(scenario),
    });
  },
  compare(ids: string[]) {
    return request<{ investigations: Investigation[]; limitations: string[] }>(
      "/api/compare",
      { method: "POST", body: JSON.stringify({ investigation_ids: ids }) },
    );
  },
  chat(question: string) {
    return request<{ answer: string; citations: Citation[]; limitations: string[] }>(
      "/api/chat",
      { method: "POST", body: JSON.stringify({ question }) },
    );
  },
  measurements() {
    return request<{ items: Measurement[] }>("/api/measurements");
  },
  report(ids: string[]) {
    return request<Report>("/api/reports", {
      method: "POST",
      body: JSON.stringify({ investigation_ids: ids }),
    });
  },
};
