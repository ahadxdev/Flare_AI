from __future__ import annotations

import hashlib
import logging
import math
import re
from dataclasses import dataclass, field
from pathlib import Path

from pypdf.errors import PdfReadError

from app.document_index import iter_verified_source_pages
from app.models import (
    Investigation,
    Measurement,
    MeasurementCandidate,
    MeasurementCandidateClassification,
    Source,
)


_NUMBER = (
    r"(?<![\w.-])[-+−]?(?:\d{1,3}(?:,\d{3})+|\d+)"
    r"(?:\.\d*)?(?:[eE][-+]?\d+)?|(?<![\w.-])[-+−]?\.\d+(?:[eE][-+]?\d+)?"
)
_UNIT = (
    r"(?:mm(?:²|2)\s*/\s*s|mm\s*/\s*s|cm\s*/\s*s|m\s*/\s*s|µm\s*/\s*s|μm\s*/\s*s|"
    r"kPa|MPa|GPa|psi|atm|bar|Pa|°\s*[CF]|degrees?\s*[CF]|K|"
    r"mm|cm|µm|μm|um|W|kW|MW|mg|g|kg|mL|L|ppm|percent|"
    r"seconds?|secs?|minutes?|mins?|hrs?|h|ms|m|s|%)"
)
_QUANTITY = re.compile(
    rf"(?P<approximate>~\s*)?(?P<reported_value>{_NUMBER})\s*[-–—]?\s*"
    rf"(?P<unit>{_UNIT})(?:(?![A-Za-z])|(?=O\s?2))",
    re.IGNORECASE,
)
_NUMERIC_TOKEN = re.compile(_NUMBER)
_TABLE_REFERENCE = re.compile(r"\bTable\s+([A-Z]?\d+[A-Z]?)\b", re.IGNORECASE)
_RUN_ID = re.compile(r"(?:\bRun\s*)?#\s*(\d+)\b", re.IGNORECASE)
_FLEX_TEST_ID = re.compile(r"\bFLEX\s*[–−-]\s*0*(\d+)\b", re.IGNORECASE)
_SECTION = re.compile(
    r"^\s*\d+(?:\.\d+)*\s+[A-Z][A-Za-z0-9 &/()-]{1,70}\s*$"
)
_APPENDIX_SECTION = re.compile(r"^\s*(A\.\d+)\s+([A-Z][A-Za-z0-9 &/()-]{1,70})\s*$")
_TABLE_IX_TITLE = re.compile(r"\bTABLE\s+IX\b", re.IGNORECASE)
_TABLE_IX_HEADER_TERMS = (
    "ambient",
    "pressure",
    "initial ambient",
    "mole fraction",
    "droplet",
    "visible",
    "burning",
    "time",
    "test end",
    "identifier",
)
_TABLE_IX_ROW = re.compile(r"^\s*FLEX\s*[–−-]\s*0*\d+\b", re.IGNORECASE)
_TABLE_NUMBER = re.compile(r"^[−+-]?(?:\d+(?:\.\d*)?|\.\d+)$")
_TABLE_VALUE = re.compile(
    r"^(?P<approximate>~)?(?P<value>[−+-]?(?:\d+(?:\.\d*)?|\.\d+))$"
)

