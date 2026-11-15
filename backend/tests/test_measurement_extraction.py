from __future__ import annotations

import hashlib
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter

from app.document_index import iter_verified_source_pages
from app.main import create_app
from app.measurement_extraction import (
    extract_page_candidates,
    extract_table_ix_candidates,
    reconcile_approved_measurement_duplicates,
)
from app.measurement_review import main as measurement_review_main
from app.models import (
    Investigation,
    Measurement,
    MeasurementCandidate,
    MeasurementCandidateClassification,
    Source,
)
from app.store import SQLiteStore


def _verified_source(
    *,
    local_file_path: str | None = None,
    sha256: str = "a" * 64,
    file_size_bytes: int | None = None,
) -> Source:
    return Source(
        source_id="test-only-nasa-source",
        document_title="TEST FIXTURE — NASA source",
        source_url="https://ntrs.nasa.gov/test-fixture",
        source_type="NASA_REPORT",
        local_file_path=local_file_path,
        downloaded_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        sha256=sha256,
        file_size_bytes=file_size_bytes,
        mime_type="application/pdf" if local_file_path else None,
        last_verified_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
        verification_status="verified",
    )


def _candidate(
    source: Source,
    *,
    candidate_id: str = "candidate-test-only",
    classification: MeasurementCandidateClassification = "experimental_observation",
) -> MeasurementCandidate:
    return MeasurementCandidate(
        candidate_id=candidate_id,
        investigation_id="test-only-measurement-investigation",
        source_id=source.source_id,
        document_title=source.document_title,
        source_url=source.source_url,
        source_sha256=source.sha256,
        variable="extinction diameter",
        reported_value="1.10",
        value=1.1,
        unit="mm",
        observation_context={"run": "#204"},
        page_number=5,
        section="3.1 Results",
        table_reference="Table 2",
        supporting_excerpt="TEST FIXTURE: extinction diameter was 1.10 mm.",
        extraction_method="pdf_table_text",
        confidence=0.98,
        classification=classification,
    )


def _investigation(source: Source) -> Investigation:
    return Investigation(
        investigation_id="test-only-measurement-investigation",
        title="TEST FIXTURE — measurement investigation",
        research_area="fundamentals",
        environment="microgravity",
        sources=[source],
    )


def _write_test_pdf(path) -> Source:
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    with path.open("wb") as file:
        writer.write(file)
    raw = path.read_bytes()
    return _verified_source(
        local_file_path=path.name,
        sha256=hashlib.sha256(raw).hexdigest(),
        file_size_bytes=len(raw),
    )


def test_extracts_text_results_units_context_and_table_reference(
    test_investigation: Investigation,
) -> None:
    source = _verified_source()
    investigation = test_investigation.model_copy(update={"sources": [source]})
    text = (
        "Table 2. TEST FIXTURE observations\n"
        "3.1 Results\n"
        "Run #204 corresponds to a methanol droplet with initial diameter 2.75 mm.\n"
        "Flame extinction occurs at a droplet diameter of 1.10 mm, the extinction diameter.\n"
        "The extinction diameters for Run #110 and #263 were 1.57 mm and 1.42 mm, respectively."
    )

    candidates, rejected = extract_page_candidates(
        investigation=investigation,
        source=source,
        page_number=5,
        section="3.1 Results",
        text=text,
        extraction_method="pdf_text",
    )

    by_value = {item.reported_value: item for item in candidates}
    assert by_value["2.75"].variable == "initial droplet diameter"
    assert by_value["2.75"].classification == "initial_condition"
    assert by_value["1.10"].variable == "extinction diameter"
    assert by_value["1.10"].classification == "experimental_observation"
    assert by_value["1.10"].observation_context == {"run": "#204"}
    assert by_value["1.57"].observation_context == {"run": "#110"}
    assert by_value["1.42"].observation_context == {"run": "#263"}
    assert by_value["1.57"].unit == by_value["1.42"].unit == "mm"
    assert by_value["1.10"].page_number == 5
    assert by_value["1.10"].table_reference == "Table 2"
    assert "1.10 mm" in by_value["1.10"].supporting_excerpt
    assert by_value["1.10"].extraction_method == "pdf_table_text"
    assert rejected.get("quantity_without_recognized_variable", 0) == 0


