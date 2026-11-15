from datetime import datetime
from typing import Literal

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)


ResearchArea = Literal[
    "prevention", "detection", "suppression", "fundamentals", "related", "other"
]
Environment = Literal["microgravity", "normal_gravity", "other", "unknown"]
DataAvailability = Literal["metadata_only", "documents", "numeric_dataset", "unknown"]
SourceVerificationStatus = Literal["verified", "unverified", "unavailable"]
MeasurementExtractionMethod = Literal[
    "pdf_text", "pdf_table_text", "metadata_text", "manual"
]
MeasurementCandidateClassification = Literal[
    "experimental_observation",
    "derived_quantity",
    "initial_condition",
    "approximate_value",
    "setup_parameter",
    "boundary_condition",
    "simulation_input",
    "hypothetical",
    "incidental",
    "reported_summary",
    "ambiguous",
    "other",
]
MeasurementReviewStatus = Literal[
    "pending_review", "needs_more_evidence", "approved", "rejected"
]
MeasurementReviewDecision = Literal["approve", "reject", "needs_more_evidence"]
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
    local_file_path: str | None = None
    downloaded_at: datetime | None = None
    sha256: str | None = Field(
        default=None, min_length=64, max_length=64, pattern=r"^[0-9a-fA-F]{64}$"
    )
    file_size_bytes: int | None = Field(default=None, ge=0)
    mime_type: str | None = None
    last_verified_at: datetime | None = None
    verification_status: SourceVerificationStatus = "unverified"

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
    local_file_path: str | None = None
    downloaded_at: datetime | None = None
    sha256: str | None = None
    file_size_bytes: int | None = Field(default=None, ge=0)
    mime_type: str | None = None
    last_verified_at: datetime | None = None
    verification_status: SourceVerificationStatus = "unverified"

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


ComparisonFieldName = Literal[
    "objectives",
    "research_area",
    "environment",
    "conditions",
    "materials_or_fuels",
    "hardware",
    "sensors",
    "variables_measured",
    "findings",
    "data_availability",
]
ComparisonStatus = Literal["same", "different", "not_comparable"]


class ComparisonRequest(APIModel):
    investigation_ids: list[str] = Field(min_length=2, max_length=5)

    @field_validator("investigation_ids")
    @classmethod
    def unique_investigations(cls, ids: list[str]) -> list[str]:
        if any(not item.strip() for item in ids):
            raise ValueError("Investigation IDs must be non-empty.")
        if len(set(ids)) != len(ids):
            raise ValueError("Investigation IDs must be unique.")
        return ids


class ComparisonInvestigation(APIModel):
    investigation_id: str
    title: str
    acronym: str | None
    research_area: ResearchArea
    environment: Environment
    data_availability: DataAvailability
    citations: list[SourceCitation]


class ComparisonValue(APIModel):
    investigation_id: str
    value: str | list[str] | InvestigationConditions | None


class FieldComparison(APIModel):
    field: ComparisonFieldName
    status: ComparisonStatus
    values: list[ComparisonValue]
    explanation: str | None = None


class ComparisonResponse(APIModel):
    investigations: list[ComparisonInvestigation]
    field_comparisons: list[FieldComparison]
    differences_summary: list[str]
    limitations: list[str]


class ChatRequest(APIModel):
    question: str = Field(min_length=1, max_length=4000)
    scenario_id: str | None = Field(default=None, min_length=1, max_length=100)
    investigation_ids: list[str] = Field(default_factory=list, max_length=5)
    research_area: ResearchArea | None = None

    @field_validator("investigation_ids")
    @classmethod
    def unique_investigations(cls, ids: list[str]) -> list[str]:
        if len(set(ids)) != len(ids):
            raise ValueError("Investigation IDs must be unique.")
        return ids


class EvidenceExcerpt(APIModel):
    excerpt_id: str = Field(min_length=1)
    investigation_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    excerpt: str = Field(min_length=1, max_length=6000)
    page_number: int | None = Field(default=None, ge=1)
    section: str | None = None


class ChatEvidence(APIModel):
    source_id: str
    investigation_id: str
    document_title: str
    source_url: HttpUrl
    page_number: int | None = None
    section: str | None = None
    excerpt: str


class ChatResponse(APIModel):
    answer: str
    evidence: list[ChatEvidence]
    citations: list[SourceCitation]
    limitations: list[str]
    answer_status: Literal["grounded", "insufficient_evidence"]

    @model_validator(mode="after")
    def citations_must_reference_retrieved_evidence(self):
        evidence_keys = {
            (
                item.source_id,
                item.document_title,
                str(item.source_url),
                item.page_number,
                item.section,
                item.excerpt,
            )
            for item in self.evidence
        }
        for citation in self.citations:
            citation_key = (
                citation.source_id,
                citation.document_title,
                str(citation.source_url),
                citation.page_number,
                citation.section,
                citation.quote_or_supported_excerpt,
            )
            if citation_key not in evidence_keys:
                raise ValueError("Every citation must map to a retrieved evidence excerpt.")
        if self.answer_status == "grounded" and (not self.evidence or not self.citations):
            raise ValueError("Grounded answers require retrieved evidence and citations.")
        return self