_VARIABLES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("extinction diameter", re.compile(r"\bextinction\s+(?:droplet\s+)?diameters?\b", re.I)),
    ("initial droplet diameter", re.compile(r"\binitial\s+(?:droplet\s+)?diameters?\b", re.I)),
    ("initial droplet diameter", re.compile(r"\binitial\s+(?:methanol\s+)?droplet\s+sizes?\b", re.I)),
    ("flame propagation rate", re.compile(r"\b(?:flame\s+)?(?:propagation|spread)\s+(?:rate|velocity|speed)\b", re.I)),
    ("burning-rate constant", re.compile(r"\b(?:burning|burn)\s*[- ]?rate\s+constant\b|\bK(?:ex|cal)\b", re.I)),
    ("burning rate", re.compile(r"\b(?:burning|burn)\s*[- ]?rate\b", re.I)),
    ("heat release rate", re.compile(r"\bheat\s+release\s+rates?\b", re.I)),
    ("flame diameter", re.compile(r"\bflame\s+diameters?\b", re.I)),
    ("droplet diameter", re.compile(r"\bdroplet\s+diameters?\b", re.I)),
    ("oxygen concentration", re.compile(r"\b(?:oxygen|O\s?2)\s+(?:mole\s+)?(?:concentration|fraction|level)\b|\b\d+(?:\.\d+)?%\s*O\s?2\b", re.I)),
    ("pressure", re.compile(r"\bpressures?\b", re.I)),
    ("temperature", re.compile(r"\btemperatures?\b|\btemp\.?\b", re.I)),
    ("flow velocity", re.compile(r"\b(?:flow\s+)?velocities\b|\bflow\s+velocity\b", re.I)),
    ("time", re.compile(r"\b(?:burning|burn|residence|extinction|combustion)\s+times?\b", re.I)),
    ("mass", re.compile(r"\bmass(?:\s+loss)?\b", re.I)),
)

_SIMULATION_CUES = re.compile(
    r"\b(?:simulation|simulated|numerical model|computational|predicted)\b",
    re.IGNORECASE,
)
_HYPOTHETICAL_CUES = re.compile(
    r"\b(?:hypothetical|assumed|mission scenario|demonstration assumption)\b",
    re.IGNORECASE,
)
_SETUP_CUES = re.compile(
    r"\b(?:initial|ambient|set\s+to|maintained\s+at|working\s+pressure|"
    r"varied\s+between|varied\s+from|test\s+conditions?|inlet|diluent|"
    r"concentration\s+varied|atmosphere\s+consisting)\b",
    re.IGNORECASE,
)
_BOUNDARY_CUES = re.compile(
    r"\b(?:ambient|atmosphere|working|test\s+conditions?|chamber|"
    r"mole\s+fraction|oxygen\s+concentration|pressure)\b",
    re.IGNORECASE,
)
_SUMMARY_CUES = re.compile(
    r"\b(?:average|on average|most tests|in summary|typically|well below|"
    r"results showed|estimated|approximately)\b",
    re.IGNORECASE,
)
_APPROXIMATE_CUES = re.compile(r"(?:~|\bapproximately\b|\bapprox\.?\b|\babout\b)", re.I)
_DERIVED_CUES = re.compile(
    r"\b(?:calculated|derived|linear fit|slope|regression)\b",
    re.IGNORECASE,
)
_EXPLICIT_RESULT_CUES = re.compile(
    r"\b(?:extinction\b.{0,40}\boccurs?\s+at|extinction\s+diameters?\b.{0,100}\b"
    r"(?:was|were|is|are)\b|(?:was|were)\s+(?:measured|observed|recorded)\s+at)\b",
    re.IGNORECASE | re.DOTALL,
)
_NASA_SOURCE_TYPES = {"NASA_PSI", "NASA_REPORT", "NASA_DATASET"}
_LOGGER = logging.getLogger("flare.measurement_extraction")


@dataclass
class MeasurementExtractionReport:
    sources_processed: list[dict[str, object]] = field(default_factory=list)
    pages_processed: int = 0
    pages_without_text: list[dict[str, object]] = field(default_factory=list)
    pages_failed: list[dict[str, object]] = field(default_factory=list)
    rejected: dict[str, int] = field(default_factory=dict)
    issues: list[dict[str, str]] = field(default_factory=list)
    duplicate_candidates_suppressed: list[dict[str, str]] = field(
        default_factory=list
    )
    pdf_source_ids_processed: set[str] = field(default_factory=set, repr=False)
    unique_pdf_pages_with_text: set[tuple[str, int]] = field(
        default_factory=set, repr=False
    )

    def reject(self, reason: str, count: int = 1) -> None:
        self.rejected[reason] = self.rejected.get(reason, 0) + count

    def as_dict(
        self, candidates: list[MeasurementCandidate], staged_count: int | None = None
    ) -> dict[str, object]:
        classifications: dict[str, int] = {}
        for candidate in candidates:
            classification = candidate.classification
            classifications[classification] = classifications.get(classification, 0) + 1
        result: dict[str, object] = {
            "sources_processed": self.sources_processed,
            "pdfs_processed": len(self.pdf_source_ids_processed),
            "pages_processed": self.pages_processed,
            "unique_pdf_pages_with_text": len(self.unique_pdf_pages_with_text),
            "pages_without_text": self.pages_without_text,
            "pages_failed": self.pages_failed,
            "candidates_extracted": len(candidates),
            "candidates_by_classification": classifications,
            "review_status": "pending_review",
            "rejected": self.rejected,
            "issues": self.issues,
            "duplicate_candidates_suppressed": self.duplicate_candidates_suppressed,
        }
        if staged_count is not None:
            result["candidates_newly_staged"] = staged_count
        return result


