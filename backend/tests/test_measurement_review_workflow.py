from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pytest
from pypdf import PdfWriter

import app.measurement_review as measurement_review
from app.measurement_review import main as measurement_review_main
from app.models import (
    Investigation,
    Measurement,
    MeasurementCandidate,
    MeasurementCandidateClassification,
    Source,
)
from app.store import SQLiteStore


def _verified_source(directory: Path, source_id: str = "test-source") -> Source:
    path = directory / f"{source_id}.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.add_metadata({"/Title": f"TEST FIXTURE — {source_id}"})
    with path.open("wb") as stream:
        writer.write(stream)
    content = path.read_bytes()
    return Source(
        source_id=source_id,
        document_title=f"TEST FIXTURE — {source_id}",
        source_url=f"https://ntrs.nasa.gov/test-fixture/{source_id}",
        source_type="NASA_REPORT",
        local_file_path=path.name,
        sha256=hashlib.sha256(content).hexdigest(),
        file_size_bytes=len(content),
        mime_type="application/pdf",
        downloaded_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        last_verified_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
        verification_status="verified",
    )


def _candidate(
    source: Source,
    *,
    candidate_id: str = "candidate-test-review",
    classification: MeasurementCandidateClassification = "experimental_observation",
    variable: str = "extinction diameter",
    reported_value: str = "1.11",
    value: float = 1.11,
    unit: str = "mm",
) -> MeasurementCandidate:
    return MeasurementCandidate(
        candidate_id=candidate_id,
        investigation_id="test-only-review-investigation",
        source_id=source.source_id,
        document_title=source.document_title,
        source_url=source.source_url,
        source_sha256=source.sha256,
        variable=variable,
        reported_value=reported_value,
        value=value,
        unit=unit,
        observation_context={"test": "FLEX–204"},
        page_number=31,
        section="A.2 Experiment Results",
        table_reference="Table IX",
        supporting_excerpt="TEST FIXTURE: FLEX–204 reports 1.11 mm.",
        extraction_method="pdf_table_text",
        confidence=0.98,
        classification=classification,
    )


def _review_args(**overrides):
    return {
        "rationale": "TEST FIXTURE: decision based on reviewed source evidence.",
        "evidence_notes": "TEST FIXTURE: checked the cited page, row, and excerpt.",
        **overrides,
    }


def _write_audit_csv(
    root: Path,
    candidate: MeasurementCandidate,
    *,
    quality_flags: str = "TEST FIXTURE: source conflict",
    figure_reference: str = "TEST FIXTURE: Figure 207",
    figure_caption_excerpt: str = "TEST FIXTURE: conflicting source note.",
) -> None:
    path = root / "data/reports/table_ix_review_audit.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "candidate_id": candidate.candidate_id,
        "investigation_id": candidate.investigation_id,
        "source_id": candidate.source_id,
        "source_url": str(candidate.source_url),
        "source_sha256": candidate.source_sha256,
        "source_hash_verification_status": "verified; SHA-256 matches source_manifest.json",
        "reported_value": candidate.reported_value,
        "unit": candidate.unit,
        "audit_classification": "ambiguous",
        "audit_rationale": "TEST FIXTURE: conflicting source-reported values.",
        "document_title": candidate.document_title,
        "pdf_page_number": str(candidate.page_number),
        "table_reference": candidate.table_reference or "",
        "test_id": "FLEX–204",
        "table_row_excerpt": candidate.supporting_excerpt,
        "figure_reference": figure_reference,
        "figure_caption_excerpt": figure_caption_excerpt,
        "quality_flags": quality_flags,
    }
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(record))
        writer.writeheader()
        writer.writerow(record)


def _setup(
    tmp_path: Path,
    *,
    classification: MeasurementCandidateClassification = "experimental_observation",
):
    source = _verified_source(tmp_path)
    candidate = _candidate(source, classification=classification)
    investigation = Investigation(
        investigation_id=candidate.investigation_id,
        title="TEST FIXTURE — review investigation",
        research_area="fundamentals",
        sources=[source],
    )
    store = SQLiteStore(tmp_path / "review.sqlite3")
    store.import_records([investigation], [])
    store.stage_measurement_candidates([candidate])
    return store, candidate, investigation, source


