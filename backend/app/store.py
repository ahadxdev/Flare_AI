import json
import os
import re
import sqlite3
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.ingestion import validate_source_files
from app.models import (
    AdditionalMeasurementEvidence,
    EvidenceExcerpt,
    Investigation,
    Measurement,
    MeasurementCandidate,
    MeasurementCandidateClassification,
    MeasurementReviewEvent,
    ScenarioAnalysisResponse,
    Source,
)


DEFAULT_DATABASE = Path(__file__).resolve().parents[1] / "flare_ai.sqlite3"
_SEARCH_STOPWORDS = {
    "about",
    "after",
    "again",
    "are",
    "did",
    "does",
    "for",
    "from",
    "how",
    "into",
    "is",
    "its",
    "not",
    "that",
    "the",
    "their",
    "this",
    "was",
    "what",
    "when",
    "where",
    "which",
    "with",
}


def _semantic_similarity(query: str, text: str) -> float:
    """Rank local evidence with deterministic term-vector cosine similarity."""
    query_terms = [
        term
        for term in re.findall(r"[a-z0-9]{2,}", query.casefold())
        if term not in _SEARCH_STOPWORDS
    ]
    text_terms = [
        term
        for term in re.findall(r"[a-z0-9]{2,}", text.casefold())
        if term not in _SEARCH_STOPWORDS
    ]
    if not query_terms or not text_terms:
        return 0.0
    query_counts = {term: query_terms.count(term) for term in set(query_terms)}
    text_counts = {term: text_terms.count(term) for term in set(text_terms)}
    vocabulary = set(query_counts) | set(text_counts)
    query_norm = math.sqrt(
        sum((query_counts.get(term, 0) ** 2) for term in vocabulary)
    )
    text_norm = math.sqrt(
        sum((text_counts.get(term, 0) ** 2) for term in vocabulary)
    )
    if query_norm == 0 or text_norm == 0:
        return 0.0
    return sum(
        query_counts.get(term, 0) * text_counts.get(term, 0)
        for term in vocabulary
    ) / (query_norm * text_norm)


def _append_audit_note(existing: str | None, correction: str) -> str:
    return f"{existing.rstrip()}\n\n{correction}" if existing else correction


def _has_approximate_reported_value(candidate: MeasurementCandidate) -> bool:
    if (
        candidate.classification == "approximate_value"
        or "approximate_reported_value" in candidate.review_flags
    ):
        return True
    numeric_value = re.escape(candidate.reported_value.lstrip("~").strip())
    return re.search(
        rf"(?:~\s*|(?:approximately|approx\.?|about)\s+)"
        rf"(?<![\w.]){numeric_value}(?![\w.])",
        candidate.supporting_excerpt,
        re.IGNORECASE,
    ) is not None


@dataclass(frozen=True)
class EvidenceHit:
    excerpt: EvidenceExcerpt
    investigation: Investigation
    source: Source