def extract_measurement_candidates(
    investigations: list[Investigation],
    repository_root: str | Path,
) -> tuple[list[MeasurementCandidate], MeasurementExtractionReport]:
    root = Path(repository_root).resolve()
    candidates: list[MeasurementCandidate] = []
    report = MeasurementExtractionReport()
    seen_candidate_ids: set[str] = set()

    for investigation in investigations:
        for source in investigation.sources:
            if source.verification_status != "verified":
                report.reject(f"source_not_verified:{source.verification_status}")
                continue
            if source.source_type not in _NASA_SOURCE_TYPES:
                report.reject("source_not_a_NASA_record")
                continue
            if not source.local_file_path:
                report.reject("verified_source_has_no_local_file")
                continue

            path = (root / source.local_file_path).resolve()
            try:
                path.relative_to(root)
            except (OSError, ValueError, PdfReadError) as exc:
                _LOGGER.error(
                    "Verified source path is invalid",
                    extra={"source_id": source.source_id, "error": str(exc)},
                )
                report.issues.append(
                    {"source_id": source.source_id, "message": str(exc)}
                )
                continue

            nonempty_pages = 0
            source_candidates = 0
            table_ix_active = False
            current_section: str | None = None
            try:
                pages = iter_verified_source_pages(
                    path,
                    source,
                    layout=True,
                    include_empty_pages=True,
                )
                for page in pages:
                    page_number, section, text = (
                        page.page_number,
                        page.section,
                        page.text,
                    )
                    if page.error is not None:
                        _LOGGER.warning(
                            "PDF page text extraction failed",
                            extra={
                                "source_id": source.source_id,
                                "page_number": page_number,
                                "error": page.error,
                            },
                        )
                        report.pages_failed.append(
                            {
                                "source_id": source.source_id,
                                "page_number": page_number,
                                "message": page.error,
                            }
                        )
                        continue
                    if source.mime_type == "application/pdf":
                        report.pdf_source_ids_processed.add(source.source_id)
                        if page_number is not None and text.strip():
                            report.unique_pdf_pages_with_text.add(
                                (source.source_id, page_number)
                            )
                    if not text.strip():
                        if page_number is not None:
                            report.pages_without_text.append(
                                {
                                    "source_id": source.source_id,
                                    "page_number": page_number,
                                    "reason": "No text layer was extracted; OCR was not run.",
                                }
                            )
                        continue
                    nonempty_pages += 1
                    report.pages_processed += 1
                    if section is not None:
                        current_section = section
                    appendix = next(
                        (
                            match
                            for line in text.splitlines()
                            if (match := _APPENDIX_SECTION.match(line))
                        ),
                        None,
                    )
                    if appendix is not None:
                        current_section = (
                            f"{appendix.group(1)} {appendix.group(2)}"
                        )

                    if (
                        source.source_id == "src-ntrs-flex-results"
                        and _TABLE_IX_TITLE.search(text)
                    ):
                        table_ix_active = True
                    page_candidates, page_rejections = extract_page_candidates(
                        investigation=investigation,
                        source=source,
                        page_number=page_number,
                        section=current_section,
                        text=text,
                        extraction_method=(
                            "metadata_text" if page_number is None else "pdf_text"
                        ),
                    )
                    if (
                        table_ix_active
                        and source.source_id == "src-ntrs-flex-results"
                        and _has_table_ix_headers(text)
                    ):
                        table_candidates, table_rejections = (
                            extract_table_ix_candidates(
                                investigation=investigation,
                                source=source,
                                page_number=page_number,
                                section=current_section,
                                text=text,
                            )
                        )
                        page_candidates.extend(table_candidates)
                        for reason, count in table_rejections.items():
                            page_rejections[reason] = (
                                page_rejections.get(reason, 0) + count
                            )
                    for reason, count in page_rejections.items():
                        report.reject(reason, count)
                    for candidate in page_candidates:
                        if candidate.candidate_id in seen_candidate_ids:
                            report.reject("duplicate_candidate_in_extraction_batch")
                            continue
                        seen_candidate_ids.add(candidate.candidate_id)
                        candidates.append(candidate)
                        source_candidates += 1
            except (OSError, ValueError, PdfReadError) as exc:
                _LOGGER.error(
                    "Verified source extraction failed",
                    extra={"source_id": source.source_id, "error": str(exc)},
                )
                report.issues.append(
                    {"source_id": source.source_id, "message": str(exc)}
                )
                continue

            report.sources_processed.append(
                {
                    "source_id": source.source_id,
                    "document_title": source.document_title,
                    "source_url": str(source.source_url),
                    "local_file_path": source.local_file_path,
                    "source_sha256": source.sha256,
                    "text_pages": nonempty_pages,
                    "candidates": source_candidates,
                }
            )
    return candidates, report


