import math
import uuid
from dataclasses import dataclass
from typing import Protocol

from app.errors import APIError
from app.models import (
    ChatRequest,
    ChatResponse,
    ComparisonRequest,
    ComparisonResponse,
    Investigation,
    InvestigationPage,
    Measurement,
    MeasurementList,
    ReportRequest,
    ReportResponse,
    ScenarioAnalysisResponse,
    ScenarioMatch,
    ScenarioRequest,
    ScoreBreakdown,
    SourceCitation,
)
from app.store import SQLiteStore


@dataclass(frozen=True)
class RelevanceWeights:
    objective_match: float = 0.40
    parameter_similarity: float = 0.30
    measurement_usefulness: float = 0.20
    context_hardware: float = 0.10

    def __post_init__(self) -> None:
        values = (
            self.objective_match,
            self.parameter_similarity,
            self.measurement_usefulness,
            self.context_hardware,
        )
        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or value < 0
            for value in values
        ):
            raise ValueError("Relevance weights must be finite and non-negative.")
        if not math.isclose(sum(values), 1.0, abs_tol=1e-9):
            raise ValueError("Relevance weights must sum to 1.")


DEFAULT_RELEVANCE_WEIGHTS = RelevanceWeights()


class ResearchService(Protocol):
    def list_investigations(
        self,
        q: str | None,
        research_area: str | None,
        environment: str | None,
        data_availability: str | None,
        page: int,
        page_size: int,
    ) -> InvestigationPage: ...

    def get_investigation(self, investigation_id: str) -> Investigation | None: ...

    def analyze_scenario(self, scenario: ScenarioRequest) -> ScenarioAnalysisResponse: ...

    def compare(self, request: ComparisonRequest) -> ComparisonResponse: ...

    def chat(self, request: ChatRequest) -> ChatResponse: ...

    def measurements(
        self, investigation_id: str | None, variable: str | None
    ) -> MeasurementList: ...

    def create_report(self, request: ReportRequest) -> ReportResponse: ...


class SQLiteResearchService:
    def __init__(
        self,
        store: SQLiteStore,
        scoring_weights: RelevanceWeights = DEFAULT_RELEVANCE_WEIGHTS,
    ):
        self.store = store
        self.scoring_weights = scoring_weights

    def list_investigations(
        self,
        q: str | None,
        research_area: str | None,
        environment: str | None,
        data_availability: str | None,
        page: int,
        page_size: int,
    ) -> InvestigationPage:
        items, total = self.store.list_investigations(
            q, research_area, environment, data_availability, page, page_size
        )
        return InvestigationPage(items=items, page=page, page_size=page_size, total=total)

    def get_investigation(self, investigation_id: str) -> Investigation | None:
        return self.store.get_investigation(investigation_id)

    def analyze_scenario(self, scenario: ScenarioRequest) -> ScenarioAnalysisResponse:
        investigations, _ = self.store.list_investigations(page_size=1_000_000)
        measurements_by_investigation: dict[str, list[Measurement]] = {
            item.investigation_id: [] for item in investigations
        }
        sources_by_investigation = {
            item.investigation_id: {source.source_id for source in item.sources}
            for item in investigations
        }
        for measurement in self.store.measurements():
            if (
                measurement.investigation_id in measurements_by_investigation
                and measurement.source_id
                in sources_by_investigation[measurement.investigation_id]
            ):
                measurements_by_investigation[
                    measurement.investigation_id
                ].append(measurement)
        matches = [
            _score_investigation(
                scenario,
                item,
                self.scoring_weights,
                measurements_by_investigation[item.investigation_id],
            )
            for item in investigations
        ]
        matches.sort(
            key=lambda result: (-result.relevance_score, result.investigation_id)
        )
        gaps = []
        if not investigations:
            gaps.append("No investigations are available in indexed sources.")
        if not any(measurements_by_investigation.values()):
            gaps.append("Verified numeric measurements are not available in indexed sources.")
        return ScenarioAnalysisResponse(
            scenario_id=str(uuid.uuid4()),
            scenario=scenario,
            matches=matches,
            research_gaps=gaps,
            limitations=[
                "Relevance ranks research records; it is not a fire-risk score or probability.",
                "User-entered scenario conditions are hypothetical and are not NASA measurements.",
                "Microgravity evidence does not establish performance in lunar or Martian partial gravity.",
            ],
        )

    def compare(self, request: ComparisonRequest) -> ComparisonResponse:
        items = self.store.get_investigations(request.investigation_ids)
        if len(items) != len(request.investigation_ids):
            raise APIError(404, "NOT_FOUND", "One or more investigations were not found.")
        return ComparisonResponse(
            investigations=items,
            limitations=[
                "Only indexed source metadata is shown; missing conditions or findings are not inferred."
            ],
        )

    def chat(self, request: ChatRequest) -> ChatResponse:
        if request.investigation_ids:
            items = self.store.get_investigations(request.investigation_ids)
            if len(items) != len(request.investigation_ids):
                raise APIError(404, "NOT_FOUND", "One or more investigations were not found.")
        raise APIError(
            422,
            "NO_EVIDENCE",
            "Not available in indexed sources: no verified document excerpts are indexed to answer this question.",
        )

    def measurements(
        self, investigation_id: str | None, variable: str | None
    ) -> MeasurementList:
        return MeasurementList(
            items=self.store.measurements(investigation_id, variable)
        )

    def create_report(self, request: ReportRequest) -> ReportResponse:
        items = self.store.get_investigations(request.investigation_ids)
        if len(items) != len(request.investigation_ids):
            raise APIError(404, "NOT_FOUND", "One or more investigations were not found.")
        citations = [
            SourceCitation(
                source_id=source.source_id,
                document_title=source.document_title,
                source_url=source.source_url,
                page_number=source.page_number,
                section=source.section,
            )
            for item in items
            for source in item.sources
        ]
        facts = [
            f"- {item.title} ({item.research_area}); data availability: "
            f"{item.data_availability}."
            for item in items
        ]
        gaps = []
        if not citations:
            gaps.append("No source records are linked to the selected investigations.")
        if any(not item.findings for item in items):
            gaps.append("Findings are not available in indexed sources for every selection.")
        if not self.store.measurements_for_investigations(request.investigation_ids):
            gaps.append("Verified numeric measurements are not available for these investigations.")
        return ReportResponse(
            report_id=str(uuid.uuid4()),
            title="FLARE AI evidence brief",
            brief=(
                "Indexed investigation metadata (not a fire-risk assessment):\n"
                + "\n".join(facts)
            ),
            citations=citations,
            limitations=[
                "This brief summarizes indexed metadata only; it does not establish fire risk or operational safety.",
                "Citations identify source documents; no direct excerpts are indexed in this prototype.",
                "Microgravity results must not be treated as proven performance in partial gravity.",
            ],
            research_gaps=gaps,
        )


