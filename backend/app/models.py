from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


ResearchArea = Literal[
    "prevention", "detection", "suppression", "fundamentals", "related", "other"
]
Environment = Literal["microgravity", "normal_gravity", "other", "unknown"]
DataAvailability = Literal["metadata_only", "documents", "numeric_dataset", "unknown"]
ScenarioEnvironment = Literal[
    "lunar_habitat", "mars_habitat", "spacecraft", "spacesuit", "custom"
]
ScenarioObjective = Literal[
    "material_flammability",
    "fire_detection",
    "fire_suppression",
    "combustion_fundamentals",
    "general",
]
ErrorCode = Literal[
    "VALIDATION_ERROR", "NOT_FOUND", "NO_EVIDENCE", "INTERNAL_ERROR"
]


class APIModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Pressure(APIModel):
    value: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    unit: str | None = Field(default=None, max_length=16)

    @field_validator("unit")
    @classmethod
    def pressure_unit_required_for_value(cls, unit: str | None, info):
        if info.data.get("value") is not None and not unit:
            raise ValueError("A pressure unit is required when a value is provided.")
        return unit


class InvestigationConditions(APIModel):
    oxygen_pct: float | None = Field(default=None, ge=0, le=100, allow_inf_nan=False)
    pressure: Pressure = Field(default_factory=Pressure)
    other: list[str] = Field(default_factory=list)


class Source(APIModel):
    source_id: str = Field(min_length=1)
    document_title: str = Field(min_length=1, max_length=500)
    source_url: HttpUrl
    page_number: int | None = Field(default=None, ge=1)
    section: str | None = None
    source_type: Literal["NASA_PSI", "NASA_REPORT", "NASA_DATASET", "OTHER"]

    @field_validator("source_url")
    @classmethod
    def require_secure_source_url(cls, url: HttpUrl) -> HttpUrl:
        if url.scheme != "https":
            raise ValueError("Source URLs must use HTTPS.")
        return url


class SourceCitation(APIModel):
    source_id: str
    document_title: str
    source_url: HttpUrl
    page_number: int | None = None
    section: str | None = None
    quote_or_supported_excerpt: str | None = None

    @field_validator("source_url")
    @classmethod
    def require_secure_source_url(cls, url: HttpUrl) -> HttpUrl:
        if url.scheme != "https":
            raise ValueError("Source URLs must use HTTPS.")
        return url


class Investigation(APIModel):
    investigation_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    acronym: str | None = None
    research_area: ResearchArea
    objectives: list[str] = Field(default_factory=list)
    materials_or_fuels: list[str] = Field(default_factory=list)
    environment: Environment = "unknown"
    conditions: InvestigationConditions = Field(default_factory=InvestigationConditions)
    hardware: list[str] = Field(default_factory=list)
    sensors: list[str] = Field(default_factory=list)
    variables_measured: list[str] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)
    data_availability: DataAvailability = "unknown"
    sources: list[Source] = Field(default_factory=list)
    last_verified_at: datetime | None = None


class InvestigationPage(APIModel):
    items: list[Investigation]
    page: int
    page_size: int
    total: int


class ScenarioRequest(APIModel):
    environment: ScenarioEnvironment
    oxygen_pct: float | None = Field(default=None, ge=0, le=100, allow_inf_nan=False)
    pressure: Pressure = Field(default_factory=Pressure)
    material_or_fuel: str | None = Field(default=None, max_length=200)
    objective: ScenarioObjective


class ScoreBreakdown(APIModel):
    objective_match: float | None = Field(default=None, ge=0, le=1)
    parameter_similarity: float | None = Field(default=None, ge=0, le=1)
    measurement_usefulness: float | None = Field(default=None, ge=0, le=1)
    context_hardware: float | None = Field(default=None, ge=0, le=1)


class ScenarioMatch(APIModel):
    investigation_id: str
    title: str
    relevance_score: float = Field(ge=0, le=100)
    score_breakdown: ScoreBreakdown
    evidence_completeness: float = Field(ge=0, le=1)
    match_reasons: list[str]
    limitations: list[str]
    citations: list[SourceCitation]


class ScenarioAnalysisResponse(APIModel):
    scenario_id: str
    score_type: Literal["research_relevance_not_fire_risk"] = (
        "research_relevance_not_fire_risk"
    )
    scenario: ScenarioRequest
    matches: list[ScenarioMatch]
    research_gaps: list[str]
    limitations: list[str]


class ComparisonRequest(APIModel):
    investigation_ids: list[str] = Field(min_length=1, max_length=5)

    @field_validator("investigation_ids")
    @classmethod
    def unique_investigations(cls, ids: list[str]) -> list[str]:
        if len(set(ids)) != len(ids):
            raise ValueError("Investigation IDs must be unique.")
        return ids


class ComparisonResponse(APIModel):
    investigations: list[Investigation]
    limitations: list[str]


class ChatRequest(APIModel):
    question: str = Field(min_length=1, max_length=4000)
    investigation_ids: list[str] = Field(default_factory=list, max_length=5)


class ChatResponse(APIModel):
    answer: str
    citations: list[SourceCitation]
    limitations: list[str]


class Measurement(APIModel):
    measurement_id: str = Field(min_length=1)
    investigation_id: str = Field(min_length=1)
    variable: str = Field(min_length=1)
    value: float = Field(allow_inf_nan=False)
    unit: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    conditions: dict[str, str | float | None] = Field(default_factory=dict)


class MeasurementList(APIModel):
    items: list[Measurement]


class ReportRequest(APIModel):
    investigation_ids: list[str] = Field(min_length=1, max_length=10)


class ReportResponse(APIModel):
    report_id: str
    title: str
    brief: str
    citations: list[SourceCitation]
    limitations: list[str]
    research_gaps: list[str]


class HealthResponse(APIModel):
    status: Literal["ok"] = "ok"


class ErrorDetail(APIModel):
    field: str
    message: str


class ErrorBody(APIModel):
    code: ErrorCode
    message: str
    details: list[ErrorDetail] = Field(default_factory=list)


class ErrorResponse(APIModel):
    error: ErrorBody


# Backwards-compatible names for callers that imported the original model names.
Citation = SourceCitation
ScenarioAnalysis = ScenarioAnalysisResponse
CompareRequest = ComparisonRequest
CompareResponse = ComparisonResponse
