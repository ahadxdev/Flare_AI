import math
import logging
import uuid
from dataclasses import dataclass
from typing import Protocol

from app.chat_provider import (
    ChatCompletionProvider,
    ProviderAnswer,
    ProviderError,
)
from app.errors import APIError
from app.models import (
    ChatEvidence,
    ChatRequest,
    ChatResponse,
    ComparisonFieldName,
    ComparisonInvestigation,
    ComparisonRequest,
    ComparisonResponse,
    ComparisonStatus,
    ComparisonValue,
    FieldComparison,
    Investigation,
    InvestigationConditions,
    InvestigationPage,
    Measurement,
    MeasurementList,
    MeasurementObservation,
    ReportRequest,
    ReportResponse,
    ScenarioAnalysisResponse,
    ScenarioMatch,
    ScenarioRequest,
    ScoreBreakdown,
    SourceCitation,
)
from app.store import EvidenceHit, SQLiteStore


logger = logging.getLogger("flare.services")


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
        chat_provider: ChatCompletionProvider | None = None,
    ):
        self.store = store
        self.scoring_weights = scoring_weights
        self.chat_provider = chat_provider

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
        analysis = ScenarioAnalysisResponse(
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
        self.store.save_scenario_analysis(analysis)
        return analysis

    def compare(self, request: ComparisonRequest) -> ComparisonResponse:
        items = self.store.get_investigations(request.investigation_ids)
        if len(items) != len(request.investigation_ids):
            raise APIError(404, "NOT_FOUND", "One or more investigations were not found.")
        field_names: tuple[ComparisonFieldName, ...] = (
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
        )
        field_comparisons = []
        for field in field_names:
            values = [
                ComparisonValue(
                    investigation_id=item.investigation_id,
                    value=getattr(item, field),
                )
                for item in items
            ]
            status, explanation = _compare_field_values(field, values)
            field_comparisons.append(
                FieldComparison(
                    field=field,
                    status=status,
                    values=values,
                    explanation=explanation,
                )
            )

        different_fields = [
            item.field.replace("_", " ")
            for item in field_comparisons
            if item.status == "different"
        ]
        incomparable_fields = [
            (
                f"{item.field.replace('_', ' ')}"
                + (f" ({item.explanation})" if item.explanation else "")
            )
            for item in field_comparisons
            if item.status == "not_comparable"
        ]
        differences_summary = []
        if different_fields:
            differences_summary.append(
                f"Different reported fields: {', '.join(different_fields)}."
            )
        if incomparable_fields:
            differences_summary.append(
                "Not comparable or missing: " + "; ".join(incomparable_fields) + "."
            )
        if not differences_summary:
            differences_summary.append(
                "No differences were found among the complete reported fields."
            )

        return ComparisonResponse(
            investigations=[
                ComparisonInvestigation(
                    investigation_id=item.investigation_id,
                    title=item.title,
                    acronym=item.acronym,
                    research_area=item.research_area,
                    environment=item.environment,
                    data_availability=item.data_availability,
                    citations=[
                        SourceCitation.model_validate(
                            source.model_dump(mode="json", exclude={"source_type"})
                        )
                        for source in item.sources
                    ],
                )
                for item in items
            ],
            field_comparisons=field_comparisons,
            differences_summary=differences_summary,
            limitations=[
                "Values are compared as reported; numeric unit conversions are not performed.",
                "Fields missing or incomplete for any selected record are marked not_comparable.",
            ],
        )

    def chat(self, request: ChatRequest) -> ChatResponse:
        scenario_analysis = None
        scenario = None
        allowed_ids: list[str] | None = None
        if request.investigation_ids:
            items = self.store.get_investigations(request.investigation_ids)
            if len(items) != len(request.investigation_ids):
                raise APIError(404, "NOT_FOUND", "One or more investigations were not found.")
            allowed_ids = list(request.investigation_ids)
        if request.scenario_id is not None:
            scenario_analysis = self.store.get_scenario_analysis(request.scenario_id)
            if scenario_analysis is None:
                raise APIError(404, "NOT_FOUND", "The requested scenario was not found.")
            scenario = scenario_analysis.scenario
            scenario_ids = [match.investigation_id for match in scenario_analysis.matches]
            allowed_ids = (
                [item_id for item_id in allowed_ids if item_id in scenario_ids]
                if allowed_ids is not None
                else scenario_ids[:100]
            )

        hits = self.store.search_evidence(
            request.question,
            investigation_ids=allowed_ids,
            research_area=request.research_area,
        )
        if not hits:
            unavailable_sources = any(
                source.verification_status == "unavailable"
                for investigation in self.store.get_investigations(
                    allowed_ids or []
                )
                for source in investigation.sources
            )
            return self._insufficient_evidence(
                scenario is not None,
                unavailable_sources,
            )

        provider_failure: str | None = None
        if self.chat_provider is None:
            answer = self._evidence_only_answer(scenario is not None)
            provider_failure = (
                "The LLM provider is not configured; only retrieved excerpts are presented."
            )
        else:
            try:
                answer = self.chat_provider.answer(request.question, hits, scenario)
            except (ProviderError, TimeoutError, OSError):
                logger.warning(
                    "Chat provider failed; returning evidence-only fallback",
                    extra={"evidence_count": len(hits)},
                )
                answer = self._evidence_only_answer(scenario is not None)
                provider_failure = (
                    "The LLM provider timed out or failed; only retrieved excerpts are presented."
                )
        return self._grounded_response(
            answer,
            hits,
            scenario is not None,
            provider_failure=provider_failure,
        )

    def _insufficient_evidence(
        self, has_scenario: bool, has_unavailable_sources: bool = False
    ) -> ChatResponse:
        scenario_relevance = (
            "The scenario is a user-entered hypothetical; no indexed evidence was found "
            "to assess its relevance."
            if has_scenario
            else "No scenario context was supplied."
        )
        answer = (
            "Short answer: Not available in indexed sources.\n\n"
            "Evidence: No relevant verified excerpts are indexed for this question.\n\n"
            f"Relevance to the scenario: {scenario_relevance}\n\n"
            "Limitations / research gaps: No answer is inferred without source evidence. "
            "Microgravity evidence, when available, does not establish lunar or Martian "
            "partial-gravity performance.\n\n"
            "Sources: None retrieved."
        )
        limitations = [
            "Not available in indexed sources: no relevant verified excerpts were retrieved.",
            "Specific investigation claims cannot be supported without indexed evidence.",
            "Microgravity evidence does not establish lunar or Martian partial-gravity performance.",
        ]
        if has_unavailable_sources:
            limitations.append(
                "One or more linked NASA source files are unavailable locally."
            )
        return ChatResponse(
            answer=answer,
            evidence=[],
            citations=[],
            limitations=limitations,
            answer_status="insufficient_evidence",
        )

    def _evidence_only_answer(self, has_scenario: bool) -> ProviderAnswer:
        relevance = (
            "These excerpts provide research context only; they do not prove lunar or "
            "Martian partial-gravity performance."
            if has_scenario
            else "No scenario context was supplied; relevance is not assessed."
        )
        return ProviderAnswer(
            answer_status="grounded",
            short_answer=(
                "The retrieved excerpts are the available source evidence; no claim "
                "beyond their text is inferred."
            ),
            scenario_relevance=relevance,
            limitations=(
                "This evidence-only response does not synthesize beyond the quoted excerpts. "
                "Generated interpretation is not a NASA-reported fact."
            ),
        )

    def _grounded_response(
        self,
        answer: ProviderAnswer,
        hits: list[EvidenceHit],
        has_scenario: bool,
        provider_failure: str | None = None,
    ) -> ChatResponse:
        evidence = [
            ChatEvidence(
                source_id=hit.source.source_id,
                investigation_id=hit.investigation.investigation_id,
                document_title=hit.source.document_title,
                source_url=hit.source.source_url,
                page_number=hit.excerpt.page_number or hit.source.page_number,
                section=_citation_section(hit),
                excerpt=hit.excerpt.excerpt,
            )
            for hit in hits
        ]
        citations = [
            SourceCitation(
                source_id=hit.source.source_id,
                document_title=hit.source.document_title,
                source_url=hit.source.source_url,
                page_number=hit.excerpt.page_number or hit.source.page_number,
                section=_citation_section(hit),
                quote_or_supported_excerpt=hit.excerpt.excerpt,
                local_file_path=hit.source.local_file_path,
                downloaded_at=hit.source.downloaded_at,
                sha256=hit.source.sha256,
                file_size_bytes=hit.source.file_size_bytes,
                mime_type=hit.source.mime_type,
                last_verified_at=hit.source.last_verified_at,
                verification_status=hit.source.verification_status,
            )
            for hit in hits
        ]
        limitations = [answer.limitations]
        if provider_failure:
            limitations.append(provider_failure)
        if has_scenario:
            limitations.append(
                "Scenario values are user-entered assumptions, not NASA measurements."
            )
        if any(hit.investigation.environment == "microgravity" for hit in hits):
            limitations.append(
                "Microgravity evidence does not establish lunar or Martian partial-gravity performance."
            )
        if any(
            source.verification_status == "unavailable"
            for hit in hits
            for source in hit.investigation.sources
        ):
            limitations.append(
                "One or more linked NASA source files are unavailable locally; only retrieved verified excerpts are used."
            )
        limitations.append("Generated interpretation is not a NASA-reported fact.")
        source_excerpts = "\n".join(
            (
                f'- {"NASA-reported" if hit.source.source_type.startswith("NASA_") else "Indexed"} '
                f'excerpt [{hit.source.source_id}]: "{hit.excerpt.excerpt}"'
            )
            for hit in hits
        )
        sources = "\n".join(
            f"- [{item.source_id}] {item.document_title} ({item.source_url})"
            for item in evidence
        )
        formatted_answer = (
            f"Short answer (interpretation): {answer.short_answer}\n\n"
            f"Evidence (verbatim source excerpts):\n{source_excerpts}\n\n"
            f"Relevance to the scenario (interpretation): {answer.scenario_relevance}\n\n"
            f"Limitations / research gaps: {' '.join(limitations)}\n\n"
            f"Sources:\n{sources}"
        )
        return ChatResponse(
            answer=formatted_answer,
            evidence=evidence,
            citations=citations,
            limitations=limitations,
            answer_status=answer.answer_status,
        )

    def measurements(
        self, investigation_id: str | None, variable: str | None
    ) -> MeasurementList:
        if investigation_id is not None:
            investigation = self.store.get_investigation(investigation_id)
            if investigation is None:
                raise APIError(404, "NOT_FOUND", "Investigation not found.")
            investigations = [investigation]
        else:
            investigations, _ = self.store.list_investigations(page_size=1_000_000)

        sources = {
            (investigation.investigation_id, source.source_id): source
            for investigation in investigations
            for source in investigation.sources
        }
        data: list[MeasurementObservation] = []
        for item in self.store.measurements(investigation_id, variable):
            source = sources.get((item.investigation_id, item.source_id))
            if (
                source is None
                or source.verification_status != "verified"
                or source.source_type not in {"NASA_PSI", "NASA_REPORT", "NASA_DATASET"}
            ):
                continue
            point = item.model_dump()
            point.update(
                document_title=source.document_title,
                source_url=source.source_url,
                page_number=item.page_number or source.page_number,
                section=item.section or source.section,
            )
            data.append(MeasurementObservation.model_validate(point))

        availability = (
            "numeric_dataset"
            if data
            else (
                investigations[0].data_availability
                if investigation_id and investigations
                else (
                    investigations[0].data_availability
                    if investigations
                    and len({item.data_availability for item in investigations}) == 1
                    else "unknown"
                )
            )
        )
        message = (
            "Reported NASA-source observations are shown; plotted values are observations, not predictions."
            if data
            else (
                f"No verified numeric observations are indexed. Catalog data availability: {availability}."
            )
        )
        return MeasurementList(
            data=data,
            data_availability=availability,
            message=message,
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
                local_file_path=source.local_file_path,
                downloaded_at=source.downloaded_at,
                sha256=source.sha256,
                file_size_bytes=source.file_size_bytes,
                mime_type=source.mime_type,
                last_verified_at=source.last_verified_at,
                verification_status=source.verification_status,
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
        if any(
            source.verification_status == "unavailable"
            for item in items
            for source in item.sources
        ):
            gaps.append("One or more linked source documents are unavailable locally.")
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


def _citation_section(hit: EvidenceHit) -> str | None:
    if hit.excerpt.section is not None:
        return hit.excerpt.section
    return hit.source.section if hit.excerpt.page_number is None else None


def _compare_field_values(
    field: ComparisonFieldName, values: list[ComparisonValue]
) -> tuple[ComparisonStatus, str | None]:
    raw_values = [value.value for value in values]
    if field == "conditions":
        conditions = [
            value for value in raw_values if isinstance(value, InvestigationConditions)
        ]
        if len(conditions) != len(raw_values) or any(
            item.oxygen_pct is None
            or item.pressure.value is None
            or item.pressure.unit is None
            for item in conditions
        ):
            return (
                "not_comparable",
                "One or more records have incomplete oxygen or pressure conditions.",
            )
        pressure_units = {item.pressure.unit for item in conditions}
        if len(pressure_units) != 1:
            return (
                "not_comparable",
                "Pressure units differ; numeric conversion is not performed.",
            )
        if all(item == conditions[0] for item in conditions[1:]):
            return "same", None
        return "different", None

    if any(_comparison_value_is_missing(value) for value in raw_values):
        return (
            "not_comparable",
            "At least one selected record does not report this field.",
        )
    if all(value == raw_values[0] for value in raw_values[1:]):
        return "same", None
    return "different", None


def _comparison_value_is_missing(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip() or value == "unknown"
    if isinstance(value, list):
        return not value
    return False


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
    if any(source.verification_status == "unavailable" for source in investigation.sources):
        limitations.append("One or more linked source documents are unavailable locally.")
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
            local_file_path=source.local_file_path,
            downloaded_at=source.downloaded_at,
            sha256=source.sha256,
            file_size_bytes=source.file_size_bytes,
            mime_type=source.mime_type,
            last_verified_at=source.last_verified_at,
            verification_status=source.verification_status,
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
