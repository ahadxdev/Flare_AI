import json
import logging
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app as default_app, create_app
from app.logging_config import JSONFormatter
from app.models import Investigation, Measurement, SourceCitation


def test_health_and_empty_catalog(client: TestClient) -> None:
    assert client.get("/api/health").json() == {"status": "ok"}
    response = client.get("/api/investigations")
    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["total"] == 0


def test_scenario_relevance_and_provenance(seeded_client: TestClient) -> None:
    response = seeded_client.post(
        "/api/scenarios/analyze",
        json={
            "environment": "spacecraft",
            "oxygen_pct": 30,
            "pressure": {"value": 10.2, "unit": "psi"},
            "objective": "combustion_fundamentals",
        },
    )
    assert response.status_code == 200
    match = response.json()["matches"][0]
    assert match["investigation_id"] == "test-only-combustion"
    assert match["score_breakdown"]["objective_match"] == 1
    assert match["score_breakdown"]["parameter_similarity"] == 1
    assert match["citations"][0]["source_id"] == "test-only-source"
    assert response.json()["score_type"] == "research_relevance_not_fire_risk"


def test_comparison_report_and_measurements(seeded_client: TestClient) -> None:
    comparison = seeded_client.post(
        "/api/compare",
        json={"investigation_ids": ["test-only-combustion"]},
    )
    assert comparison.status_code == 200
    assert comparison.json()["investigations"][0]["title"].startswith("TEST FIXTURE")

    report = seeded_client.post(
        "/api/reports",
        json={"investigation_ids": ["test-only-combustion"]},
    )
    assert report.status_code == 200
    assert report.json()["citations"][0]["source_id"] == "test-only-source"

    assert seeded_client.get("/api/measurements").json() == {"items": []}


def test_investigation_api_exposes_source_provenance(seeded_client: TestClient) -> None:
    response = seeded_client.get("/api/investigations/test-only-combustion")
    assert response.status_code == 200
    source = response.json()["sources"][0]
    assert source["source_id"] == "test-only-source"
    assert source["verification_status"] == "unverified"
    assert source["local_file_path"] is None


def test_source_linked_measurement_import(seeded_app, test_investigation) -> None:
    measurement = Measurement(
        measurement_id="test-only-measurement",
        investigation_id=test_investigation.investigation_id,
        variable="test burn time",
        value=1.2,
        unit="s",
        source_id="test-only-source",
    )
    seeded_app.state.research_service.store.import_records([], [measurement])
    with TestClient(seeded_app) as seeded_client:
        response = seeded_client.get(
            "/api/measurements",
            params={"investigation_id": test_investigation.investigation_id},
        )
    assert response.status_code == 200
    assert response.json()["items"][0]["source_id"] == "test-only-source"


def test_validation_not_found_and_no_evidence_use_standard_shape(
    client: TestClient,
) -> None:
    invalid = client.post(
        "/api/scenarios/analyze",
        json={"environment": "moon", "oxygen_pct": 101, "objective": "general"},
    )
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "VALIDATION_ERROR"
    assert {"field", "message"} <= invalid.json()["error"]["details"][0].keys()

    missing = client.get("/api/investigations/not-indexed")
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "NOT_FOUND"

    no_evidence = client.post("/api/chat", json={"question": "What happened?"})
    assert no_evidence.status_code == 422
    assert no_evidence.json()["error"]["code"] == "NO_EVIDENCE"
    assert "Not available in indexed sources" in no_evidence.json()["error"]["message"]


def test_unknown_filter_is_validation_error(client: TestClient) -> None:
    response = client.get("/api/investigations", params={"environment": "moon"})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_cors_is_configurable_from_environment(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("FLARE_CORS_ORIGINS", "https://client.example, https://other.example")
    settings = Settings.from_env()
    cors_app = create_app(str(tmp_path / "cors.sqlite3"), settings=settings)

    with TestClient(cors_app) as cors_client:
        response = cors_client.get(
            "/api/health", headers={"Origin": "https://client.example"}
        )
    assert response.headers["access-control-allow-origin"] == "https://client.example"


def test_model_contract_names_and_validation() -> None:
    assert Investigation.model_fields["investigation_id"].is_required()
    assert SourceCitation.model_validate(
        {
            "source_id": "source-1",
            "document_title": "NASA report",
            "source_url": "https://example.test/report",
        }
    )
    with pytest.raises(ValueError):
        Measurement(
            measurement_id="m1",
            investigation_id="test-only-combustion",
            variable="burn time",
            value=float("nan"),
            unit="s",
            source_id="test-only-source",
        )


def test_openapi_contract_file_matches_runtime() -> None:
    contract_path = Path(__file__).resolve().parents[2] / "api" / "openapi.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    assert contract == default_app.openapi()
    assert "/api/health" in contract["paths"]
    assert "/api/scenarios/analyze" in contract["paths"]
    expected_schemas = {
        "Investigation",
        "SourceCitation",
        "ScenarioRequest",
        "ScenarioAnalysisResponse",
        "ComparisonRequest",
        "ComparisonResponse",
        "ChatRequest",
        "ChatResponse",
        "Measurement",
        "ReportRequest",
        "ReportResponse",
    }
    assert expected_schemas <= contract["components"]["schemas"].keys()


def test_request_logs_are_json_structured() -> None:
    record = logging.LogRecord(
        name="flare.api",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="HTTP request completed",
        args=(),
        exc_info=None,
    )
    record.method = "GET"
    record.path = "/api/health"
    record.status_code = 200
    event = json.loads(JSONFormatter().format(record))
    assert event["message"] == "HTTP request completed"
    assert event["status_code"] == 200
