export type ResearchArea =
  | "prevention"
  | "detection"
  | "suppression"
  | "fundamentals"
  | "related"
  | "other";

export type InvestigationEnvironment =
  | "microgravity"
  | "normal_gravity"
  | "other"
  | "unknown";

export type DataAvailability =
  | "metadata_only"
  | "documents"
  | "numeric_dataset"
  | "unknown";

export type ScenarioEnvironment =
  | "lunar_habitat"
  | "mars_habitat"
  | "spacecraft"
  | "spacesuit"
  | "custom";

export type ScenarioObjective =
  | "material_flammability"
  | "fire_detection"
  | "fire_suppression"
  | "combustion_fundamentals"
  | "general";

export interface Pressure {
  value: number | null;
  unit: string | null;
}

export interface InvestigationConditions {
  oxygen_pct: number | null;
  pressure: Pressure;
  other: string[];
}

export interface InvestigationSource {
  source_id: string;
  document_title: string;
  source_url: string;
  page_number: number | null;
  section: string | null;
  source_type: "NASA_PSI" | "NASA_REPORT" | "NASA_DATASET" | "OTHER";
}

export interface SourceCitation {
  source_id: string;
  document_title: string;
  source_url: string;
  page_number: number | null;
  section: string | null;
  quote_or_supported_excerpt: string | null;
}

export interface Investigation {
  investigation_id: string;
  title: string;
  acronym: string | null;
  research_area: ResearchArea;
  objectives: string[];
  materials_or_fuels: string[];
  environment: InvestigationEnvironment;
  conditions: InvestigationConditions;
  hardware: string[];
  sensors: string[];
  variables_measured: string[];
  findings: string[];
  data_availability: DataAvailability;
  sources: InvestigationSource[];
  last_verified_at: string | null;
}

export interface InvestigationPage {
  items: Investigation[];
  page: number;
  page_size: number;
  total: number;
}

export interface ScenarioRequest {
  environment: ScenarioEnvironment;
  oxygen_pct: number | null;
  pressure: Pressure;
  material_or_fuel: string | null;
  objective: ScenarioObjective;
}

export interface ScoreBreakdown {
  objective_match: number | null;
  parameter_similarity: number | null;
  measurement_usefulness: number | null;
  context_hardware: number | null;
}

export interface ScenarioMatch {
  investigation_id: string;
  title: string;
  relevance_score: number;
  score_breakdown: ScoreBreakdown;
  evidence_completeness: number;
  match_reasons: string[];
  limitations: string[];
  citations: SourceCitation[];
}

export interface ScenarioAnalysisResponse {
  scenario_id: string;
  score_type: "research_relevance_not_fire_risk";
  scenario: ScenarioRequest;
  matches: ScenarioMatch[];
  research_gaps: string[];
  limitations: string[];
}

export interface ComparisonRequest {
  investigation_ids: string[];
}

export interface ComparisonResponse {
  investigations: Investigation[];
  limitations: string[];
}

export interface ChatRequest {
  question: string;
  investigation_ids?: string[];
}

export interface ChatResponse {
  answer: string;
  citations: SourceCitation[];
  limitations: string[];
}

export interface Measurement {
  measurement_id: string;
  investigation_id: string;
  variable: string;
  value: number;
  unit: string;
  source_id: string;
  conditions: Record<string, string | number | null>;
}

export interface MeasurementList {
  items: Measurement[];
}

export interface ReportRequest {
  investigation_ids: string[];
}

export interface ReportResponse {
  report_id: string;
  title: string;
  brief: string;
  citations: SourceCitation[];
  limitations: string[];
  research_gaps: string[];
}

export interface HealthResponse {
  status: "ok";
}

export interface APIErrorDetail {
  field: string;
  message: string;
}

export interface APIErrorResponse {
  error: {
    code: "VALIDATION_ERROR" | "NOT_FOUND" | "NO_EVIDENCE" | "INTERNAL_ERROR";
    message: string;
    details: APIErrorDetail[];
  };
}

export class APIRequestError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly code?: APIErrorResponse["error"]["code"],
    readonly details: APIErrorDetail[] = [],
  ) {
    super(message);
    this.name = "APIRequestError";
  }
}

function isErrorResponse(payload: unknown): payload is APIErrorResponse {
  if (typeof payload !== "object" || payload === null || !("error" in payload)) {
    return false;
  }
  const error = payload.error;
  return (
    typeof error === "object" &&
    error !== null &&
    "message" in error &&
    typeof error.message === "string"
  );
}

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(url, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
  } catch {
    throw new APIRequestError(
      "Could not reach the FLARE AI API. Check the backend connection and retry.",
      0,
    );
  }

  const payload: unknown = await response.json().catch(() => undefined);
  if (!response.ok) {
    if (isErrorResponse(payload)) {
      throw new APIRequestError(
        payload.error.message,
        response.status,
        payload.error.code,
        payload.error.details,
      );
    }
    throw new APIRequestError(
      `The API request failed with status ${response.status}.`,
      response.status,
    );
  }
  if (payload === undefined) {
    throw new APIRequestError("The API returned an unreadable response.", response.status);
  }
  return payload as T;
}

export const api = {
  health(): Promise<HealthResponse> {
    return request<HealthResponse>("/api/health");
  },
  investigations(params: URLSearchParams = new URLSearchParams()): Promise<InvestigationPage> {
    return request<InvestigationPage>(`/api/investigations?${params}`);
  },
  investigation(id: string): Promise<Investigation> {
    return request<Investigation>(`/api/investigations/${encodeURIComponent(id)}`);
  },
  analyze(scenario: ScenarioRequest): Promise<ScenarioAnalysisResponse> {
    return request<ScenarioAnalysisResponse>("/api/scenarios/analyze", {
      method: "POST",
      body: JSON.stringify(scenario),
    });
  },
  compare(requestBody: ComparisonRequest): Promise<ComparisonResponse> {
    return request<ComparisonResponse>("/api/compare", {
      method: "POST",
      body: JSON.stringify(requestBody),
    });
  },
  chat(requestBody: ChatRequest): Promise<ChatResponse> {
    return request<ChatResponse>("/api/chat", {
      method: "POST",
      body: JSON.stringify(requestBody),
    });
  },
  measurements(params: URLSearchParams = new URLSearchParams()): Promise<MeasurementList> {
    return request<MeasurementList>(`/api/measurements?${params}`);
  },
  report(requestBody: ReportRequest): Promise<ReportResponse> {
    return request<ReportResponse>("/api/reports", {
      method: "POST",
      body: JSON.stringify(requestBody),
    });
  },
};
