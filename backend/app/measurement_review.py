from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any

from app.measurement_extraction import (
    extract_measurement_candidates,
    reconcile_approved_measurement_duplicates,
)
from app.models import MeasurementCandidate, MeasurementCandidateClassification
from app.store import SQLiteStore


_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_CLASSIFICATIONS = (
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
)
_AUDIT_CLASSIFICATIONS = (
    "experimental_observation",
    "derived_quantity",
    "approximate_value",
    "boundary_condition",
    "initial_condition",
    "setup_parameter",
    "simulation_input",
    "reported_summary",
    "hypothetical_scenario",
    "ambiguous",
    "unsupported",
)
_CLASSIFICATION_BY_NAME: dict[str, MeasurementCandidateClassification] = {
    item: item for item in _CLASSIFICATIONS
}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Extract source-backed measurement candidates and review them before "
            "they enter the measurements API."
        )
    )
    parser.add_argument("--database", help="SQLite database path; defaults to FLARE_DATABASE_PATH.")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser(
        "scan",
        help="Scan verified source documents and idempotently stage candidates.",
    )
    listing = commands.add_parser("list", help="List staged candidates.")
    listing.add_argument(
        "--status",
        choices=(
            "pending_review",
            "needs_more_evidence",
            "approved",
            "rejected",
        ),
        help="Filter by review status.",
    )
    listing.add_argument("--classification", choices=_CLASSIFICATIONS)
    listing.add_argument("--source-id")
    listing.add_argument("--investigation-id")
    listing.add_argument("--variable")
    listing.add_argument("--audit-classification", choices=_AUDIT_CLASSIFICATIONS)
    listing.add_argument(
        "--priority",
        action="store_true",
        help="Limit results to the 28 ambiguous candidates in the latest Table IX audit.",
    )

    show = commands.add_parser(
        "show", help="Display one candidate and its complete provenance."
    )
    show.add_argument("candidate_id")

    review = commands.add_parser("review", help="Approve or reject one staged candidate.")
    review.add_argument("candidate_id")
    review.add_argument(
        "--decision",
        choices=("approve", "reject", "needs-more-evidence"),
        required=True,
    )
    review.add_argument("--reviewer", required=True)
    review.add_argument("--classification", choices=_CLASSIFICATIONS)
    review.add_argument(
        "--classification-reason",
        help="Required when changing the candidate's scientific classification.",
    )
    review.add_argument(
        "--rationale",
        "--notes",
        dest="rationale",
        required=True,
        help="Document the reason for this review decision.",
    )
    review.add_argument(
        "--evidence-notes",
        required=True,
        help="Record the source evidence inspected and any relevant limitations.",
    )
    review.add_argument(
        "--confirm-source-review",
        action="store_true",
        help="Confirm that the original cited document and excerpt were checked.",
    )
    review.add_argument(
        "--confirm-measurement-definition",
        action="store_true",
        help="For burn time, confirm the source definition and reporting convention were checked.",
    )
    review.add_argument(
        "--resolve-priority",
        action="store_true",
        help="Confirm that the Table IX audit finding for this priority candidate was resolved.",
    )
    review.add_argument(
        "--resolve-conflict",
        action="store_true",
        help="Confirm that a conflict with an already approved observation was explicitly resolved.",
    )
    review.add_argument(
        "--resolve-zero-extinction-diameter",
        action="store_true",
        help="Confirm the source convention for a zero-valued extinction diameter was resolved.",
    )
    review.add_argument(
        "--additional-evidence-source-id",
        help="Verified NASA source ID supporting a no-diameter or zero-value resolution.",
    )
    review.add_argument("--additional-evidence-page-number", type=int)
    review.add_argument("--additional-evidence-section")
    review.add_argument("--additional-evidence-excerpt")
    review.add_argument(
        "--confirm-additional-evidence-review",
        action="store_true",
        help="Confirm that the cited additional source evidence was inspected.",
    )
    history = commands.add_parser(
        "history", help="Display append-only review decisions for one candidate."
    )
    history.add_argument("candidate_id")
    correct_reviewers = commands.add_parser(
        "correct-reviewer-placeholders",
        help="Clear placeholder reviewer labels without changing approval status.",
    )
    correct_reviewers.add_argument(
        "--confirm-reviewer-attribution-unknown",
        action="store_true",
        help="Confirm the original reviewer cannot be established.",
    )
    return parser


def _read_audit_records() -> dict[str, dict[str, str]]:
    path = _REPOSITORY_ROOT / "data/reports/table_ix_review_audit.csv"
    if not path.is_file():
        return {}
    records: dict[str, dict[str, str]] = {}
    with path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            candidate_id = row.get("candidate_id", "")
            if not candidate_id:
                raise ValueError(f"Audit CSV contains a row without candidate_id: {path}")
            if candidate_id in records:
                raise ValueError(f"Audit CSV contains duplicate candidate ID: {candidate_id}")
            records[candidate_id] = row
    return records


