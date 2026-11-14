import math
import uuid
from typing import Protocol

from app.errors import APIError
from app.models import (
    ChatRequest,
    ChatResponse,
    ComparisonRequest,
    ComparisonResponse,
    Investigation,
    InvestigationPage,
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
    def __init__(self, store: SQLiteStore):
        self.store = store

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
        matches = [_score_investigation(scenario, item) for item in investigations]
        matches.sort(key=lambda result: result.relevance_score, reverse=True)
        gaps = []
        if not investigations:
            gaps.append("No investigations are available in indexed sources.")
        if not self.store.measurements():
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
    scenario: ScenarioRequest, investigation: Investigation
) -> ScenarioMatch:
    objective_areas = {
        "material_flammability": {"prevention"},
        "fire_detection": {"detection"},
        "fire_suppression": {"suppression"},
        "combustion_fundamentals": {"fundamentals"},
        "general": set(),
    }
    objective_score = float(
        investigation.research_area in objective_areas[scenario.objective]
    )
    parameter_scores: list[float] = []
    reasons: list[str] = []
    if scenario.oxygen_pct is not None and investigation.conditions.oxygen_pct is not None:
        parameter_scores.append(
            max(
                0.0,
                1.0
                - abs(
                    scenario.oxygen_pct - investigation.conditions.oxygen_pct
                )
                / 100,
            )
        )
        reasons.append("Oxygen conditions can be compared with indexed metadata.")
    if (
        scenario.pressure.value is not None
        and investigation.conditions.pressure.value is not None
    ):
        scenario_psi = _pressure_psi(
            scenario.pressure.value, scenario.pressure.unit or ""
        )
        record_psi = _pressure_psi(
            investigation.conditions.pressure.value,
            investigation.conditions.pressure.unit or "",
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
            reasons.append("Pressure conditions can be compared with indexed metadata.")
    parameter_score = (
        sum(parameter_scores) / len(parameter_scores) if parameter_scores else 0
    )
    context_score = 0.0
    if scenario.material_or_fuel:
        requested_material = scenario.material_or_fuel.strip().casefold()
        indexed_materials = {
            material.strip().casefold()
            for material in investigation.materials_or_fuels
        }
        if requested_material in indexed_materials:
            context_score = 1.0
            reasons.append("The requested material or fuel matches indexed metadata.")
    measurement_score = float(
        investigation.data_availability == "numeric_dataset"
        and bool(investigation.variables_measured)
    )
    if objective_score:
        reasons.append("Research area matches the requested objective.")
    if measurement_score:
        reasons.append("A numeric dataset and measured variables are indexed.")
    limitations = []
    if not parameter_scores:
        limitations.append("No comparable oxygen or pressure values are indexed.")
    if scenario.material_or_fuel and context_score == 0:
        limitations.append("The requested material or fuel is not matched in indexed metadata.")
    if not investigation.sources:
        limitations.append("No citations are linked to this investigation record.")
    if investigation.environment == "microgravity":
        limitations.append("Microgravity results do not prove partial-gravity performance.")
    components = [objective_score, parameter_score, measurement_score, context_score]
    relevance = round(100 * sum(components) / len(components), 2)
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
            parameter_similarity=round(parameter_score, 4),
            measurement_usefulness=measurement_score,
            context_hardware=context_score,
        ),
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