class Measurement(APIModel):
    measurement_id: str = Field(min_length=1)
    investigation_id: str = Field(min_length=1)
    variable: str = Field(min_length=1)
    value: float = Field(allow_inf_nan=False)
    reported_value: str | None = None
    unit: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    observation_context: dict[str, str | float | None] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("observation_context", "conditions"),
    )
    page_number: int | None = Field(default=None, ge=1)
    section: str | None = None
    table_reference: str | None = None
    supporting_excerpt: str | None = None
    extraction_method: MeasurementExtractionMethod = "manual"
    confidence: float | None = Field(default=None, ge=0, le=1)
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    review_notes: str | None = None


class MeasurementObservation(Measurement):
    document_title: str
    source_url: HttpUrl


class MeasurementList(APIModel):
    data: list[MeasurementObservation]
    data_availability: DataAvailability
    message: str


class MeasurementCandidate(APIModel):
    candidate_id: str = Field(min_length=1)
    investigation_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    document_title: str = Field(min_length=1)
    source_url: HttpUrl
    source_sha256: str = Field(pattern=r"^[0-9a-fA-F]{64}$")
    variable: str | None = None
    reported_value: str = Field(min_length=1)
    value: float = Field(allow_inf_nan=False)
    unit: str = Field(min_length=1)
    observation_context: dict[str, str | float | None] = Field(default_factory=dict)
    page_number: int | None = Field(default=None, ge=1)
    section: str | None = None
    table_reference: str | None = None
    supporting_excerpt: str = Field(min_length=1)
    extraction_method: Literal["pdf_text", "pdf_table_text", "metadata_text"]
    confidence: float = Field(ge=0, le=1)
    classification: MeasurementCandidateClassification
    review_status: MeasurementReviewStatus = "pending_review"
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    review_notes: str | None = None
    review_flags: list[str] = Field(default_factory=list)
    measurement_id: str | None = None

    @field_validator("source_url")
    @classmethod
    def require_secure_candidate_source_url(cls, url: HttpUrl) -> HttpUrl:
        if url.scheme != "https":
            raise ValueError("Source URLs must use HTTPS.")
        return url

    @model_validator(mode="after")
    def validate_approval_provenance(self) -> "MeasurementCandidate":
        if self.review_status == "approved":
            if not all((self.reviewed_at, self.measurement_id)):
                raise ValueError("Approved candidates require review and measurement provenance.")
            if self.reviewed_by is None and not (
                self.review_notes
                and "reviewer could not be established" in self.review_notes.casefold()
            ):
                raise ValueError(
                    "Approved candidates without a reviewer require an explicit attribution audit note."
                )
        return self


class AdditionalMeasurementEvidence(APIModel):
    source_id: str = Field(min_length=1)
    document_title: str = Field(min_length=1)
    source_url: HttpUrl
    source_sha256: str = Field(pattern=r"^[0-9a-fA-F]{64}$")
    page_number: int | None = Field(default=None, ge=1)
    section: str | None = None
    supporting_excerpt: str = Field(min_length=1)


class MeasurementReviewEvent(APIModel):
    review_event_id: str = Field(min_length=1)
    candidate_id: str = Field(min_length=1)
    reviewer: str = Field(min_length=1)
    decision: MeasurementReviewDecision
    previous_status: MeasurementReviewStatus
    new_status: MeasurementReviewStatus
    previous_classification: MeasurementCandidateClassification
    new_classification: MeasurementCandidateClassification
    classification_reason: str | None = None
    reviewed_at: datetime
    rationale: str = Field(min_length=1)
    evidence_notes: str = Field(min_length=1)
    source_review_confirmed: bool = False
    measurement_definition_confirmed: bool = False
    priority_finding: str | None = None
    audit_classification: str | None = None
    audit_quality_flags: list[str] = Field(default_factory=list)
    figure_reference: str | None = None
    figure_caption_excerpt: str | None = None
    priority_resolution_confirmed: bool = False
    conflict_resolution_confirmed: bool = False
    zero_value_resolution_confirmed: bool = False
    additional_evidence_review_confirmed: bool = False
    additional_supporting_evidence: AdditionalMeasurementEvidence | None = None
    source_id: str = Field(min_length=1)
    source_url: HttpUrl
    document_title: str = Field(min_length=1)
    source_sha256: str = Field(pattern=r"^[0-9a-fA-F]{64}$")
    page_number: int | None = Field(default=None, ge=1)
    section: str | None = None
    table_reference: str | None = None
    row_reference: str | None = None
    supporting_excerpt: str = Field(min_length=1)


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