def _validated_audit_record(
    candidate: MeasurementCandidate,
    audit_records: dict[str, dict[str, str]],
) -> dict[str, str] | None:
    record = audit_records.get(candidate.candidate_id)
    if record is None:
        return None
    for field, candidate_value in (
        ("source_id", candidate.source_id),
        ("source_sha256", candidate.source_sha256),
        ("source_url", str(candidate.source_url)),
        ("document_title", candidate.document_title),
        ("investigation_id", candidate.investigation_id),
        ("reported_value", candidate.reported_value),
        ("unit", candidate.unit),
        ("pdf_page_number", str(candidate.page_number or "")),
        ("table_reference", candidate.table_reference or ""),
    ):
        if record.get(field) != str(candidate_value):
            raise ValueError(
                f"Table IX audit provenance does not match candidate "
                f"{candidate.candidate_id} ({field})."
            )
    if record.get("source_hash_verification_status") != (
        "verified; SHA-256 matches source_manifest.json"
    ):
        raise ValueError(
            f"Table IX audit source hash is not verified for candidate "
            f"{candidate.candidate_id}."
        )
    return record


def _audit_quality_flags(record: dict[str, str] | None) -> list[str]:
    if record is None:
        return []
    return [
        flag.strip()
        for flag in record.get("quality_flags", "").split(";")
        if flag.strip()
    ]


def _context_run_number(context: dict[str, Any]) -> str | None:
    for key in ("test", "run"):
        value = context.get(key)
        if isinstance(value, str):
            match = re.search(r"(\d+)\s*$", value)
            if match:
                return match.group(1).lstrip("0") or "0"
    return None


def _run_number(candidate: MeasurementCandidate) -> str | None:
    return _context_run_number(candidate.observation_context)


def _canonical_variable(variable: str) -> str:
    normalized = " ".join(variable.casefold().split())
    return (
        "extinction diameter"
        if normalized == "visible flame extinction diameter"
        else normalized
    )


def _related_approved_measurements(
    candidate: MeasurementCandidate, store: SQLiteStore
) -> list[dict[str, Any]]:
    candidate_run = _run_number(candidate)
    if candidate_run is None or candidate.variable is None:
        return []
    investigation = store.get_investigation(candidate.investigation_id)
    if investigation is None:
        return []
    sources = {source.source_id: source for source in investigation.sources}
    related: list[dict[str, Any]] = []
    for measurement in store.measurements(candidate.investigation_id):
        if (
            _canonical_variable(measurement.variable)
            != _canonical_variable(candidate.variable)
            or _context_run_number(measurement.observation_context) != candidate_run
        ):
            continue
        source = sources.get(measurement.source_id)
        if (
            source is None
            or source.verification_status != "verified"
            or source.source_type not in {"NASA_PSI", "NASA_REPORT", "NASA_DATASET"}
        ):
            continue
        related.append(
            {
                **measurement.model_dump(mode="json"),
                "document_title": source.document_title,
                "source_url": str(source.source_url),
                "conflict_warning": (
                    "This previously approved source reports a different value; "
                    "the source-reported values must remain separate."
                    if measurement.reported_value != candidate.reported_value
                    or measurement.unit != candidate.unit
                    else None
                ),
            }
        )
    return related