def test_extracts_oxygen_and_temperature_without_changing_reported_units(
    test_investigation: Investigation,
) -> None:
    source = _verified_source()
    investigation = test_investigation.model_copy(update={"sources": [source]})
    candidates, _ = extract_page_candidates(
        investigation=investigation,
        source=source,
        page_number=2,
        section=None,
        text=(
            "The oxygen concentration was 21%O2 during this TEST FIXTURE run.\n"
            "The measured temperature was 1200 K."
        ),
        extraction_method="pdf_text",
    )

    assert [(item.variable, item.reported_value, item.unit) for item in candidates] == [
        ("oxygen concentration", "21", "%"),
        ("temperature", "1200", "K"),
    ]
    assert candidates[0].classification == "boundary_condition"


def test_approximate_text_values_keep_precision_and_review_flag(
    test_investigation: Investigation,
) -> None:
    source = _verified_source()
    investigation = test_investigation.model_copy(update={"sources": [source]})

    candidates, _ = extract_page_candidates(
        investigation=investigation,
        source=source,
        page_number=2,
        section="TEST FIXTURE: Results",
        text="TEST FIXTURE: The burning time was ~12.90 s.",
        extraction_method="pdf_text",
    )

    assert len(candidates) == 1
    assert candidates[0].reported_value == "~12.90"
    assert candidates[0].value == 12.9
    assert candidates[0].unit == "s"
    assert candidates[0].classification == "approximate_value"
    assert candidates[0].review_flags == ["approximate_reported_value"]


def test_extracts_row_linked_table_ix_values_and_skips_reported_missing_cells(
    test_investigation: Investigation,
) -> None:
    source = _verified_source()
    investigation = test_investigation.model_copy(update={"sources": [source]})
    text = (
        "TABLE IX.—RESULTS BY TEST NUMBER AND FLEX IDENTIFIER\n"
        "FLEX Test Identifier Date Fuel Ambient pressure Initial ambient composition "
        "mole fraction Droplet initial Visible flame Burning Burn time Test end\n"
        "Test Identifier Date GMT Fuel mmHg O2 N2 CO2 He diameter mm "
        "extinction diameter mm rate mm2/s s\n"
        "FLEX–204  N01M201  8/24/11  21:58:36  Methanol  761.6  .21  .79  "
        "0  0  2.75  1.11  .52  12.8  Extinction\n"
        "FLEX–205  N01M202  8/24/11  22:00:00  Methanol  761.6  .21  .79  "
        "0  0  2.75  –  .51  ~12.9  Completion"
    )

    candidates, rejected = extract_table_ix_candidates(
        investigation=investigation,
        source=source,
        page_number=26,
        section="A.2 Experiment Results",
        text=text,
    )

    by_variable = {item.variable: item for item in candidates if item.observation_context["test"] == "FLEX–204"}
    assert len(by_variable) == 9
    assert by_variable["pressure"].reported_value == "761.6"
    assert by_variable["pressure"].unit == "mmHg"
    assert by_variable["pressure"].classification == "boundary_condition"
    assert by_variable["oxygen mole fraction"].reported_value == ".21"
    assert by_variable["oxygen mole fraction"].unit == "mole fraction"
    assert by_variable["initial droplet diameter"].classification == "initial_condition"
    assert by_variable["visible flame extinction diameter"].reported_value == "1.11"
    assert by_variable["visible flame extinction diameter"].classification == "experimental_observation"
    assert by_variable["burning rate"].reported_value == ".52"
    assert by_variable["burning rate"].unit == "mm2/s"
    assert by_variable["burning rate"].classification == "derived_quantity"
    assert by_variable["burn time"].reported_value == "12.8"
    assert by_variable["burn time"].unit == "s"
    assert by_variable["burn time"].table_reference == "Table IX"
    assert by_variable["burn time"].page_number == 26
    assert "FLEX–204" in by_variable["burn time"].supporting_excerpt
    assert "Visible flame" in by_variable["burn time"].supporting_excerpt
    assert all(item.review_status == "pending_review" for item in candidates)
    assert rejected == {}
    assert not any(
        item.observation_context["test"] == "FLEX–205"
        and item.variable == "visible flame extinction diameter"
        for item in candidates
    )
    approximate_burn_time = next(
        item
        for item in candidates
        if item.observation_context["test"] == "FLEX–205"
        and item.variable == "burn time"
    )
    assert approximate_burn_time.reported_value == "~12.9"
    assert approximate_burn_time.value == 12.9
    assert approximate_burn_time.classification == "approximate_value"
    assert approximate_burn_time.review_flags == ["approximate_reported_value"]