def reconcile_approved_measurement_duplicates(
    candidates: list[MeasurementCandidate],
    measurements: list[Measurement],
) -> tuple[list[MeasurementCandidate], list[dict[str, str]]]:
    remaining: list[MeasurementCandidate] = []
    suppressed: list[dict[str, str]] = []
    for candidate in candidates:
        candidate_run = _run_number(candidate.observation_context)
        matching = next(
            (
                measurement
                for measurement in measurements
                if candidate_run is not None
                and candidate.investigation_id == measurement.investigation_id
                and _canonical_variable(candidate.variable)
                == _canonical_variable(measurement.variable)
                and candidate_run == _run_number(measurement.observation_context)
            ),
            None,
        )
        if matching is None:
            remaining.append(candidate)
            continue
        if (
            candidate.unit.casefold() == matching.unit.casefold()
            and candidate.value == matching.value
        ):
            suppressed.append(
                {
                    "candidate_id": candidate.candidate_id,
                    "measurement_id": matching.measurement_id,
                    "reason": "Exact approved run/variable/value duplicate.",
                }
            )
            continue

        flag = (
            "conflicts_with_approved_measurement: "
            f"{matching.measurement_id} reports "
            f"{matching.reported_value or matching.value} {matching.unit}; "
            f"this source reports {candidate.reported_value} {candidate.unit}."
        )
        remaining.append(
            candidate.model_copy(
                update={
                    "classification": "ambiguous",
                    "review_flags": [
                        *candidate.review_flags,
                        flag,
                    ],
                }
            )
        )
    return remaining, suppressed