def main(argv: list[str] | None = None) -> None:
    parser = _parser()
    args = parser.parse_args(argv)
    store = SQLiteStore(args.database)

    if args.command == "scan":
        investigations, _ = store.list_investigations(page_size=1_000_000)
        candidates, report = extract_measurement_candidates(
            investigations, _REPOSITORY_ROOT
        )
        candidates, suppressed = reconcile_approved_measurement_duplicates(
            candidates, store.measurements()
        )
        report.duplicate_candidates_suppressed.extend(suppressed)
        if suppressed:
            report.reject(
                "duplicate_candidate_of_approved_measurement", len(suppressed)
            )
        staged_count = store.stage_measurement_candidates(candidates)
        print(json.dumps(report.as_dict(candidates, staged_count), indent=2))
        return

    if args.command == "list":
        candidates = store.measurement_candidates(args.status)
        audit_records: dict[str, dict[str, str]] = {}
        if args.priority or args.audit_classification is not None:
            try:
                audit_records = _read_audit_records()
            except ValueError as exc:
                parser.error(str(exc))
            if not audit_records and args.priority:
                parser.error("The Table IX candidate audit CSV is unavailable.")
            if not audit_records and args.audit_classification is not None:
                parser.error("The Table IX candidate audit CSV is unavailable.")
        if args.priority:
            candidates = [
                candidate
                for candidate in candidates
                if (
                    record := _validated_audit_record(candidate, audit_records)
                ) is not None
                and record.get("audit_classification") == "ambiguous"
            ]
        if args.classification is not None:
            candidates = [
                candidate
                for candidate in candidates
                if candidate.classification == args.classification
            ]
        if args.source_id is not None:
            candidates = [
                candidate
                for candidate in candidates
                if candidate.source_id == args.source_id
            ]
        if args.investigation_id is not None:
            candidates = [
                candidate
                for candidate in candidates
                if candidate.investigation_id == args.investigation_id
            ]
        if args.variable is not None:
            candidates = [
                candidate
                for candidate in candidates
                if candidate.variable
                and candidate.variable.casefold() == args.variable.casefold()
            ]
        if args.audit_classification is not None:
            candidates = [
                candidate
                for candidate in candidates
                if (
                    record := _validated_audit_record(candidate, audit_records)
                ) is not None
                and record.get("audit_classification")
                == args.audit_classification
            ]
        if args.priority:
            payload: list[dict[str, Any]] = []
            for candidate in candidates:
                audit = _validated_audit_record(candidate, audit_records)
                payload.append(
                    {
                        "candidate": candidate.model_dump(mode="json"),
                        "priority_review": audit,
                    }
                )
        else:
            payload = [item.model_dump(mode="json") for item in candidates]
        print(json.dumps(payload, indent=2))
        return

    if args.command == "show":
        candidate = store.measurement_candidate(args.candidate_id)
        if candidate is None:
            parser.error(f"Candidate not found: {args.candidate_id}")
        try:
            audit_record = _validated_audit_record(candidate, _read_audit_records())
        except ValueError as exc:
            parser.error(str(exc))
        history = store.measurement_review_history(candidate.candidate_id)
        print(
            json.dumps(
                {
                    "candidate": candidate.model_dump(mode="json"),
                    "priority_review": audit_record,
                    "related_approved_measurements": _related_approved_measurements(
                        candidate, store
                    ),
                    "review_history": [
                        event.model_dump(mode="json") for event in history
                    ],
                    "history_notice": (
                        None
                        if history or candidate.review_status == "pending_review"
                        else "This pre-history decision has no reconstructable event; "
                        "reviewer identity and evidence notes were not inferred."
                    ),
                },
                indent=2,
            )
        )
        return

    if args.command == "history":
        candidate = store.measurement_candidate(args.candidate_id)
        if candidate is None:
            parser.error(f"Candidate not found: {args.candidate_id}")
        history = store.measurement_review_history(candidate.candidate_id)
        print(
            json.dumps(
                {
                    "candidate_id": candidate.candidate_id,
                    "review_history": [
                        event.model_dump(mode="json") for event in history
                    ],
                    "history_notice": (
                        None
                        if history or candidate.review_status == "pending_review"
                        else "This pre-history decision has no reconstructable event; "
                        "reviewer identity and evidence notes were not inferred."
                    ),
                },
                indent=2,
            )
        )
        return

    if args.command == "review":
        candidate = store.measurement_candidate(args.candidate_id)
        if candidate is None:
            parser.error(f"Candidate not found: {args.candidate_id}")
        try:
            audit_record = _validated_audit_record(candidate, _read_audit_records())
        except ValueError as exc:
            parser.error(str(exc))
        try:
            candidate = store.review_measurement_candidate(
                args.candidate_id,
                args.decision.replace("-", "_"),
                args.reviewer,
                classification=(
                    _CLASSIFICATION_BY_NAME.get(args.classification)
                    if args.classification is not None
                    else None
                ),
                classification_reason=args.classification_reason,
                rationale=args.rationale,
                evidence_notes=args.evidence_notes,
                source_review_confirmed=args.confirm_source_review,
                measurement_definition_confirmed=(
                    args.confirm_measurement_definition
                ),
                priority_resolution_confirmed=args.resolve_priority,
                conflict_resolution_confirmed=args.resolve_conflict,
                audit_classification=(
                    audit_record.get("audit_classification")
                    if audit_record
                    else None
                ),
                audit_rationale=(
                    audit_record.get("audit_rationale") if audit_record else None
                ),
                audit_quality_flags=_audit_quality_flags(audit_record),
                figure_reference=(
                    audit_record.get("figure_reference") if audit_record else None
                ),
                figure_caption_excerpt=(
                    audit_record.get("figure_caption_excerpt")
                    if audit_record
                    else None
                ),
                repository_root=_REPOSITORY_ROOT,
                zero_value_resolution_confirmed=(
                    args.resolve_zero_extinction_diameter
                ),
                additional_evidence_source_id=args.additional_evidence_source_id,
                additional_evidence_page_number=args.additional_evidence_page_number,
                additional_evidence_section=args.additional_evidence_section,
                additional_evidence_excerpt=args.additional_evidence_excerpt,
                additional_evidence_review_confirmed=(
                    args.confirm_additional_evidence_review
                ),
            )
        except ValueError as exc:
            parser.error(str(exc))
        if candidate is None:
            parser.error(f"Candidate not found: {args.candidate_id}")
        print(json.dumps(candidate.model_dump(mode="json"), indent=2))
        return

    if args.command == "correct-reviewer-placeholders":
        if not args.confirm_reviewer_attribution_unknown:
            parser.error(
                "This correction requires --confirm-reviewer-attribution-unknown."
            )
        corrected = store.correct_placeholder_reviewer_attributions()
        print(json.dumps({"corrected": corrected, "count": len(corrected)}, indent=2))


if __name__ == "__main__":
    main()