def test_existing_approved_run_duplicates_are_suppressed_or_flagged(
    test_investigation: Investigation,
) -> None:
    source = _verified_source()
    investigation = test_investigation.model_copy(update={"sources": [source]})
    exact = _candidate(source, candidate_id="candidate-exact")
    exact = exact.model_copy(
        update={
            "investigation_id": investigation.investigation_id,
            "variable": "visible flame extinction diameter",
            "observation_context": {"test": "FLEX–110"},
        }
    )
    conflicting = exact.model_copy(
        update={
            "candidate_id": "candidate-conflicting",
            "reported_value": "1.11",
            "value": 1.11,
            "observation_context": {"test": "FLEX–204"},
        }
    )
    approved_110 = Measurement(
        measurement_id="measurement-existing-110",
        investigation_id=investigation.investigation_id,
        variable="extinction diameter",
        value=1.1,
        reported_value="1.10",
        unit="mm",
        source_id=source.source_id,
        observation_context={"run": "#110"},
    )
    approved_204 = Measurement(
        measurement_id="measurement-existing-204",
        investigation_id=investigation.investigation_id,
        variable="extinction diameter",
        value=1.1,
        reported_value="1.10",
        unit="mm",
        source_id=source.source_id,
        observation_context={"run": "#204"},
    )

    remaining, suppressed = reconcile_approved_measurement_duplicates(
        [exact, conflicting], [approved_110, approved_204]
    )

    assert [item.candidate_id for item in remaining] == ["candidate-conflicting"]
    assert remaining[0].classification == "ambiguous"
    assert remaining[0].review_flags[0].startswith(
        "conflicts_with_approved_measurement"
    )
    assert suppressed[0]["measurement_id"] == approved_110.measurement_id


def test_placeholder_reviewer_correction_preserves_approval_and_observation(
    tmp_path,
) -> None:
    import json
    import sqlite3

    source = _write_test_pdf(tmp_path / "source.pdf")
    store = SQLiteStore(tmp_path / "test.sqlite3")
    store.import_records([_investigation(source)], [])
    candidate = _candidate(source)
    store.stage_measurement_candidates([candidate])
    store.review_measurement_candidate(
        candidate.candidate_id,
        "approve",
        "TEST REVIEWER",
        notes="TEST FIXTURE: checked the source.",
        evidence_notes="TEST FIXTURE: checked the cited page and excerpt.",
        source_review_confirmed=True,
        repository_root=tmp_path,
    )
    with sqlite3.connect(store.database_path) as connection:
        for table, key, key_value in (
            ("measurements", "measurement_id", "measurement-test-only"),
            ("measurement_candidates", "candidate_id", candidate.candidate_id),
        ):
            payload = connection.execute(
                f"SELECT payload FROM {table} WHERE {key} = ?", (key_value,)
            ).fetchone()[0]
            record = json.loads(payload)
            record["reviewed_by"] = "YOUR NAME"
            connection.execute(
                f"UPDATE {table} SET payload = ? WHERE {key} = ?",
                (json.dumps(record), key_value),
            )

    corrected = store.correct_placeholder_reviewer_attributions()

    assert len(corrected) == 1
    measurement = store.measurements()[0]
    approved_candidate = store.measurement_candidate(candidate.candidate_id)
    assert measurement.reported_value == "1.10"
    assert measurement.value == 1.1
    assert measurement.reviewed_by is None
    assert "could not be established" in (measurement.review_notes or "")
    assert approved_candidate is not None
    assert approved_candidate.review_status == "approved"
    assert approved_candidate.reviewed_by is None
    assert "TEST FIXTURE: checked the source." in (approved_candidate.review_notes or "")
    assert "could not be established" in (approved_candidate.review_notes or "")
    assert store.correct_placeholder_reviewer_attributions() == []