class SQLiteStore:
    def __init__(self, database_path: str | Path | None = None):
        self.database_path = Path(
            database_path or os.environ.get("FLARE_DATABASE_PATH", DEFAULT_DATABASE)
        )
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS investigations "
                "(investigation_id TEXT PRIMARY KEY, payload TEXT NOT NULL)"
            )
            connection.execute(
                "CREATE TABLE IF NOT EXISTS measurements "
                "(measurement_id TEXT PRIMARY KEY, investigation_id TEXT NOT NULL, "
                "variable TEXT NOT NULL, payload TEXT NOT NULL, "
                "FOREIGN KEY(investigation_id) REFERENCES investigations(investigation_id))"
            )
            connection.execute(
                "CREATE TABLE IF NOT EXISTS measurement_candidates "
                "(candidate_id TEXT PRIMARY KEY, investigation_id TEXT NOT NULL, "
                "source_id TEXT NOT NULL, review_status TEXT NOT NULL, payload TEXT NOT NULL, "
                "FOREIGN KEY(investigation_id) REFERENCES investigations(investigation_id))"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS measurement_candidates_status "
                "ON measurement_candidates(review_status, candidate_id)"
            )
            connection.execute(
                "CREATE TABLE IF NOT EXISTS measurement_review_history "
                "(review_event_id TEXT PRIMARY KEY, candidate_id TEXT NOT NULL, "
                "reviewed_at TEXT NOT NULL, payload TEXT NOT NULL)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS measurement_review_history_candidate "
                "ON measurement_review_history(candidate_id, reviewed_at, review_event_id)"
            )
            connection.execute(
                "CREATE TRIGGER IF NOT EXISTS measurement_review_history_no_update "
                "BEFORE UPDATE ON measurement_review_history BEGIN "
                "SELECT RAISE(ABORT, 'measurement review history is append-only'); END"
            )
            connection.execute(
                "CREATE TRIGGER IF NOT EXISTS measurement_review_history_no_delete "
                "BEFORE DELETE ON measurement_review_history BEGIN "
                "SELECT RAISE(ABORT, 'measurement review history is append-only'); END"
            )
            connection.execute(
                "CREATE TABLE IF NOT EXISTS evidence_excerpts "
                "(excerpt_id TEXT PRIMARY KEY, investigation_id TEXT NOT NULL, "
                "source_id TEXT NOT NULL, payload TEXT NOT NULL, "
                "FOREIGN KEY(investigation_id) REFERENCES investigations(investigation_id))"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS evidence_investigation_source "
                "ON evidence_excerpts(investigation_id, source_id)"
            )
            connection.execute(
                "CREATE VIRTUAL TABLE IF NOT EXISTS evidence_search USING fts5("
                "excerpt_id UNINDEXED, investigation_id UNINDEXED, "
                "source_id UNINDEXED, excerpt, tokenize='unicode61')"
            )
            connection.execute(
                "CREATE TRIGGER IF NOT EXISTS evidence_excerpts_insert "
                "AFTER INSERT ON evidence_excerpts BEGIN "
                "INSERT INTO evidence_search"
                "(excerpt_id, investigation_id, source_id, excerpt) VALUES "
                "(new.excerpt_id, new.investigation_id, new.source_id, "
                "json_extract(new.payload, '$.excerpt')); END"
            )
            connection.execute(
                "CREATE TRIGGER IF NOT EXISTS evidence_excerpts_update "
                "AFTER UPDATE ON evidence_excerpts BEGIN "
                "DELETE FROM evidence_search WHERE excerpt_id = old.excerpt_id; "
                "INSERT INTO evidence_search"
                "(excerpt_id, investigation_id, source_id, excerpt) VALUES "
                "(new.excerpt_id, new.investigation_id, new.source_id, "
                "json_extract(new.payload, '$.excerpt')); END"
            )
            connection.execute(
                "CREATE TRIGGER IF NOT EXISTS evidence_excerpts_delete "
                "AFTER DELETE ON evidence_excerpts BEGIN "
                "DELETE FROM evidence_search WHERE excerpt_id = old.excerpt_id; END"
            )
            connection.execute(
                "INSERT INTO evidence_search"
                "(excerpt_id, investigation_id, source_id, excerpt) "
                "SELECT excerpt_id, investigation_id, source_id, "
                "json_extract(payload, '$.excerpt') FROM evidence_excerpts "
                "WHERE NOT EXISTS (SELECT 1 FROM evidence_search "
                "WHERE evidence_search.excerpt_id = evidence_excerpts.excerpt_id)"
            )
            connection.execute(
                "CREATE TABLE IF NOT EXISTS scenario_analyses "
                "(scenario_id TEXT PRIMARY KEY, payload TEXT NOT NULL)"
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def list_investigations(
        self,
        q: str | None = None,
        research_area: str | None = None,
        environment: str | None = None,
        data_availability: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Investigation], int]:
        clauses: list[str] = []
        parameters: list[object] = []
        for field, value in (
            ("research_area", research_area),
            ("environment", environment),
            ("data_availability", data_availability),
        ):
            if value:
                clauses.append(f"json_extract(payload, '$.{field}') = ?")
                parameters.append(value)
        if q:
            clauses.append(
                "(lower(json_extract(payload, '$.title')) LIKE ? OR "
                "lower(json_extract(payload, '$.acronym')) LIKE ? OR "
                "lower(payload) LIKE ?)"
            )
            term = f"%{q.lower()}%"
            parameters.extend([term, term, term])
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connect() as connection:
            total = connection.execute(
                f"SELECT COUNT(*) FROM investigations{where}", parameters
            ).fetchone()[0]
            rows = connection.execute(
                f"SELECT payload FROM investigations{where} "
                "ORDER BY json_extract(payload, '$.title') "
                "LIMIT ? OFFSET ?",
                [*parameters, page_size, (page - 1) * page_size],
            ).fetchall()
        return [Investigation.model_validate_json(row["payload"]) for row in rows], total

    def get_investigation(self, investigation_id: str) -> Investigation | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM investigations WHERE investigation_id = ?",
                (investigation_id,),
            ).fetchone()
        return Investigation.model_validate_json(row["payload"]) if row else None

    def get_investigations(self, investigation_ids: list[str]) -> list[Investigation]:
        if not investigation_ids:
            return []
        placeholders = ",".join("?" for _ in investigation_ids)
        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT payload FROM investigations "
                f"WHERE investigation_id IN ({placeholders})",
                investigation_ids,
            ).fetchall()
        by_id = {
            investigation.investigation_id: investigation
            for investigation in (
                Investigation.model_validate_json(row["payload"]) for row in rows
            )
        }
        return [by_id[item_id] for item_id in investigation_ids if item_id in by_id]

    def measurements(
        self, investigation_id: str | None = None, variable: str | None = None
    ) -> list[Measurement]:
        clauses: list[str] = []
        parameters: list[str] = []
        if investigation_id:
            clauses.append("investigation_id = ?")
            parameters.append(investigation_id)
        if variable:
            clauses.append("lower(variable) = lower(?)")
            parameters.append(variable)
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT payload FROM measurements{where} ORDER BY variable",
                parameters,
            ).fetchall()
        return [Measurement.model_validate_json(row["payload"]) for row in rows]

    def measurements_for_investigations(
        self, investigation_ids: list[str]
    ) -> list[Measurement]:
        if not investigation_ids:
            return []
        placeholders = ",".join("?" for _ in investigation_ids)
        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT payload FROM measurements "
                f"WHERE investigation_id IN ({placeholders})",
                investigation_ids,
            ).fetchall()
        return [Measurement.model_validate_json(row["payload"]) for row in rows]

    def stage_measurement_candidates(
        self, candidates: list[MeasurementCandidate]
    ) -> int:
        candidate_ids = {item.candidate_id for item in candidates}
        if len(candidate_ids) != len(candidates):
            raise ValueError("Candidate IDs in the extraction batch must be unique.")

        inserted = 0
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            investigation_ids = {item.investigation_id for item in candidates}
            if investigation_ids:
                placeholders = ",".join("?" for _ in investigation_ids)
                rows = connection.execute(
                    "SELECT payload FROM investigations "
                    f"WHERE investigation_id IN ({placeholders})",
                    list(investigation_ids),
                ).fetchall()
            else:
                rows = []
            investigations = {
                item.investigation_id: item
                for item in (
                    Investigation.model_validate_json(row["payload"]) for row in rows
                )
            }

            for candidate in candidates:
                if candidate.review_status != "pending_review":
                    raise ValueError("Only pending candidates may be staged.")
                investigation = investigations.get(candidate.investigation_id)
                source = next(
                    (
                        item
                        for item in investigation.sources
                        if item.source_id == candidate.source_id
                    ),
                    None,
                ) if investigation else None
                if (
                    source is None
                    or source.verification_status != "verified"
                    or source.source_type not in {"NASA_PSI", "NASA_REPORT", "NASA_DATASET"}
                    or source.sha256 is None
                    or source.sha256.casefold() != candidate.source_sha256.casefold()
                    or str(source.source_url) != str(candidate.source_url)
                    or source.document_title != candidate.document_title
                ):
                    raise ValueError(
                        "Candidates must cite the matching verified NASA source "
                        "attached to their investigation."
                    )
                cursor = connection.execute(
                    "INSERT OR IGNORE INTO measurement_candidates"
                    "(candidate_id, investigation_id, source_id, review_status, payload) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (
                        candidate.candidate_id,
                        candidate.investigation_id,
                        candidate.source_id,
                        candidate.review_status,
                        candidate.model_dump_json(),
                    ),
                )
                inserted += cursor.rowcount
        return inserted

    def measurement_candidates(
        self, review_status: str | None = None
    ) -> list[MeasurementCandidate]:
        if review_status:
            query = (
                "SELECT payload FROM measurement_candidates "
                "WHERE review_status = ? ORDER BY candidate_id"
            )
            parameters = (review_status,)
        else:
            query = "SELECT payload FROM measurement_candidates ORDER BY candidate_id"
            parameters = ()
        with self._connect() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [
            MeasurementCandidate.model_validate_json(row["payload"])
            for row in rows
        ]

    def measurement_candidate(
        self, candidate_id: str
    ) -> MeasurementCandidate | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM measurement_candidates WHERE candidate_id = ?",
                (candidate_id,),
            ).fetchone()
        return (
            MeasurementCandidate.model_validate_json(row["payload"])
            if row
            else None
        )

    def measurement_review_history(
        self, candidate_id: str
    ) -> list[MeasurementReviewEvent]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload FROM measurement_review_history "
                "WHERE candidate_id = ? ORDER BY reviewed_at, review_event_id",
                (candidate_id,),
            ).fetchall()
        return [
            MeasurementReviewEvent.model_validate_json(row["payload"])
            for row in rows
        ]

    def correct_placeholder_reviewer_attributions(self) -> list[dict[str, str]]:
        placeholders = {"your name", "your reviewer name"}
        corrected: list[dict[str, str]] = []
        corrected_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            rows = connection.execute(
                "SELECT measurement_id, payload FROM measurements"
            ).fetchall()
            candidate_rows = connection.execute(
                "SELECT payload FROM measurement_candidates"
            ).fetchall()
            candidates_by_measurement = {
                candidate.measurement_id: candidate
                for candidate in (
                    MeasurementCandidate.model_validate_json(row["payload"])
                    for row in candidate_rows
                )
                if candidate.measurement_id is not None
            }
            for row in rows:
                measurement = Measurement.model_validate_json(row["payload"])
                previous_reviewer = (measurement.reviewed_by or "").strip()
                if previous_reviewer.casefold() not in placeholders:
                    continue
                correction = (
                    f"Audit correction {corrected_at}: removed placeholder reviewer "
                    f"attribution {previous_reviewer!r}; the original reviewer "
                    "could not be established. The existing approval status and "
                    "review timestamp are retained; this correction does not "
                    "certify the observation."
                )
                review_notes = _append_audit_note(
                    measurement.review_notes, correction
                )
                updated_measurement = measurement.model_copy(
                    update={"reviewed_by": None, "review_notes": review_notes}
                )
                connection.execute(
                    "UPDATE measurements SET payload = ? WHERE measurement_id = ?",
                    (
                        updated_measurement.model_dump_json(),
                        measurement.measurement_id,
                    ),
                )
                candidate = candidates_by_measurement.get(
                    measurement.measurement_id
                )
                corrected_candidate_id = ""
                if candidate is not None:
                    candidate_reviewer = (candidate.reviewed_by or "").strip()
                    if candidate_reviewer.casefold() in placeholders:
                        candidate_notes = _append_audit_note(
                            candidate.review_notes, correction
                        )
                        updated_candidate = MeasurementCandidate.model_validate(
                            {
                                **candidate.model_dump(),
                                "reviewed_by": None,
                                "review_notes": candidate_notes,
                            }
                        )
                        connection.execute(
                            "UPDATE measurement_candidates "
                            "SET payload = ? WHERE candidate_id = ?",
                            (
                                updated_candidate.model_dump_json(),
                                candidate.candidate_id,
                            ),
                        )
                        corrected_candidate_id = candidate.candidate_id
                corrected.append(
                    {
                        "measurement_id": measurement.measurement_id,
                        "candidate_id": corrected_candidate_id,
                        "previous_reviewer": previous_reviewer,
                        "reviewer_attribution": "unknown",
                    }
                )
        return corrected

    def review_measurement_candidate(
        self,
        candidate_id: str,
        decision: str,
        reviewer: str,
        *,
        classification: MeasurementCandidateClassification | None = None,
        classification_reason: str | None = None,
        notes: str | None = None,
        rationale: str | None = None,
        evidence_notes: str | None = None,
        source_review_confirmed: bool = False,
        measurement_definition_confirmed: bool = False,
        priority_resolution_confirmed: bool = False,
        conflict_resolution_confirmed: bool = False,
        audit_classification: str | None = None,
        audit_rationale: str | None = None,
        audit_quality_flags: list[str] | None = None,
        figure_reference: str | None = None,
        figure_caption_excerpt: str | None = None,
        zero_value_resolution_confirmed: bool = False,
        additional_evidence_source_id: str | None = None,
        additional_evidence_page_number: int | None = None,
        additional_evidence_section: str | None = None,
        additional_evidence_excerpt: str | None = None,
        additional_evidence_review_confirmed: bool = False,
        repository_root: str | Path | None = None,
    ) -> MeasurementCandidate | None:
        if decision not in {"approve", "reject", "needs_more_evidence"}:
            raise ValueError(
                "Candidate decision must be approve, reject, or needs_more_evidence."
            )
        if not reviewer.strip():
            raise ValueError("A reviewer name is required.")
        if reviewer.strip().casefold() in {
            "your name",
            "your reviewer name",
            "unknown",
            "unknown reviewer",
            "anonymous",
            "n/a",
        }:
            raise ValueError("Use the actual reviewer name, not a placeholder.")
        if rationale and notes and rationale.strip() != notes.strip():
            raise ValueError("Provide either rationale or legacy notes, not both.")
        decision_rationale = (rationale or notes or "").strip()
        inspected_evidence = (evidence_notes or "").strip()
        reviewed_quality_flags = [
            flag.strip()
            for flag in (audit_quality_flags or [])
            if flag.strip()
        ]
        supplemental_inputs = (
            additional_evidence_source_id,
            additional_evidence_page_number,
            additional_evidence_section,
            additional_evidence_excerpt,
        )
        has_supplemental_inputs = any(value is not None for value in supplemental_inputs)
        additional_supporting_evidence: AdditionalMeasurementEvidence | None = None

        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT payload FROM measurement_candidates WHERE candidate_id = ?",
                (candidate_id,),
            ).fetchone()
            if row is None:
                return None
            candidate = MeasurementCandidate.model_validate_json(row["payload"])
            target_status = {
                "approve": "approved",
                "reject": "rejected",
                "needs_more_evidence": "needs_more_evidence",
            }[decision]
            if candidate.review_status == target_status and target_status != "needs_more_evidence":
                return candidate
            if candidate.review_status in {"approved", "rejected"}:
                raise ValueError(
                    "Approved and rejected decisions are final; use review history "
                    "to inspect the prior decision."
                )
            if not decision_rationale:
                raise ValueError("A documented review rationale is required.")
            if not inspected_evidence:
                raise ValueError("Notes about the evidence inspected are required.")
            updated_classification = classification or candidate.classification
            classification_changed = updated_classification != candidate.classification
            classification_reason_text = (classification_reason or "").strip()
            if classification_changed and not classification_reason_text:
                raise ValueError(
                    "Changing a candidate classification requires an explicit reason."
                )
            if not classification_changed and classification_reason_text:
                raise ValueError(
                    "A classification reason is only valid when changing classification."
                )
            review_notes = (
                f"{decision_rationale}\n\nEvidence inspected: {inspected_evidence}"
            )
            if (
                candidate.review_status == target_status
                and candidate.classification == updated_classification
                and candidate.review_notes == review_notes
                and candidate.reviewed_by == reviewer.strip()
            ):
                return candidate

            if decision == "approve" and any(
                flag.startswith("conflicts_with_approved_measurement")
                for flag in candidate.review_flags
            ):
                if not conflict_resolution_confirmed:
                    raise ValueError(
                        "This candidate conflicts with an approved measurement. "
                        "Resolve the conflict explicitly and document the source "
                        "comparison before approval."
                    )
            if decision == "approve" and _has_approximate_reported_value(candidate):
                raise ValueError(
                    "Approximate source values cannot be approved as exact measurements."
                )
            extinction_variables = {
                "extinction diameter",
                "visible flame extinction diameter",
            }
            normalized_variable = " ".join(
                (candidate.variable or "").casefold().split()
            )
            is_extinction_diameter = normalized_variable in extinction_variables
            is_zero_extinction_diameter = (
                is_extinction_diameter and candidate.value == 0
            )
            caption_says_no_diameter = (
                "Figure_says_no_extinction_diameter_reported"
                in reviewed_quality_flags
            )
            if decision == "approve" and is_zero_extinction_diameter:
                if not zero_value_resolution_confirmed:
                    raise ValueError(
                        "A zero-valued extinction diameter requires an explicit "
                        "documented zero-value resolution."
                    )
            if decision == "approve" and (
                is_zero_extinction_diameter or caption_says_no_diameter
            ):
                if (
                    not has_supplemental_inputs
                    or not additional_evidence_review_confirmed
                ):
                    raise ValueError(
                        "This extinction-diameter conflict requires separately "
                        "cited, verified additional source evidence and explicit "
                        "confirmation that it was reviewed."
                    )
            elif decision == "approve" and has_supplemental_inputs:
                if not additional_evidence_review_confirmed:
                    raise ValueError(
                        "Additional evidence requires explicit confirmation that "
                        "the cited source was reviewed."
                    )
            elif decision == "approve" and additional_evidence_review_confirmed:
                raise ValueError(
                    "Additional evidence review confirmation requires a cited "
                    "additional source and excerpt."
                )
            if decision != "approve" and (
                has_supplemental_inputs or additional_evidence_review_confirmed
            ):
                raise ValueError(
                    "Additional approval evidence can only be attached to an "
                    "approval decision."
                )

            reviewed_at = datetime.now(timezone.utc)
            measurement_id = None
            if decision == "approve":
                non_observation_audit_classes = {
                    "derived_quantity",
                    "approximate_value",
                    "boundary_condition",
                    "initial_condition",
                    "setup_parameter",
                    "simulation_input",
                    "reported_summary",
                    "hypothetical",
                    "hypothetical_scenario",
                    "incidental",
                    "unsupported",
                }
                if audit_classification in non_observation_audit_classes:
                    raise ValueError(
                        "The source audit classifies this candidate as a derived "
                        "quantity, condition, approximate value, or non-observation; "
                        "it cannot enter the direct-observation measurements dataset."
                    )
                if (
                    audit_classification == "ambiguous"
                    and not priority_resolution_confirmed
                ):
                    raise ValueError(
                        "This priority candidate requires an explicit documented "
                        "resolution of its audit finding before approval."
                    )
                if (
                    audit_classification == "ambiguous"
                    and updated_classification != "experimental_observation"
                ):
                    raise ValueError(
                        "A priority candidate can only be approved after it is "
                        "explicitly classified as an experimental observation."
                    )
                if updated_classification != "experimental_observation":
                    raise ValueError(
                        "Only candidates classified as experimental observations can be approved."
                    )
                if not source_review_confirmed:
                    raise ValueError(
                        "Approval requires explicit confirmation that the original "
                        "source evidence was inspected."
                    )
                if (
                    candidate.variable
                    and candidate.variable.casefold().strip() == "burn time"
                    and not measurement_definition_confirmed
                ):
                    raise ValueError(
                        "Burn-time approval requires confirmation that the source's "
                        "definition and reporting convention were checked."
                    )
                if candidate.variable is None or not candidate.supporting_excerpt.strip():
                    raise ValueError(
                        "Approval requires a variable and exact supporting excerpt."
                    )
                record = connection.execute(
                    "SELECT payload FROM investigations WHERE investigation_id = ?",
                    (candidate.investigation_id,),
                ).fetchone()
                investigation = (
                    Investigation.model_validate_json(record["payload"])
                    if record
                    else None
                )
                source = next(
                    (
                        item
                        for item in investigation.sources
                        if item.source_id == candidate.source_id
                    ),
                    None,
                ) if investigation else None
                if (
                    source is None
                    or source.verification_status != "verified"
                    or source.source_type not in {"NASA_PSI", "NASA_REPORT", "NASA_DATASET"}
                    or source.sha256 is None
                    or source.sha256.casefold() != candidate.source_sha256.casefold()
                    or str(source.source_url) != str(candidate.source_url)
                    or source.document_title != candidate.document_title
                ):
                    raise ValueError(
                        "The candidate's verified source provenance no longer matches."
                    )
                source_check = validate_source_files(
                    [investigation.model_copy(update={"sources": [source]})],
                    repository_root or Path(__file__).resolve().parents[2],
                )
                if source_check:
                    raise ValueError(
                        "The original source file failed verification: "
                        + source_check[0].message
                    )
                if has_supplemental_inputs:
                    if (
                        not additional_evidence_source_id
                        or not additional_evidence_excerpt
                        or not additional_evidence_excerpt.strip()
                    ):
                        raise ValueError(
                            "Additional evidence requires a source ID and a "
                            "supporting excerpt."
                        )
                    if (
                        additional_evidence_page_number is None
                        and not (additional_evidence_section or "").strip()
                    ):
                        raise ValueError(
                            "Additional evidence requires a source page number "
                            "or section reference."
                        )
                    if additional_evidence_source_id == candidate.source_id:
                        raise ValueError(
                            "Additional evidence must come from a different "
                            "verified source than the conflicting Table IX source."
                        )
                    additional_source = next(
                        (
                            item
                            for item in investigation.sources
                            if item.source_id == additional_evidence_source_id
                        ),
                        None,
                    )
                    if (
                        additional_source is None
                        or additional_source.verification_status != "verified"
                        or additional_source.source_type
                        not in {"NASA_PSI", "NASA_REPORT", "NASA_DATASET"}
                        or additional_source.sha256 is None
                    ):
                        raise ValueError(
                            "Additional evidence must reference a verified NASA "
                            "source attached to this investigation."
                        )
                    if (
                        additional_source.sha256.casefold()
                        == candidate.source_sha256.casefold()
                    ):
                        raise ValueError(
                            "Additional evidence must come from a different "
                            "verified source document."
                        )
                    additional_check = validate_source_files(
                        [
                            investigation.model_copy(
                                update={"sources": [additional_source]}
                            )
                        ],
                        repository_root or Path(__file__).resolve().parents[2],
                    )
                    if additional_check:
                        raise ValueError(
                            "The additional evidence source failed verification: "
                            + additional_check[0].message
                        )
                    additional_supporting_evidence = AdditionalMeasurementEvidence(
                        source_id=additional_source.source_id,
                        document_title=additional_source.document_title,
                        source_url=additional_source.source_url,
                        source_sha256=additional_source.sha256,
                        page_number=additional_evidence_page_number,
                        section=additional_evidence_section,
                        supporting_excerpt=additional_evidence_excerpt.strip(),
                    )

                measurement_id = "measurement-" + candidate.candidate_id.removeprefix(
                    "candidate-"
                )
                measurement = Measurement(
                    measurement_id=measurement_id,
                    investigation_id=candidate.investigation_id,
                    variable=candidate.variable,
                    value=candidate.value,
                    reported_value=candidate.reported_value,
                    unit=candidate.unit,
                    source_id=candidate.source_id,
                    observation_context=candidate.observation_context,
                    page_number=candidate.page_number,
                    section=candidate.section,
                    table_reference=candidate.table_reference,
                    supporting_excerpt=candidate.supporting_excerpt,
                    extraction_method=candidate.extraction_method,
                    confidence=candidate.confidence,
                    reviewed_by=reviewer.strip(),
                    reviewed_at=reviewed_at,
                    review_notes=review_notes,
                )
                existing = connection.execute(
                    "SELECT payload FROM measurements WHERE measurement_id = ?",
                    (measurement_id,),
                ).fetchone()
                if existing and (
                    Measurement.model_validate_json(existing["payload"]) != measurement
                ):
                    raise ValueError(
                        "Measurement ID already exists with different source data."
                    )
                connection.execute(
                    "INSERT OR IGNORE INTO measurements"
                    "(measurement_id, investigation_id, variable, payload) "
                    "VALUES (?, ?, ?, ?)",
                    (
                        measurement.measurement_id,
                        measurement.investigation_id,
                        measurement.variable,
                        measurement.model_dump_json(),
                    ),
                )

            updated = MeasurementCandidate.model_validate(
                {
                    **candidate.model_dump(),
                    "classification": updated_classification,
                    "review_status": target_status,
                    "reviewed_by": reviewer.strip(),
                    "reviewed_at": reviewed_at,
                    "review_notes": review_notes,
                    "measurement_id": measurement_id,
                }
            )
            connection.execute(
                "UPDATE measurement_candidates "
                "SET review_status = ?, payload = ? WHERE candidate_id = ?",
                (
                    updated.review_status,
                    updated.model_dump_json(),
                    updated.candidate_id,
                ),
            )
            context_reference = candidate.observation_context.get(
                "test", candidate.observation_context.get("run")
            )
            event = MeasurementReviewEvent(
                review_event_id=f"review-{uuid4().hex}",
                candidate_id=candidate.candidate_id,
                reviewer=reviewer.strip(),
                decision=decision,
                previous_status=candidate.review_status,
                new_status=target_status,
                previous_classification=candidate.classification,
                new_classification=updated_classification,
                classification_reason=(
                    classification_reason_text if classification_changed else None
                ),
                reviewed_at=reviewed_at,
                rationale=decision_rationale,
                evidence_notes=inspected_evidence,
                source_review_confirmed=source_review_confirmed,
                measurement_definition_confirmed=measurement_definition_confirmed,
                priority_finding=audit_rationale,
                audit_classification=audit_classification,
                audit_quality_flags=reviewed_quality_flags,
                figure_reference=figure_reference,
                figure_caption_excerpt=figure_caption_excerpt,
                priority_resolution_confirmed=priority_resolution_confirmed,
                conflict_resolution_confirmed=conflict_resolution_confirmed,
                zero_value_resolution_confirmed=zero_value_resolution_confirmed,
                additional_evidence_review_confirmed=additional_evidence_review_confirmed,
                additional_supporting_evidence=additional_supporting_evidence,
                source_id=candidate.source_id,
                source_url=candidate.source_url,
                document_title=candidate.document_title,
                source_sha256=candidate.source_sha256,
                page_number=candidate.page_number,
                section=candidate.section,
                table_reference=candidate.table_reference,
                row_reference=(
                    str(context_reference) if context_reference is not None else None
                ),
                supporting_excerpt=candidate.supporting_excerpt,
            )
            connection.execute(
                "INSERT INTO measurement_review_history"
                "(review_event_id, candidate_id, reviewed_at, payload) "
                "VALUES (?, ?, ?, ?)",
                (
                    event.review_event_id,
                    event.candidate_id,
                    event.reviewed_at.isoformat(),
                    event.model_dump_json(),
                ),
            )
        return updated

    def search_evidence(
        self,
        query: str,
        investigation_ids: list[str] | None = None,
        research_area: str | None = None,
        limit: int = 8,
    ) -> list[EvidenceHit]:
        terms = [
            term
            for term in dict.fromkeys(re.findall(r"[a-z0-9]{2,}", query.casefold()))
            if term not in _SEARCH_STOPWORDS
        ][:12]
        if not terms or investigation_ids == []:
            return []
        clauses = []
        parameters: list[object] = []
        if investigation_ids is not None:
            placeholders = ",".join("?" for _ in investigation_ids)
            clauses.append(f"evidence_excerpts.investigation_id IN ({placeholders})")
            parameters.extend(investigation_ids)
        if research_area is not None:
            clauses.append(
                "json_extract(investigations.payload, '$.research_area') = ?"
            )
            parameters.append(research_area)
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT evidence_excerpts.payload FROM evidence_excerpts "
                "JOIN investigations USING (investigation_id) "
                + ("WHERE " + " AND ".join(clauses) if clauses else ""),
                parameters,
            ).fetchall()
        excerpts = [
            EvidenceExcerpt.model_validate_json(row["payload"]) for row in rows
        ]
        ranked = [
            excerpt
            for excerpt in sorted(
                excerpts,
                key=lambda item: _semantic_similarity(query, item.excerpt),
                reverse=True,
            )
            if _semantic_similarity(query, excerpt.excerpt) > 0
        ][:limit]
        investigations = self.get_investigations(
            list(dict.fromkeys(item.investigation_id for item in ranked))
        )
        by_id = {item.investigation_id: item for item in investigations}
        hits: list[EvidenceHit] = []
        for excerpt in ranked:
            investigation = by_id.get(excerpt.investigation_id)
            if investigation is None:
                continue
            source = next(
                (
                    source
                    for source in investigation.sources
                    if source.source_id == excerpt.source_id
                ),
                None,
            )
            if source is None:
                continue
            hits.append(EvidenceHit(excerpt, investigation, source))
        return hits

    def save_scenario_analysis(self, analysis: ScenarioAnalysisResponse) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO scenario_analyses(scenario_id, payload) VALUES (?, ?) "
                "ON CONFLICT(scenario_id) DO UPDATE SET payload = excluded.payload",
                (analysis.scenario_id, analysis.model_dump_json()),
            )

    def get_scenario_analysis(
        self, scenario_id: str
    ) -> ScenarioAnalysisResponse | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM scenario_analyses WHERE scenario_id = ?",
                (scenario_id,),
            ).fetchone()
        return ScenarioAnalysisResponse.model_validate_json(row["payload"]) if row else None

    def import_records(
        self,
        investigations: list[Investigation],
        measurements: list[Measurement],
        replace: bool = False,
        evidence_excerpts: list[EvidenceExcerpt] | None = None,
    ) -> None:
        evidence_excerpts = evidence_excerpts or []
        investigation_ids = {item.investigation_id for item in investigations}
        if len(investigation_ids) != len(investigations):
            raise ValueError("Investigation IDs in the import must be unique.")
        if any(not item.sources for item in investigations):
            raise ValueError("Every imported investigation must include at least one source.")
        measurement_ids = {item.measurement_id for item in measurements}
        if len(measurement_ids) != len(measurements):
            raise ValueError("Measurement IDs in the import must be unique.")
        excerpt_ids = {item.excerpt_id for item in evidence_excerpts}
        if len(excerpt_ids) != len(evidence_excerpts):
            raise ValueError("Evidence excerpt IDs in the import must be unique.")
        known_ids = investigation_ids
        if not replace:
            existing, _ = self.list_investigations(page_size=1_000_000)
            known_ids.update(item.investigation_id for item in existing)
        sources = {
            (item.investigation_id, source.source_id)
            for item in investigations
            for source in item.sources
        }
        if not replace:
            sources.update(
                (item.investigation_id, source.source_id)
                for item in existing
                for source in item.sources
            )
        if any(item.investigation_id not in known_ids for item in measurements):
            raise ValueError("Every measurement must reference an imported investigation.")
        if any(
            (item.investigation_id, item.source_id) not in sources
            for item in measurements
        ):
            raise ValueError("Every measurement must cite a source for its investigation.")
        if any(item.investigation_id not in known_ids for item in evidence_excerpts):
            raise ValueError("Every evidence excerpt must reference an indexed investigation.")
        if any(
            (item.investigation_id, item.source_id) not in sources
            for item in evidence_excerpts
        ):
            raise ValueError("Every evidence excerpt must cite a source for its investigation.")

        with self._connect() as connection:
            if replace:
                connection.execute("DELETE FROM scenario_analyses")
                connection.execute("DELETE FROM evidence_excerpts")
                connection.execute("DELETE FROM measurement_candidates")
                connection.execute("DELETE FROM measurements")
                connection.execute("DELETE FROM investigations")
            connection.executemany(
                "INSERT INTO investigations(investigation_id, payload) VALUES (?, ?) "
                "ON CONFLICT(investigation_id) DO UPDATE SET payload = excluded.payload",
                [
                    (item.investigation_id, item.model_dump_json())
                    for item in investigations
                ],
            )
            connection.executemany(
                "INSERT INTO measurements"
                "(measurement_id, investigation_id, variable, payload) "
                "VALUES (?, ?, ?, ?) ON CONFLICT(measurement_id) DO UPDATE SET "
                "investigation_id = excluded.investigation_id, "
                "variable = excluded.variable, payload = excluded.payload",
                [
                    (
                        item.measurement_id,
                        item.investigation_id,
                        item.variable,
                        item.model_dump_json(),
                    )
                    for item in measurements
                ],
            )
            connection.executemany(
                "INSERT INTO evidence_excerpts"
                "(excerpt_id, investigation_id, source_id, payload) "
                "VALUES (?, ?, ?, ?) ON CONFLICT(excerpt_id) DO UPDATE SET "
                "investigation_id = excluded.investigation_id, "
                "source_id = excluded.source_id, payload = excluded.payload",
                [
                    (
                        item.excerpt_id,
                        item.investigation_id,
                        item.source_id,
                        item.model_dump_json(),
                    )
                    for item in evidence_excerpts
                ],
            )

    def replace_evidence_index(self, evidence_excerpts: list[EvidenceExcerpt]) -> None:
        """Replace only the derived document index; canonical records remain unchanged."""
        investigations, _ = self.list_investigations(page_size=1_000_000)
        known_ids = {item.investigation_id for item in investigations}
        sources = {
            (item.investigation_id, source.source_id)
            for item in investigations
            for source in item.sources
        }
        if any(item.investigation_id not in known_ids for item in evidence_excerpts):
            raise ValueError("Every evidence excerpt must reference an indexed investigation.")
        if any(
            (item.investigation_id, item.source_id) not in sources
            for item in evidence_excerpts
        ):
            raise ValueError("Every evidence excerpt must cite a source for its investigation.")
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM evidence_excerpts WHERE excerpt_id LIKE 'excerpt-%'"
            )
            connection.executemany(
                "INSERT INTO evidence_excerpts"
                "(excerpt_id, investigation_id, source_id, payload) VALUES (?, ?, ?, ?)",
                [
                    (
                        item.excerpt_id,
                        item.investigation_id,
                        item.source_id,
                        item.model_dump_json(),
                    )
                    for item in evidence_excerpts
                ],
            )


def load_import_file(
    path: str | Path,
) -> tuple[list[Investigation], list[Measurement], list[EvidenceExcerpt]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) - {
        "investigations",
        "measurements",
        "evidence_excerpts",
    }:
        raise ValueError(
            "Import file must contain only investigations, measurements, and evidence_excerpts."
        )
    if any(
        not isinstance(data.get(field, []), list)
        for field in ("investigations", "measurements", "evidence_excerpts")
    ):
        raise ValueError("Import fields must be JSON arrays.")
    investigations = [
        Investigation.model_validate(item) for item in data.get("investigations", [])
    ]
    measurements = [
        Measurement.model_validate(item) for item in data.get("measurements", [])
    ]
    evidence_excerpts = [
        EvidenceExcerpt.model_validate(item)
        for item in data.get("evidence_excerpts", [])
    ]
    return investigations, measurements, evidence_excerpts