def extract_page_candidates(
    *,
    investigation: Investigation,
    source: Source,
    page_number: int | None,
    section: str | None,
    text: str,
    extraction_method: str,
) -> tuple[list[MeasurementCandidate], dict[str, int]]:
    if source.sha256 is None:
        return [], {"missing_source_checksum": 1}
    lines = text.splitlines()
    candidates: list[MeasurementCandidate] = []
    rejected: dict[str, int] = {}

    for line_index, line in enumerate(lines):
        numeric_tokens = list(_NUMERIC_TOKEN.finditer(line))
        quantities = list(_QUANTITY.finditer(line))
        covered_spans = [(match.start(), match.end()) for match in quantities]
        uncovered = sum(
            not any(start <= token.start() < end for start, end in covered_spans)
            for token in numeric_tokens
        )
        if uncovered:
            rejected["number_without_supported_unit"] = (
                rejected.get("number_without_supported_unit", 0) + uncovered
            )
        if not quantities:
            continue
        for quantity_index, quantity in enumerate(quantities):
            context_start = max(0, line_index - 3)
            context_end = min(len(lines), line_index + 4)
            local_lines = lines[context_start:context_end]
            local_text = "\n".join(local_lines)
            local_line_index = line_index - context_start
            line_offset = len("\n".join(local_lines[:local_line_index]))
            if local_line_index:
                line_offset += 1
            value_position = line_offset + quantity.start()
            variable = _identify_variable(local_text, value_position)
            if variable is None:
                rejected["quantity_without_recognized_variable"] = (
                    rejected.get("quantity_without_recognized_variable", 0) + 1
                )
                continue

            support_start = max(0, line_index - 3)
            support_end = min(len(lines), line_index + 4)
            supporting_excerpt = "\n".join(lines[support_start:support_end]).strip()
            table_reference = _find_table_reference(lines, line_index)
            extraction_type = (
                "pdf_table_text"
                if table_reference is not None and extraction_method == "pdf_text"
                else extraction_method
            )
            current_section = section or _find_section(lines, line_index)
            classification, confidence = _classify_candidate(
                variable=variable,
                local_text=local_text,
                value_position=value_position,
                same_line_text=line,
                same_line_value_position=quantity.start(),
            )
            value_text = quantity.group("reported_value")
            value = float(value_text.replace(",", "").replace("−", "-"))
            if not math.isfinite(value):
                rejected["non_finite_numeric_value"] = (
                    rejected.get("non_finite_numeric_value", 0) + 1
                )
                continue
            observation_context = _observation_context(
                local_text=local_text,
                same_line_text=line,
                value_position=value_position,
                quantities=quantities,
                quantity_index=quantity_index,
                line_offset=line_offset,
            )
            approximate = (
                quantity.group("approximate") is not None
                or classification == "approximate_value"
            )
            if approximate:
                classification = "approximate_value"
            reported_value = (
                f"~{value_text}" if quantity.group("approximate") else value_text
            )
            candidate_id = _candidate_id(
                investigation_id=investigation.investigation_id,
                source=source,
                page_number=page_number,
                variable=variable,
                reported_value=value_text,
                unit=quantity.group("unit"),
                observation_context=observation_context,
            )
            candidates.append(
                MeasurementCandidate(
                    candidate_id=candidate_id,
                    investigation_id=investigation.investigation_id,
                    source_id=source.source_id,
                    document_title=source.document_title,
                    source_url=source.source_url,
                    source_sha256=source.sha256,
                    variable=variable,
                    reported_value=reported_value,
                    value=value,
                    unit=quantity.group("unit"),
                    observation_context=observation_context,
                    page_number=page_number,
                    section=current_section,
                    table_reference=table_reference,
                    supporting_excerpt=supporting_excerpt,
                    extraction_method=extraction_type,
                    confidence=confidence,
                    classification=classification,
                    review_flags=(
                        ["approximate_reported_value"] if approximate else []
                    ),
                )
            )

    return candidates, rejected


def _run_number(context: dict[str, str | float | None]) -> str | None:
    for key in ("run", "test"):
        value = context.get(key)
        if isinstance(value, str):
            match = re.search(r"(\d+)\s*$", value)
            if match:
                return match.group(1).lstrip("0") or "0"
    return None


def _canonical_variable(variable: str | None) -> str | None:
    if variable is None:
        return None
    normalized = " ".join(variable.casefold().split())
    if normalized == "visible flame extinction diameter":
        return "extinction diameter"
    return normalized