@pytest.mark.parametrize(
    ("text", "expected_classification"),
    [
        ("Simulation predicted a temperature of 1200 K.", "simulation_input"),
        (
            "A hypothetical mission scenario assumed a temperature of 1200 K.",
            "hypothetical",
        ),
        ("Heat release rates were well below 100 W.", "reported_summary"),
    ],
)
def test_classifies_simulation_hypothetical_and_summary_values(
    test_investigation: Investigation,
    text: str,
    expected_classification: MeasurementCandidateClassification,
) -> None:
    source = _verified_source()
    investigation = test_investigation.model_copy(update={"sources": [source]})
    candidates, _ = extract_page_candidates(
        investigation=investigation,
        source=source,
        page_number=None,
        section=None,
        text=f"TEST FIXTURE: {text}",
        extraction_method="metadata_text",
    )

    assert len(candidates) == 1
    assert candidates[0].classification == expected_classification


def test_rejects_incidental_and_range_numbers_without_variable_evidence(
    test_investigation: Investigation,
) -> None:
    source = _verified_source()
    investigation = test_investigation.model_copy(update={"sources": [source]})
    candidates, rejected = extract_page_candidates(
        investigation=investigation,
        source=source,
        page_number=2,
        section=None,
        text="TEST FIXTURE published in 2014; sample size was 2-5 mm.",
        extraction_method="pdf_text",
    )

    assert candidates == []
    assert rejected.get("quantity_without_recognized_variable", 0) == 0
    assert rejected.get("number_without_supported_unit", 0) >= 2


def test_staging_is_idempotent_and_requires_matching_verified_provenance(
    tmp_path,
) -> None:
    source = _write_test_pdf(tmp_path / "source.pdf")
    store = SQLiteStore(tmp_path / "test.sqlite3")
    store.import_records([_investigation(source)], [])
    candidate = _candidate(source)

    assert store.stage_measurement_candidates([candidate]) == 1
    assert store.stage_measurement_candidates([candidate]) == 0

    bad_candidate = candidate.model_copy(
        update={
            "candidate_id": "candidate-test-only-bad-hash",
            "source_sha256": "b" * 64,
        }
    )
    with pytest.raises(ValueError, match="matching verified NASA source"):
        store.stage_measurement_candidates([bad_candidate])
    assert store.measurements() == []


def test_streaming_reader_yields_pages_and_rechecks_source_integrity(tmp_path) -> None:
    source = _write_test_pdf(tmp_path / "source.pdf")

    pages = list(
        iter_verified_source_pages(
            tmp_path / "source.pdf",
            source,
            layout=True,
            include_empty_pages=True,
        )
    )

    assert len(pages) == 1
    assert pages[0].page_number == 1
    assert pages[0].text == ""
    (tmp_path / "source.pdf").write_bytes(b"TEST FIXTURE: tampered source")
    with pytest.raises(ValueError, match="file size"):
        list(iter_verified_source_pages(tmp_path / "source.pdf", source))


def test_review_approval_imports_once_and_rejection_does_not_import(tmp_path) -> None:
    source = _write_test_pdf(tmp_path / "source.pdf")
    store = SQLiteStore(tmp_path / "test.sqlite3")
    store.import_records([_investigation(source)], [])
    approved_candidate = _candidate(source)
    rejected_candidate = _candidate(
        source,
        candidate_id="candidate-test-only-rejected",
        classification="ambiguous",
    )
    store.stage_measurement_candidates([approved_candidate, rejected_candidate])

    with pytest.raises(ValueError, match="experimental observations"):
        store.review_measurement_candidate(
            approved_candidate.candidate_id,
            "approve",
            "TEST REVIEWER",
            classification="ambiguous",
            classification_reason="TEST FIXTURE: exercise the classification gate.",
            rationale="TEST FIXTURE: classification is not approval eligible.",
            evidence_notes="TEST FIXTURE: inspected the source excerpt.",
            repository_root=tmp_path,
        )

    approved = store.review_measurement_candidate(
        approved_candidate.candidate_id,
        "approve",
        "TEST REVIEWER",
        notes="TEST FIXTURE: source excerpt checked.",
        evidence_notes="TEST FIXTURE: checked the cited source page.",
        source_review_confirmed=True,
        repository_root=tmp_path,
    )
    rejected = store.review_measurement_candidate(
        rejected_candidate.candidate_id,
        "reject",
        "TEST REVIEWER",
        notes="TEST FIXTURE: not an observation.",
        evidence_notes="TEST FIXTURE: inspected the source context.",
        repository_root=tmp_path,
    )

    assert approved is not None
    assert approved.review_status == "approved"
    assert approved.reviewed_by == "TEST REVIEWER"
    assert approved.measurement_id is not None
    assert rejected is not None
    assert rejected.review_status == "rejected"
    assert store.measurement_candidates("pending_review") == []
    measurements = store.measurements()
    assert len(measurements) == 1
    assert measurements[0].reported_value == "1.10"
    assert measurements[0].supporting_excerpt == approved_candidate.supporting_excerpt
    assert measurements[0].reviewed_by == "TEST REVIEWER"

    store.review_measurement_candidate(
        approved_candidate.candidate_id,
        "approve",
        "TEST REVIEWER",
        repository_root=tmp_path,
    )
    assert len(store.measurements()) == 1


