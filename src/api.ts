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
export type SourceVerificationStatus = "verified" | "unverified" | "unavailable";

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
  local_file_path: string | null;
  downloaded_at: string | null;
  sha256: string | null;
  file_size_bytes: number | null;
  mime_type: string | null;
  last_verified_at: string | null;
  verification_status: SourceVerificationStatus;
}

export interface SourceCitation {
  source_id: string;
  document_title: string;
  source_url: string;
  page_number: number | null;
  section: string | null;
  quote_or_supported_excerpt: string | null;
  local_file_path: string | null;
  downloaded_at: string | null;
  sha256: string | null;
  file_size_bytes: number | null;
  mime_type: string | null;
  last_verified_at: string | null;
  verification_status: SourceVerificationStatus;
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

export interface InvestigationQuery {
  q?: string;
  research_area?: ResearchArea;
  environment?: InvestigationEnvironment;
  data_availability?: DataAvailability;
  page?: number;
  page_size?: number;
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

export interface ComparisonInvestigation {
  investigation_id: string;
  title: string;
  acronym: string | null;
  research_area: ResearchArea;
  environment: InvestigationEnvironment;
  data_availability: DataAvailability;
  citations: SourceCitation[];
}

export type ComparisonFieldName =
  | "objectives"
  | "research_area"
  | "environment"
  | "conditions"
  | "materials_or_fuels"
  | "hardware"
  | "sensors"
  | "variables_measured"
  | "findings"
  | "data_availability";

export interface ComparisonValue {
  investigation_id: string;
  value: string | string[] | InvestigationConditions | null;
}

export interface FieldComparison {
  field: ComparisonFieldName;
  status: "same" | "different" | "not_comparable";
  values: ComparisonValue[];
  explanation: string | null;
}

export interface ComparisonResponse {
  investigations: ComparisonInvestigation[];
  field_comparisons: FieldComparison[];
  differences_summary: string[];
  limitations: string[];
}

export interface ChatRequest {
  question: string;
  scenario_id?: string | null;
  investigation_ids?: string[];
  research_area?: ResearchArea | null;
}

export interface ChatEvidence {
  source_id: string;
  investigation_id: string;
  document_title: string;
  source_url: string;
  page_number: number | null;
  section: string | null;
  excerpt: string;
}

export interface ChatResponse {
  answer: string;
  evidence: ChatEvidence[];
  citations: SourceCitation[];
  limitations: string[];
  answer_status: "grounded" | "insufficient_evidence";
}

export interface Measurement {
  measurement_id: string;
  investigation_id: string;
  variable: string;
  value: number;
  reported_value: string | null;
  unit: string;
  observation_context: Record<string, string | number | null>;
  source_id: string;
  document_title: string;
  source_url: string;
  page_number: number | null;
  section: string | null;
  table_reference: string | null;
  supporting_excerpt: string | null;
  extraction_method: "pdf_text" | "pdf_table_text" | "metadata_text" | "manual";
  confidence: number | null;
  reviewed_by: string | null;
  reviewed_at: string | null;
  review_notes?: string | null;
}

export interface MeasurementList {
  data: Measurement[];
  data_availability: DataAvailability;
  message: string;
}

export interface ReportRequest {
  scenario_id: string;
  investigation_ids: string[];
  include_measurements: boolean;
  format: "html" | "markdown";
}

export interface ReportResponse {
  report_id: string;
  title: string;
  generated_at: string;
  format: "html" | "markdown";
  content: string;
  brief: string;
  scenario: ScenarioRequest;
  ranked_investigations: ScenarioMatch[];
  comparison: ComparisonResponse | null;
  measurements: Measurement[];
  evidence: SourceCitation[];
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

function isRecord(payload: unknown): payload is Record<string, unknown> {
  return typeof payload === "object" && payload !== null && !Array.isArray(payload);
}

function isMeasurementPoint(payload: unknown): payload is Measurement {
  if (!isRecord(payload)) return false;
  let isSecureSource = false;
  if (typeof payload.source_url === "string") {
    try {
      isSecureSource = new URL(payload.source_url).protocol === "https:";
    } catch {
      isSecureSource = false;
    }
  }
  return (
    typeof payload.measurement_id === "string" &&
    typeof payload.investigation_id === "string" &&
    typeof payload.variable === "string" &&
    typeof payload.value === "number" &&
    Number.isFinite(payload.value) &&
    (payload.reported_value === null || typeof payload.reported_value === "string") &&
    typeof payload.unit === "string" &&
    typeof payload.source_id === "string" &&
    typeof payload.document_title === "string" &&
    isSecureSource &&
    (payload.page_number === null ||
      (typeof payload.page_number === "number" &&
        Number.isInteger(payload.page_number) &&
        payload.page_number >= 1)) &&
    (payload.section === null || typeof payload.section === "string") &&
    (payload.table_reference === null ||
      typeof payload.table_reference === "string") &&
    (payload.supporting_excerpt === null ||
      typeof payload.supporting_excerpt === "string") &&
    ["pdf_text", "pdf_table_text", "metadata_text", "manual"].includes(
      String(payload.extraction_method),
    ) &&
    (payload.confidence === null ||
      (typeof payload.confidence === "number" &&
        Number.isFinite(payload.confidence) &&
        payload.confidence >= 0 &&
        payload.confidence <= 1)) &&
    (payload.reviewed_by === null || typeof payload.reviewed_by === "string") &&
    (payload.reviewed_at === null || typeof payload.reviewed_at === "string") &&
    (payload.review_notes === undefined ||
      payload.review_notes === null ||
      typeof payload.review_notes === "string") &&
    isRecord(payload.observation_context)
  );
}

function isMeasurementList(payload: unknown): payload is MeasurementList {
  return (
    isRecord(payload) &&
    Array.isArray(payload.data) &&
    payload.data.every(isMeasurementPoint) &&
    ["metadata_only", "documents", "numeric_dataset", "unknown"].includes(
      String(payload.data_availability),
    ) &&
    typeof payload.message === "string"
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
  investigations(query: InvestigationQuery = {}): Promise<InvestigationPage> {
    const params = new URLSearchParams();
    for (const [field, value] of Object.entries(query)) {
      if (value !== undefined) params.set(field, String(value));
    }
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
    return request<unknown>(`/api/measurements?${params}`).then((payload) => {
      if (!isMeasurementList(payload)) {
        throw new APIRequestError(
          "The API returned an incompatible measurements response. Restart the backend to load the current contract.",
          502,
        );
      }
      return payload;
    });
  },
  report(requestBody: ReportRequest): Promise<ReportResponse> {
    return request<ReportResponse>("/api/reports", {
      method: "POST",
      body: JSON.stringify(requestBody),
    });
  },
};