def test_priority_queue_and_candidate_detail_include_audit_and_approved_conflict(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    store, candidate, investigation, source = _setup(tmp_path)
    earlier_source = _verified_source(tmp_path, "earlier-nasa-report")
    updated_investigation = investigation.model_copy(
        update={"sources": [source, earlier_source]}
    )
    store.import_records([updated_investigation], [])
    store.import_records(
        [],
        [
            Measurement(
                measurement_id="measurement-existing-run-204",
                investigation_id=candidate.investigation_id,
                variable="extinction diameter",
                value=1.1,
                reported_value="1.10",
                unit="mm",
                source_id=earlier_source.source_id,
                observation_context={"run": "#204"},
                page_number=5,
                section="3.1 Results",
                supporting_excerpt="TEST FIXTURE: Run #204 measured 1.10 mm.",
            )
        ],
    )
    _write_audit_csv(tmp_path, candidate)
    monkeypatch.setattr(measurement_review, "_REPOSITORY_ROOT", tmp_path)

    measurement_review_main(
        [
            "--database",
            str(store.database_path),
            "list",
            "--priority",
            "--status",
            "pending_review",
            "--source-id",
            candidate.source_id,
            "--investigation-id",
            candidate.investigation_id,
            "--variable",
            candidate.variable,
            "--audit-classification",
            "ambiguous",
        ]
    )
    priority = json.loads(capsys.readouterr().out)
    assert len(priority) == 1
    assert priority[0]["candidate"]["candidate_id"] == candidate.candidate_id
    assert priority[0]["priority_review"]["audit_rationale"].startswith(
        "TEST FIXTURE:"
    )
    assert priority[0]["priority_review"]["figure_reference"] == "TEST FIXTURE: Figure 207"

    measurement_review_main(
        ["--database", str(store.database_path), "show", candidate.candidate_id]
    )
    detail = json.loads(capsys.readouterr().out)
    assert detail["candidate"]["reported_value"] == "1.11"
    assert detail["priority_review"]["source_url"] == str(source.source_url)
    assert detail["related_approved_measurements"][0]["reported_value"] == "1.10"
    assert (
        detail["related_approved_measurements"][0]["source_url"]
        == str(earlier_source.source_url)
    )
    assert detail["related_approved_measurements"][0]["conflict_warning"]


def test_review_requires_source_confirmation_and_keeps_unreviewed_candidate_out(
    tmp_path: Path,
) -> None:
    store, candidate, _, _ = _setup(tmp_path)

    with pytest.raises(ValueError, match="original source evidence was inspected"):
        store.review_measurement_candidate(
            candidate.candidate_id,
            "approve",
            "Actual Reviewer",
            **_review_args(),
            repository_root=tmp_path,
        )

    assert store.measurement_candidate(candidate.candidate_id).review_status == "pending_review"
    assert store.measurements() == []
    assert store.measurement_review_history(candidate.candidate_id) == []


def test_needs_evidence_then_approval_appends_review_history(
    tmp_path: Path, capsys
) -> None:
    store, candidate, _, _ = _setup(tmp_path)

    first = store.review_measurement_candidate(
        candidate.candidate_id,
        "needs_more_evidence",
        "Actual Reviewer",
        **_review_args(
            evidence_notes="TEST FIXTURE: source row checked; figure context still needed."
        ),
    )
    assert first.review_status == "needs_more_evidence"
    assert store.measurements() == []

    measurement_review_main(
        [
            "--database",
            str(store.database_path),
            "list",
            "--status",
            "needs_more_evidence",
        ]
    )
    list_output = json.loads(capsys.readouterr().out)
    assert [item["candidate_id"] for item in list_output] == [
        candidate.candidate_id
    ]

    measurement_review_main(
        [
            "--database",
            str(store.database_path),
            "history",
            candidate.candidate_id,
        ]
    )
    history_output = json.loads(capsys.readouterr().out)
    assert history_output["review_history"][0]["decision"] == "needs_more_evidence"

    approved = store.review_measurement_candidate(
        candidate.candidate_id,
        "approve",
        "Actual Reviewer",
        source_review_confirmed=True,
        **_review_args(
            evidence_notes="TEST FIXTURE: original source page and supporting figure checked."
        ),
        repository_root=tmp_path,
    )
    history = store.measurement_review_history(candidate.candidate_id)
    assert approved.review_status == "approved"
    assert len(history) == 2
    assert [event.decision for event in history] == [
        "needs_more_evidence",
        "approve",
    ]
    assert history[0].previous_status == "pending_review"
    assert history[1].previous_status == "needs_more_evidence"
    assert history[1].reviewer == "Actual Reviewer"
    assert history[1].source_sha256 == candidate.source_sha256
    assert history[1].page_number == candidate.page_number
    assert history[1].table_reference == "Table IX"
    assert history[1].row_reference == "FLEX–204"
    assert history[1].supporting_excerpt == candidate.supporting_excerpt


def test_review_cli_requires_source_confirmation_and_uses_supplied_reviewer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    store, candidate, _, _ = _setup(tmp_path)
    monkeypatch.setattr(measurement_review, "_REPOSITORY_ROOT", tmp_path)
    base_args = [
        "--database",
        str(store.database_path),
        "review",
        candidate.candidate_id,
        "--decision",
        "approve",
        "--reviewer",
        "Actual Reviewer",
        "--rationale",
        "TEST FIXTURE: approve after checking the original source.",
        "--evidence-notes",
        "TEST FIXTURE: checked the page, row, and exact reported value.",
    ]

    with pytest.raises(SystemExit):
        measurement_review_main(base_args)
    assert store.measurement_candidate(candidate.candidate_id).review_status == "pending_review"

    measurement_review_main([*base_args, "--confirm-source-review"])
    result = json.loads(capsys.readouterr().out)
    assert result["review_status"] == "approved"
    assert result["reviewed_by"] == "Actual Reviewer"
    assert store.measurement_review_history(candidate.candidate_id)[0].reviewer == "Actual Reviewer"


def test_classification_change_requires_reason_and_is_recorded(
    tmp_path: Path,
) -> None:
    store, candidate, _, _ = _setup(tmp_path, classification="ambiguous")

    with pytest.raises(ValueError, match="explicit reason"):
        store.review_measurement_candidate(
            candidate.candidate_id,
            "needs_more_evidence",
            "Actual Reviewer",
            classification="experimental_observation",
            **_review_args(),
        )

    updated = store.review_measurement_candidate(
        candidate.candidate_id,
        "needs_more_evidence",
        "Actual Reviewer",
        classification="experimental_observation",
        classification_reason="TEST FIXTURE: row is an individual extinction result.",
        **_review_args(),
    )
    event = store.measurement_review_history(candidate.candidate_id)[0]
    assert updated.classification == "experimental_observation"
    assert event.previous_classification == "ambiguous"
    assert event.new_classification == "experimental_observation"
    assert event.classification_reason == "TEST FIXTURE: row is an individual extinction result."


def test_candidate_detail_displays_field_of_view_limitations(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys,
) -> None:
    store, candidate, _, _ = _setup(tmp_path)
    monkeypatch.setattr(measurement_review, "_REPOSITORY_ROOT", tmp_path)
    figure_caption = (
        "TEST FIXTURE: droplet left the HiBMs field of view before extinction."
    )
    _write_audit_csv(
        tmp_path,
        candidate,
        quality_flags="field_of_view_or_estimate_quality_issue",
        figure_reference="TEST FIXTURE: Figure 108",
        figure_caption_excerpt=figure_caption,
    )

    measurement_review_main(
        [
            "--database",
            str(store.database_path),
            "show",
            candidate.candidate_id,
        ]
    )

    output = json.loads(capsys.readouterr().out)
    assert output["priority_review"]["quality_flags"] == (
        "field_of_view_or_estimate_quality_issue"
    )
    assert output["priority_review"]["figure_caption_excerpt"] == figure_caption
    assert output["candidate"]["review_status"] == "pending_review"


def test_priority_conflict_requires_explicit_resolution_before_approval(
    tmp_path: Path,
) -> None:
    store, candidate, _, _ = _setup(tmp_path, classification="ambiguous")
    _write_audit_csv(tmp_path, candidate)

    with pytest.raises(ValueError, match="priority candidate"):
        store.review_measurement_candidate(
            candidate.candidate_id,
            "approve",
            "Actual Reviewer",
            classification="experimental_observation",
            classification_reason="TEST FIXTURE: override classification for test.",
            source_review_confirmed=True,
            audit_classification="ambiguous",
            audit_rationale="TEST FIXTURE: unresolved source conflict.",
            **_review_args(),
            repository_root=tmp_path,
        )
    assert store.measurements() == []


def test_figure_that_reports_no_diameter_requires_separate_verified_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    store, candidate, investigation, source = _setup(
        tmp_path, classification="ambiguous"
    )
    quality_flag = "Figure_says_no_extinction_diameter_reported"
    caption = (
        "TEST FIXTURE: no extinction droplet diameter is reported."
    )
    _write_audit_csv(
        tmp_path,
        candidate,
        quality_flags=quality_flag,
        figure_reference="TEST FIXTURE: Figure 108",
        figure_caption_excerpt=caption,
    )
    review_args = {
        "classification": "experimental_observation",
        "classification_reason": "TEST FIXTURE: cite independent supporting evidence.",
        "source_review_confirmed": True,
        "priority_resolution_confirmed": True,
        "audit_classification": "ambiguous",
        "audit_quality_flags": [quality_flag],
        "figure_reference": "TEST FIXTURE: Figure 108",
        "figure_caption_excerpt": caption,
        **_review_args(),
        "repository_root": tmp_path,
    }

    monkeypatch.setattr(measurement_review, "_REPOSITORY_ROOT", tmp_path)
    with pytest.raises(SystemExit):
        measurement_review_main(
            [
                "--database",
                str(store.database_path),
                "review",
                candidate.candidate_id,
                "--decision",
                "approve",
                "--reviewer",
                "Actual Reviewer",
                "--classification",
                "experimental_observation",
                "--classification-reason",
                "TEST FIXTURE: separate evidence is necessary to resolve the conflict.",
                "--rationale",
                "TEST FIXTURE: caption conflict has no additional evidence.",
                "--evidence-notes",
                "TEST FIXTURE: Table IX and its figure caption were inspected.",
                "--confirm-source-review",
                "--resolve-priority",
            ]
        )
    assert store.measurements() == []
    assert store.measurement_candidate(candidate.candidate_id).review_status == "pending_review"

    additional_source = _verified_source(tmp_path, "additional-nasa-source")
    store.import_records(
        [investigation.model_copy(update={"sources": [source, additional_source]})],
        [],
    )
    with pytest.raises(ValueError, match="different verified source"):
        store.review_measurement_candidate(
            candidate.candidate_id,
            "approve",
            "Actual Reviewer",
            **review_args,
            additional_evidence_source_id=source.source_id,
            additional_evidence_page_number=2,
            additional_evidence_excerpt="TEST FIXTURE: same report cannot resolve its own conflict.",
            additional_evidence_review_confirmed=True,
        )

    measurement_review_main(
        [
            "--database",
            str(store.database_path),
            "review",
            candidate.candidate_id,
            "--decision",
            "approve",
            "--reviewer",
            "Actual Reviewer",
            "--classification",
            "experimental_observation",
            "--classification-reason",
            "TEST FIXTURE: independent evidence resolves the caption conflict.",
            "--rationale",
            "TEST FIXTURE: an independent verified source supports this observation.",
            "--evidence-notes",
            "TEST FIXTURE: checked the Table IX row, caption, and additional source.",
            "--confirm-source-review",
            "--resolve-priority",
            "--additional-evidence-source-id",
            additional_source.source_id,
            "--additional-evidence-page-number",
            "2",
            "--additional-evidence-section",
            "TEST FIXTURE: independent image analysis",
            "--additional-evidence-excerpt",
            "TEST FIXTURE: independent verified record supports the reported diameter.",
            "--confirm-additional-evidence-review",
        ]
    )
    capsys.readouterr()
    approved = store.measurement_candidate(candidate.candidate_id)
    assert approved is not None
    assert approved.review_status == "approved"
    event = store.measurement_review_history(candidate.candidate_id)[0]
    assert event.audit_quality_flags == [quality_flag]
    assert event.figure_reference == "TEST FIXTURE: Figure 108"
    assert event.figure_caption_excerpt == caption
    assert event.additional_supporting_evidence is not None
    assert event.additional_supporting_evidence.source_id == additional_source.source_id
    assert event.additional_supporting_evidence.source_sha256 == additional_source.sha256
    assert event.additional_supporting_evidence.page_number == 2
    assert event.additional_evidence_review_confirmed


def test_zero_extinction_diameter_requires_explicit_resolution_and_evidence(
    tmp_path: Path,
) -> None:
    store, candidate, _, _ = _setup(tmp_path)
    zero_candidate = candidate.model_copy(
        update={
            "candidate_id": "candidate-test-zero-diameter",
            "reported_value": "0",
            "value": 0.0,
        }
    )
    store.stage_measurement_candidates([zero_candidate])

    with pytest.raises(ValueError, match="explicit documented zero-value resolution"):
        store.review_measurement_candidate(
            zero_candidate.candidate_id,
            "approve",
            "Actual Reviewer",
            source_review_confirmed=True,
            **_review_args(),
            repository_root=tmp_path,
        )
    with pytest.raises(ValueError, match="additional source evidence"):
        store.review_measurement_candidate(
            zero_candidate.candidate_id,
            "approve",
            "Actual Reviewer",
            source_review_confirmed=True,
            zero_value_resolution_confirmed=True,
            **_review_args(),
            repository_root=tmp_path,
        )
    assert store.measurements() == []
    assert store.measurement_candidate(zero_candidate.candidate_id).review_status == "pending_review"
    assert store.measurement_review_history(zero_candidate.candidate_id) == []


def test_run_204_source_conflict_requires_explicit_documented_resolution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store, _, investigation, source = _setup(tmp_path)
    earlier_source = _verified_source(tmp_path, "earlier-nasa-report")
    store.import_records(
        [
            investigation.model_copy(
                update={"sources": [source, earlier_source]}
            )
        ],
        [
            Measurement(
                measurement_id="measurement-run-204-earlier",
                investigation_id=investigation.investigation_id,
                variable="extinction diameter",
                value=1.1,
                reported_value="1.10",
                unit="mm",
                source_id=earlier_source.source_id,
                observation_context={"run": "#204"},
                page_number=5,
                supporting_excerpt="TEST FIXTURE: earlier source reports 1.10 mm.",
            )
        ],
    )
    conflict_candidate = _candidate(
        source, candidate_id="candidate-test-run-204-table-ix"
    ).model_copy(
        update={
            "classification": "ambiguous",
            "review_flags": [
                "conflicts_with_approved_measurement: measurement-run-204-earlier"
            ]
        }
    )
    store.stage_measurement_candidates([conflict_candidate])
    _write_audit_csv(
        tmp_path,
        conflict_candidate,
        quality_flags="conflicts_with_approved_measurement",
    )
    monkeypatch.setattr(measurement_review, "_REPOSITORY_ROOT", tmp_path)

    with pytest.raises(SystemExit):
        measurement_review_main(
            [
                "--database",
                str(store.database_path),
                "review",
                conflict_candidate.candidate_id,
                "--decision",
                "approve",
                "--reviewer",
                "Actual Reviewer",
                "--classification",
                "experimental_observation",
                "--classification-reason",
                "TEST FIXTURE: attempted unresolved conflict.",
                "--rationale",
                "TEST FIXTURE: Table IX and earlier source values remain different.",
                "--evidence-notes",
                "TEST FIXTURE: both source reports were compared.",
                "--confirm-source-review",
                "--resolve-priority",
            ]
        )

    assert [item.reported_value for item in store.measurements()] == ["1.10"]
    assert store.measurement_candidate(conflict_candidate.candidate_id).review_status == "pending_review"
    assert store.measurement_review_history(conflict_candidate.candidate_id) == []


def test_derived_and_approximate_candidates_cannot_enter_direct_measurements(
    tmp_path: Path,
) -> None:
    store, candidate, _, _ = _setup(tmp_path, classification="derived_quantity")
    with pytest.raises(ValueError, match="cannot enter the direct-observation"):
        store.review_measurement_candidate(
            candidate.candidate_id,
            "approve",
            "Actual Reviewer",
            classification="experimental_observation",
            classification_reason="TEST FIXTURE: attempted derived override.",
            source_review_confirmed=True,
            audit_classification="derived_quantity",
            **_review_args(),
            repository_root=tmp_path,
        )
    assert store.measurements() == []

    approximate = candidate.model_copy(
        update={
            "candidate_id": "candidate-test-approximate",
            "classification": "approximate_value",
            "reported_value": "~1.11",
            "review_flags": ["approximate_reported_value"],
        }
    )
    store.stage_measurement_candidates([approximate])
    with pytest.raises(ValueError, match="Approximate source values"):
        store.review_measurement_candidate(
            approximate.candidate_id,
            "approve",
            "Actual Reviewer",
            classification="experimental_observation",
            classification_reason="TEST FIXTURE: attempted approximate override.",
            source_review_confirmed=True,
            **_review_args(),
            repository_root=tmp_path,
        )
    assert store.measurements() == []


def test_burn_time_approval_requires_source_definition_confirmation(
    tmp_path: Path,
) -> None:
    store, candidate, _, _ = _setup(tmp_path)
    burn_time = candidate.model_copy(
        update={
            "candidate_id": "candidate-test-burn-time",
            "variable": "burn time",
            "reported_value": "12.8",
            "value": 12.8,
            "unit": "s",
        }
    )
    store.stage_measurement_candidates([burn_time])

    with pytest.raises(ValueError, match="reporting convention"):
        store.review_measurement_candidate(
            burn_time.candidate_id,
            "approve",
            "Actual Reviewer",
            source_review_confirmed=True,
            **_review_args(),
            repository_root=tmp_path,
        )
    assert store.measurements() == []


def test_transaction_rolls_back_measurement_and_history_on_candidate_update_failure(
    tmp_path: Path,
) -> None:
    store, candidate, _, _ = _setup(tmp_path)
    with store._connect() as connection:
        connection.execute(
            "CREATE TRIGGER fail_candidate_review_update "
            "BEFORE UPDATE ON measurement_candidates BEGIN "
            "SELECT RAISE(ABORT, 'TEST FIXTURE: forced transaction failure'); END"
        )

    with pytest.raises(sqlite3.IntegrityError, match="forced transaction failure"):
        store.review_measurement_candidate(
            candidate.candidate_id,
            "approve",
            "Actual Reviewer",
            source_review_confirmed=True,
            **_review_args(),
            repository_root=tmp_path,
        )

    assert store.measurements() == []
    assert store.measurement_review_history(candidate.candidate_id) == []
    assert store.measurement_candidate(candidate.candidate_id).review_status == "pending_review"


def test_review_history_is_append_only_and_repeat_decisions_are_idempotent(
    tmp_path: Path,
) -> None:
    store, candidate, _, _ = _setup(tmp_path)
    first = store.review_measurement_candidate(
        candidate.candidate_id,
        "needs_more_evidence",
        "Actual Reviewer",
        **_review_args(),
    )
    repeated = store.review_measurement_candidate(
        candidate.candidate_id,
        "needs_more_evidence",
        "Actual Reviewer",
        **_review_args(),
    )
    assert repeated.reviewed_at == first.reviewed_at
    assert len(store.measurement_review_history(candidate.candidate_id)) == 1

    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        with store._connect() as connection:
            connection.execute(
                "DELETE FROM measurement_review_history WHERE candidate_id = ?",
                (candidate.candidate_id,),
            )

    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        with store._connect() as connection:
            connection.execute(
                "UPDATE measurement_review_history SET payload = '{}' "
                "WHERE candidate_id = ?",
                (candidate.candidate_id,),
            )


def test_rejection_requires_rationale_and_is_not_exposed_by_measurements_api(
    tmp_path: Path,
) -> None:
    store, candidate, _, _ = _setup(tmp_path)
    with pytest.raises(ValueError, match="documented review rationale"):
        store.review_measurement_candidate(
            candidate.candidate_id,
            "reject",
            "Actual Reviewer",
            evidence_notes="TEST FIXTURE: inspected the source.",
        )

    rejected = store.review_measurement_candidate(
        candidate.candidate_id,
        "reject",
        "Actual Reviewer",
        **_review_args(rationale="TEST FIXTURE: not an eligible observation."),
    )
    assert rejected.review_status == "rejected"
    assert store.measurements() == []
    event = store.measurement_review_history(candidate.candidate_id)[0]
    assert event.decision == "reject"
    assert event.rationale == "TEST FIXTURE: not an eligible observation."


def test_unverified_source_cannot_be_approved(
    tmp_path: Path,
) -> None:
    store, candidate, investigation, source = _setup(tmp_path)
    unverified = source.model_copy(update={"verification_status": "unverified"})
    store.import_records([investigation.model_copy(update={"sources": [unverified]})], [])

    with pytest.raises(ValueError, match="verified source provenance"):
        store.review_measurement_candidate(
            candidate.candidate_id,
            "approve",
            "Actual Reviewer",
            source_review_confirmed=True,
            **_review_args(),
            repository_root=tmp_path,
        )
    assert store.measurements() == []
    assert store.measurement_review_history(candidate.candidate_id) == []