def test_conflicting_approved_run_cannot_be_imported_twice(tmp_path) -> None:
    source = _write_test_pdf(tmp_path / "source.pdf")
    store = SQLiteStore(tmp_path / "test.sqlite3")
    store.import_records([_investigation(source)], [])
    candidate = _candidate(source).model_copy(
        update={
            "classification": "ambiguous",
            "review_flags": [
                "conflicts_with_approved_measurement: measurement-existing"
            ],
        }
    )
    store.stage_measurement_candidates([candidate])

    with pytest.raises(ValueError, match="conflicts with an approved measurement"):
        store.review_measurement_candidate(
            candidate.candidate_id,
            "approve",
            "TEST REVIEWER",
            classification="experimental_observation",
            classification_reason="TEST FIXTURE: explicit conflict override attempt.",
            rationale="TEST FIXTURE: this must hit the source-conflict guard.",
            evidence_notes="TEST FIXTURE: inspected both competing source records.",
            repository_root=tmp_path,
        )

    assert store.measurements() == []
    assert store.measurement_candidate(candidate.candidate_id).review_status == "pending_review"


def test_show_command_displays_complete_candidate_provenance(
    tmp_path, capsys
) -> None:
    source = _write_test_pdf(tmp_path / "source.pdf")
    store = SQLiteStore(tmp_path / "test.sqlite3")
    store.import_records([_investigation(source)], [])
    candidate = _candidate(source)
    store.stage_measurement_candidates([candidate])

    measurement_review_main(
        ["--database", str(tmp_path / "test.sqlite3"), "show", candidate.candidate_id]
    )

    import json

    output = json.loads(capsys.readouterr().out)
    assert output["candidate"]["candidate_id"] == candidate.candidate_id
    assert output["candidate"]["source_sha256"] == source.sha256
    assert output["candidate"]["supporting_excerpt"] == candidate.supporting_excerpt
    assert output["review_history"] == []


def test_approval_rechecks_original_file_integrity(tmp_path) -> None:
    source = _write_test_pdf(tmp_path / "source.pdf")
    store = SQLiteStore(tmp_path / "test.sqlite3")
    store.import_records([_investigation(source)], [])
    candidate = _candidate(source)
    store.stage_measurement_candidates([candidate])
    (tmp_path / "source.pdf").write_bytes(b"TEST FIXTURE: changed original")

    with pytest.raises(ValueError, match="failed verification"):
        store.review_measurement_candidate(
            candidate.candidate_id,
            "approve",
            "TEST REVIEWER",
            rationale="TEST FIXTURE: verify original source integrity.",
            evidence_notes="TEST FIXTURE: attempted review of a changed PDF.",
            source_review_confirmed=True,
            repository_root=tmp_path,
        )
    assert store.measurements() == []
    assert store.measurement_candidates("pending_review")[0].review_status == "pending_review"