def extract_table_ix_candidates(
    *,
    investigation: Investigation,
    source: Source,
    page_number: int | None,
    section: str | None,
    text: str,
) -> tuple[list[MeasurementCandidate], dict[str, int]]:
    if source.sha256 is None:
        return [], {"missing_source_checksum": 1}
    if page_number is None:
        return [], {"table_row_missing_page_number": 1}
    if not _has_table_ix_headers(text):
        return [], {}

    definitions: tuple[
        tuple[int, str, str, MeasurementCandidateClassification], ...
    ] = (
        (5, "pressure", "mmHg", "boundary_condition"),
        (6, "oxygen mole fraction", "mole fraction", "boundary_condition"),
        (7, "nitrogen mole fraction", "mole fraction", "boundary_condition"),
        (8, "carbon dioxide mole fraction", "mole fraction", "boundary_condition"),
        (9, "helium mole fraction", "mole fraction", "boundary_condition"),
        (10, "initial droplet diameter", "mm", "initial_condition"),
        (
            11,
            "visible flame extinction diameter",
            "mm",
            "experimental_observation",
        ),
        (12, "burning rate", "mm2/s", "derived_quantity"),
        (13, "burn time", "s", "experimental_observation"),
    )
    lines = text.splitlines()
    candidates: list[MeasurementCandidate] = []
    rejected: dict[str, int] = {}
    for row_index, line in enumerate(lines):
        if not _TABLE_IX_ROW.match(line):
            continue
        columns = re.split(r"\s{2,}", line.strip())
        if len(columns) != 15:
            rejected["malformed_table_ix_row"] = (
                rejected.get("malformed_table_ix_row", 0) + 1
            )
            continue
        test_id = columns[0]
        context = _table_ix_context(columns)
        nonempty_headers = [
            prior.strip()
            for prior in lines[:row_index]
            if prior.strip()
        ][-4:]
        supporting_excerpt = "\n".join([*nonempty_headers, line.strip()])
        current_section = section or "A.2 Experiment Results"

        for column_index, variable, unit, classification in definitions:
            reported_value = columns[column_index].strip()
            number = _TABLE_VALUE.fullmatch(reported_value)
            if number is None:
                continue
            approximate = number.group("approximate") is not None
            value = float(number.group("value").replace("−", "-"))
            observation_context = {
                **context,
                "test": test_id,
            }
            candidate_id = _candidate_id(
                investigation_id=investigation.investigation_id,
                source=source,
                page_number=page_number,
                variable=variable,
                reported_value=reported_value,
                unit=unit,
                observation_context=observation_context,
            )
            candidates.append(
                MeasurementCandidate(
                    candidate_id=candidate_id,
                    investigation_id=investigation.investigation_id,
                    source_id=source.source_id,
                    document_title=source.document_title,
                    source_url=source.source_url,
                    source_sha256=source.sha256,
                    variable=variable,
                    reported_value=reported_value,
                    value=value,
                    unit=unit,
                    observation_context=observation_context,
                    page_number=page_number,
                    section=current_section,
                    table_reference="Table IX",
                    supporting_excerpt=supporting_excerpt,
                    extraction_method="pdf_table_text",
                    confidence=0.98,
                    classification=(
                        "approximate_value" if approximate else classification
                    ),
                    review_flags=(
                        ["approximate_reported_value"] if approximate else []
                    ),
                )
            )
    return candidates, rejected


def _has_table_ix_headers(text: str) -> bool:
    lowered = " ".join(text.casefold().split())
    return all(term in lowered for term in _TABLE_IX_HEADER_TERMS)


def _table_ix_context(columns: list[str]) -> dict[str, str | None]:
    context: dict[str, str | None] = {
        "flex_identifier": columns[1],
        "fuel": columns[4],
        "test_end": columns[14],
    }
    for key, index, unit in (
        ("ambient_pressure", 5, "mmHg"),
        ("oxygen_mole_fraction", 6, "mole fraction"),
        ("nitrogen_mole_fraction", 7, "mole fraction"),
        ("carbon_dioxide_mole_fraction", 8, "mole fraction"),
        ("helium_mole_fraction", 9, "mole fraction"),
    ):
        value = columns[index].strip()
        context[key] = (
            f"{value} {unit}" if _TABLE_NUMBER.fullmatch(value) else None
        )
    return context