def _score_investigation(
    scenario: ScenarioRequest,
    investigation: Investigation,
    weights: RelevanceWeights = DEFAULT_RELEVANCE_WEIGHTS,
    verified_measurements: list[Measurement] | None = None,
) -> ScenarioMatch:
    objective_areas = {
        "material_flammability": {"prevention"},
        "fire_detection": {"detection"},
        "fire_suppression": {"suppression"},
        "combustion_fundamentals": {"fundamentals"},
        "general": set(),
    }
    objective_targets = objective_areas[scenario.objective]
    objective_score = (
        float(investigation.research_area in objective_targets)
        if objective_targets
        else None
    )
    parameter_scores: list[float] = []
    reasons: list[str] = []
    limitations: list[str] = []
    requested_parameter_count = int(scenario.oxygen_pct is not None) + int(
        scenario.pressure.value is not None
    )
    record_oxygen = investigation.conditions.oxygen_pct
    if scenario.oxygen_pct is not None and record_oxygen is not None:
        parameter_scores.append(
            max(
                0.0,
                1.0 - abs(scenario.oxygen_pct - record_oxygen) / 100,
            )
        )
        reasons.append("Oxygen percentages are comparable in indexed metadata.")
    elif scenario.oxygen_pct is not None:
        limitations.append(
            "Oxygen percentage is not reported in indexed sources; parameter evidence is incomplete."
        )

    record_pressure = investigation.conditions.pressure
    if scenario.pressure.value is not None and record_pressure.value is not None:
        scenario_psi = _pressure_psi(
            scenario.pressure.value, scenario.pressure.unit or ""
        )
        record_psi = _pressure_psi(
            record_pressure.value, record_pressure.unit or ""
        )
        if scenario_psi is not None and record_psi is not None:
            parameter_scores.append(
                max(
                    0.0,
                    1.0
                    - abs(scenario_psi - record_psi)
                    / max(scenario_psi, record_psi),
                )
            )
            reasons.append("Pressure values are comparable after unit conversion.")
        else:
            limitations.append(
                "Pressure units are not comparable; parameter evidence is incomplete and numeric similarity was not calculated."
            )
    elif scenario.pressure.value is not None:
        limitations.append(
            "Pressure is not reported in indexed sources; parameter evidence is incomplete."
        )

    parameter_score = (
        sum(parameter_scores) / len(parameter_scores) if parameter_scores else None
    )
    context_score = 0.0
    context_available = False
    if scenario.material_or_fuel:
        requested_material = scenario.material_or_fuel.strip().casefold()
        indexed_materials = {
            material.strip().casefold()
            for material in investigation.materials_or_fuels
        }
        if investigation.materials_or_fuels:
            context_available = True
            if requested_material in indexed_materials:
                context_score = 1.0
                reasons.append(
                    "The requested material or fuel matches indexed metadata."
                )
            else:
                reasons.append(
                    "The requested material or fuel does not match the indexed materials."
                )
        else:
            context_score = None
            limitations.append(
                "Materials or fuels are not reported in indexed sources."
            )
    else:
        context_score = None

    source_ids = {source.source_id for source in investigation.sources}
    has_verified_measurements = any(
        measurement.investigation_id == investigation.investigation_id
        and measurement.source_id in source_ids
        for measurement in verified_measurements or []
    )
    measurement_score = 1.0 if has_verified_measurements else None
    if objective_score == 1:
        reasons.append("Research area matches the requested objective.")
    elif objective_score == 0:
        reasons.append("Research area does not align with the requested objective.")
    elif scenario.objective == "general":
        limitations.append(
            "The general objective does not target a single research area; objective evidence is not specific."
        )
    if has_verified_measurements:
        reasons.append(
            "Source-linked numeric measurement observations are indexed."
        )
    elif investigation.data_availability == "numeric_dataset":
        limitations.append(
            "A numeric dataset is declared, but no source-linked measurement observations are available in the indexed measurement store."
        )
    else:
        limitations.append(
            "Verified source-linked measurement observations are not available in the indexed measurement store."
        )
    if requested_parameter_count and not parameter_scores:
        reasons.append(
            "Parameter similarity is unavailable; no comparable requested values were found."
        )
    if not investigation.sources:
        limitations.append("No citations are linked to this investigation record.")
    if investigation.environment == "microgravity":
        limitations.append("Microgravity results do not prove partial-gravity performance.")

    comparable_parameter_fraction = (
        len(parameter_scores) / requested_parameter_count
        if requested_parameter_count
        else 0.0
    )
    weighted_components = (
        (objective_score, weights.objective_match),
        (
            parameter_score,
            weights.parameter_similarity * comparable_parameter_fraction,
        ),
        (
            measurement_score,
            weights.measurement_usefulness if has_verified_measurements else 0.0,
        ),
        (
            context_score,
            weights.context_hardware if context_available else 0.0,
        ),
    )
    available_weight = sum(
        component_weight
        for component, component_weight in weighted_components
        if component is not None
    )
    total_weight = sum(
        (
            weights.objective_match,
            weights.parameter_similarity,
            weights.measurement_usefulness,
            weights.context_hardware,
        )
    )
    weighted_score = sum(
        component * component_weight
        for component, component_weight in weighted_components
        if component is not None
    )
    relevance = (
        round(100 * weighted_score / available_weight, 2)
        if available_weight
        else 0.0
    )
    evidence_completeness = (
        min(1.0, available_weight / total_weight) if total_weight else 0.0
    )
    if evidence_completeness < 1:
        limitations.append(
            f"Evidence completeness is {evidence_completeness:.0%}; the relevance score is normalized over available evidence only."
        )
    citations = [
        SourceCitation(
            source_id=source.source_id,
            document_title=source.document_title,
            source_url=source.source_url,
            page_number=source.page_number,
            section=source.section,
        )
        for source in investigation.sources
    ]
    return ScenarioMatch(
        investigation_id=investigation.investigation_id,
        title=investigation.title,
        relevance_score=relevance,
        score_breakdown=ScoreBreakdown(
            objective_match=objective_score,
            parameter_similarity=(
                round(parameter_score, 4) if parameter_score is not None else None
            ),
            measurement_usefulness=measurement_score,
            context_hardware=context_score,
        ),
        evidence_completeness=round(evidence_completeness, 4),
        match_reasons=reasons or ["No positive evidence match was found."],
        limitations=limitations,
        citations=citations,
    )


def _pressure_psi(value: float, unit: str) -> float | None:
    conversion = {
        "psi": 1.0,
        "kpa": 0.1450377377,
        "bar": 14.50377377,
        "atm": 14.6959488,
    }
    factor = conversion.get(unit.lower())
    return value * factor if factor is not None and math.isfinite(value) else None