def test_approved_candidate_flows_through_existing_measurements_api(tmp_path) -> None:
    source = _write_test_pdf(tmp_path / "source.pdf")
    investigation = _investigation(source)
    app = create_app(str(tmp_path / "api.sqlite3"))
    store = app.state.research_service.store
    store.import_records([investigation], [])
    candidate = _candidate(source)
    store.stage_measurement_candidates([candidate])

    with TestClient(app) as client:
        pending_response = client.get(
            "/api/measurements",
            params={"investigation_id": investigation.investigation_id},
        )
        assert pending_response.status_code == 200
        assert pending_response.json()["data"] == []

        store.review_measurement_candidate(
            candidate.candidate_id,
            "needs_more_evidence",
            "TEST REVIEWER",
            rationale="TEST FIXTURE: verify the source timing context.",
            evidence_notes="TEST FIXTURE: checked the table excerpt; definition still needed.",
        )
        evidence_response = client.get(
            "/api/measurements",
            params={"investigation_id": investigation.investigation_id},
        )
        assert evidence_response.status_code == 200
        assert evidence_response.json()["data"] == []

        store.review_measurement_candidate(
            candidate.candidate_id,
            "approve",
            "TEST REVIEWER",
            notes="TEST FIXTURE: approved after checking the source.",
            evidence_notes="TEST FIXTURE: checked the exact value and source page.",
            source_review_confirmed=True,
            repository_root=tmp_path,
        )
        response = client.get(
            "/api/measurements",
            params={"investigation_id": investigation.investigation_id},
        )

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 1
    item = body["data"][0]
    assert item["reported_value"] == "1.10"
    assert item["unit"] == "mm"
    assert item["document_title"] == source.document_title
    assert item["source_url"] == str(source.source_url)
    assert item["page_number"] == 5
    assert item["section"] == "3.1 Results"
    assert item["table_reference"] == "Table 2"
    assert item["supporting_excerpt"] == candidate.supporting_excerpt
    assert item["reviewed_by"] == "TEST REVIEWER"
    assert item["review_notes"] == (
        "TEST FIXTURE: approved after checking the source.\n\n"
        "Evidence inspected: TEST FIXTURE: checked the exact value and source page."
    )


def test_unresolved_run_204_conflict_keeps_three_approved_observations_unchanged(
    tmp_path,
) -> None:
    source = _write_test_pdf(tmp_path / "source.pdf")
    investigation = _investigation(source)
    app = create_app(str(tmp_path / "api.sqlite3"))
    store = app.state.research_service.store
    approved_measurements = [
        Measurement(
            measurement_id=f"measurement-approved-run-{run}",
            investigation_id=investigation.investigation_id,
            variable="extinction diameter",
            value=value,
            reported_value=reported_value,
            unit="mm",
            source_id=source.source_id,
            observation_context={"run": f"#{run}"},
            page_number=5,
            section="3.1 Results",
            supporting_excerpt=f"TEST FIXTURE: Run #{run} reports {reported_value} mm.",
            reviewed_by="TEST REVIEWER",
            reviewed_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            review_notes="TEST FIXTURE: preserve existing approval metadata.",
        )
        for run, value, reported_value in (
            (204, 1.1, "1.10"),
            (110, 1.57, "1.57"),
            (263, 1.42, "1.42"),
        )
    ]
    store.import_records([investigation], approved_measurements)
    before = store.measurements()

    conflict_candidate = _candidate(source).model_copy(
        update={
            "candidate_id": "candidate-test-run-204-table-ix",
            "reported_value": "1.11",
            "value": 1.11,
            "table_reference": "Table IX",
            "classification": "ambiguous",
            "review_flags": [
                "conflicts_with_approved_measurement: measurement-approved-run-204"
            ],
        }
    )
    store.stage_measurement_candidates([conflict_candidate])

    with pytest.raises(ValueError, match="Resolve the conflict explicitly"):
        store.review_measurement_candidate(
            conflict_candidate.candidate_id,
            "approve",
            "TEST REVIEWER",
            classification="experimental_observation",
            classification_reason="TEST FIXTURE: conflict remains unresolved.",
            source_review_confirmed=True,
            priority_resolution_confirmed=True,
            audit_classification="ambiguous",
            rationale="TEST FIXTURE: preserve the conflicting source reports.",
            evidence_notes="TEST FIXTURE: reviewed both 1.10 mm and 1.11 mm records.",
            repository_root=tmp_path,
        )

    with TestClient(app) as client:
        response = client.get(
            "/api/measurements",
            params={"investigation_id": investigation.investigation_id},
        )

    assert response.status_code == 200
    observations = response.json()["data"]
    assert {
        (item["observation_context"]["run"], item["reported_value"], item["unit"])
        for item in observations
    } == {
        ("#204", "1.10", "mm"),
        ("#110", "1.57", "mm"),
        ("#263", "1.42", "mm"),
    }
    assert store.measurements() == before
    assert store.measurement_candidate(conflict_candidate.candidate_id).review_status == "pending_review"
    assert store.measurement_review_history(conflict_candidate.candidate_id) == []