def _identify_variable(text: str, value_position: int) -> str | None:
    matches: list[tuple[int, str]] = []
    for variable, pattern in _VARIABLES:
        matches.extend(
            (match.start() + (match.end() - match.start()) // 2, variable)
            for match in pattern.finditer(text)
        )
    if not matches:
        return None
    nearest_variable = min(matches, key=lambda match: abs(match[0] - value_position))[1]
    nearest_distance = min(abs(match[0] - value_position) for match in matches)
    if nearest_distance > 55:
        return None
    nearby = text[max(0, value_position - 55) : value_position + 55]
    if (
        nearest_variable == "droplet diameter"
        and re.search(r"\bextinction\b", nearby, re.IGNORECASE)
    ):
        return "extinction diameter"
    return nearest_variable


def _classify_candidate(
    *,
    variable: str,
    local_text: str,
    value_position: int,
    same_line_text: str,
    same_line_value_position: int,
) -> tuple[MeasurementCandidateClassification, float]:
    value_context = local_text[max(0, value_position - 55) : value_position + 65]
    wider_context = local_text[
        max(0, value_position - 120) : value_position + 100
    ]
    same_line_context = same_line_text[
        max(0, same_line_value_position - 55) : same_line_value_position + 65
    ]
    if _HYPOTHETICAL_CUES.search(wider_context):
        return "hypothetical", 0.15
    if _SIMULATION_CUES.search(wider_context):
        return "simulation_input", 0.45
    if _APPROXIMATE_CUES.search(same_line_context):
        return "approximate_value", 0.55
    if variable == "initial droplet diameter":
        return "initial_condition", 0.95
    if variable in {"burning rate", "burning-rate constant"} and _DERIVED_CUES.search(
        wider_context
    ):
        return "derived_quantity", 0.85
    if (
        variable == "extinction diameter"
        and _EXPLICIT_RESULT_CUES.search(wider_context)
    ):
        return "experimental_observation", 0.98
    if re.search(
        r"\b(?:measured|observed|recorded)\b.{0,30}\b(?:was|were|at)\b",
        same_line_context,
        re.IGNORECASE,
    ):
        return "experimental_observation", 0.90
    if variable in {"pressure", "oxygen concentration"} and _BOUNDARY_CUES.search(
        wider_context
    ):
        return "boundary_condition", 0.92
    if _SETUP_CUES.search(value_context):
        return "setup_parameter", 0.92
    if _SUMMARY_CUES.search(wider_context):
        return "reported_summary", 0.65
    return "ambiguous", 0.35


def _observation_context(
    *,
    local_text: str,
    same_line_text: str,
    value_position: int,
    quantities: list[re.Match[str]],
    quantity_index: int,
    line_offset: int,
) -> dict[str, str | float | None]:
    runs = list(_RUN_ID.finditer(local_text))
    runs_before = [run for run in runs if run.start() < value_position]
    selected_run: re.Match[str] | None = None
    test_ids = list(_FLEX_TEST_ID.finditer(local_text))
    respectively_position = local_text.casefold().find("respectively")
    quantity_line_end = line_offset + quantities[-1].end()
    respective_run_list = (
        respectively_position >= quantity_line_end
        and respectively_position - quantity_line_end <= 80
    )
    if (
        "respectively" in same_line_text.casefold() or respective_run_list
    ) and len(runs) >= len(quantities):
        selected_runs = runs[-len(quantities) :]
        selected_run = selected_runs[min(quantity_index, len(selected_runs) - 1)]
    elif runs_before:
        selected_run = runs_before[-1]
    context: dict[str, str | float | None] = {}
    if selected_run is not None:
        context["run"] = f"#{selected_run.group(1)}"
    elif test_ids:
        selected_test = test_ids[-1]
        context["test"] = f"FLEX-{selected_test.group(1)}"
    return context


def _find_table_reference(lines: list[str], line_index: int) -> str | None:
    for line in reversed(lines[max(0, line_index - 4) : line_index + 1]):
        reference = _TABLE_REFERENCE.search(line)
        if reference is not None:
            return f"Table {reference.group(1)}"
    return None


def _find_section(lines: list[str], line_index: int) -> str | None:
    for line in reversed(lines[max(0, line_index - 20) : line_index + 1]):
        if _SECTION.match(line):
            return " ".join(line.split())
        appendix = _APPENDIX_SECTION.match(line)
        if appendix is not None:
            return f"{appendix.group(1)} {appendix.group(2)}"
    return None


def _candidate_id(
    *,
    investigation_id: str,
    source: Source,
    page_number: int | None,
    variable: str,
    reported_value: str,
    unit: str,
    observation_context: dict[str, str | float | None],
) -> str:
    identity = "\x1f".join(
        (
            investigation_id,
            source.source_id,
            source.sha256 or "",
            str(page_number),
            variable,
            reported_value,
            unit,
            repr(sorted(observation_context.items())),
        )
    )
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    return f"candidate-{digest}"
