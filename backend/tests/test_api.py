import json
import logging
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import Settings
from app.chat_provider import ProviderAnswer, ProviderError
from app.main import app as default_app, create_app
from app.logging_config import JSONFormatter
from app.store import load_import_file
from app.models import (
    ChatEvidence,
    ChatResponse,
    EvidenceExcerpt,
    Investigation,
    Measurement,
    Source,
    SourceCitation,
)


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


def test_validation_not_found_and_no_evidence_use_contract_shape(
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
    assert no_evidence.status_code == 200
    assert no_evidence.json()["answer_status"] == "insufficient_evidence"
    assert no_evidence.json()["evidence"] == []
    assert no_evidence.json()["citations"] == []
    assert "Not available in indexed sources" in no_evidence.json()["answer"]


def test_chat_retrieves_source_linked_evidence_and_citations(
    seeded_app, test_evidence_excerpt
) -> None:
    seeded_app.state.research_service.store.import_records(
        [], [], evidence_excerpts=[test_evidence_excerpt]
    )
    with TestClient(seeded_app) as seeded_client:
        response = seeded_client.post(
            "/api/chat",
            json={
                "question": "What happened to test cellulose flame spread?",
                "scenario_id": None,
                "investigation_ids": ["test-only-combustion"],
            },
        )
    assert response.status_code == 200
    payload = response.json()
    assert payload["answer_status"] == "grounded"
    assert payload["evidence"][0]["source_id"] == "test-only-source"
    assert payload["evidence"][0]["excerpt"] == test_evidence_excerpt.excerpt
    assert payload["citations"][0]["quote_or_supported_excerpt"] == test_evidence_excerpt.excerpt
    assert any("Microgravity evidence does not establish" in item for item in payload["limitations"])


def test_chat_retrieval_respects_investigation_filter(
    seeded_app, test_investigation, test_evidence_excerpt
) -> None:
    second_source = Source(
        source_id="test-only-source-2",
        document_title="Second test-only source",
        source_url="https://example.test/fixture-2",
        source_type="OTHER",
    )
    second_investigation = test_investigation.model_copy(
        update={
            "investigation_id": "test-only-combustion-2",
            "title": "TEST FIXTURE — second combustion study",
            "sources": [second_source],
        }
    )
    second_excerpt = EvidenceExcerpt(
        excerpt_id="test-only-excerpt-2",
        investigation_id=second_investigation.investigation_id,
        source_id=second_source.source_id,
        excerpt="TEST FIXTURE: test cellulose flame spread under other test conditions.",
    )
    seeded_app.state.research_service.store.import_records(
        [test_investigation, second_investigation],
        [],
        replace=True,
        evidence_excerpts=[test_evidence_excerpt, second_excerpt],
    )
    with TestClient(seeded_app) as seeded_client:
        response = seeded_client.post(
            "/api/chat",
            json={
                "question": "test cellulose flame spread",
                "investigation_ids": ["test-only-combustion"],
            },
        )
    assert response.status_code == 200
    assert {
        item["investigation_id"] for item in response.json()["evidence"]
    } == {"test-only-combustion"}


def test_chat_scenario_id_restores_scenario_context(
    seeded_client: TestClient, seeded_app, test_evidence_excerpt
) -> None:
    scenario = seeded_client.post(
        "/api/scenarios/analyze",
        json={
            "environment": "lunar_habitat",
            "oxygen_pct": 30,
            "pressure": {"value": 10.2, "unit": "psi"},
            "objective": "combustion_fundamentals",
        },
    ).json()
    seeded_app.state.research_service.store.import_records(
        [], [], evidence_excerpts=[test_evidence_excerpt]
    )
    response = seeded_client.post(
        "/api/chat",
        json={
            "question": "What happened to test cellulose?",
            "scenario_id": scenario["scenario_id"],
            "investigation_ids": [],
        },
    )
    assert response.status_code == 200
    assert response.json()["answer_status"] == "grounded"
    assert any(
        "user-entered assumptions" in item for item in response.json()["limitations"]
    )


def test_chat_surfaces_conflicting_excerpts(
    seeded_app, test_investigation, test_evidence_excerpt
) -> None:
    second_source = Source(
        source_id="test-only-source-2",
        document_title="Second test-only source",
        source_url="https://example.test/fixture-2",
        source_type="OTHER",
    )
    investigation = test_investigation.model_copy(
        update={"sources": [*test_investigation.sources, second_source]}
    )
    excerpts = [
        test_evidence_excerpt.model_copy(
            update={
                "excerpt": "TEST FIXTURE: the test material ignited under this condition."
            }
        ),
        EvidenceExcerpt(
            excerpt_id="test-only-excerpt-2",
            investigation_id=test_investigation.investigation_id,
            source_id=second_source.source_id,
            excerpt="TEST FIXTURE: the test material did not ignite under this condition.",
        ),
    ]
    seeded_app.state.research_service.store.import_records(
        [investigation], [], replace=True, evidence_excerpts=excerpts
    )

    class ConflictProvider:
        received = []

        def answer(self, _question, evidence, _scenario):
            assert _question == "Did the test material ignite?"
            assert _scenario is None
            self.received = evidence
            return ProviderAnswer(
                answer_status="insufficient_evidence",
                short_answer="The indexed test excerpts conflict.",
                scenario_relevance="No scenario context was supplied.",
                limitations="The discrepancy cannot be resolved from these excerpts.",
            )

    provider = ConflictProvider()
    seeded_app.state.research_service.chat_provider = provider
    with TestClient(seeded_app) as seeded_client:
        response = seeded_client.post(
            "/api/chat",
            json={"question": "Did the test material ignite?"},
        )
    assert response.status_code == 200
    assert response.json()["answer_status"] == "insufficient_evidence"
    assert len(provider.received) == 2
    assert {item["source_id"] for item in response.json()["citations"]} == {
        "test-only-source",
        "test-only-source-2",
    }
    assert "excerpts conflict" in response.json()["answer"]


def test_chat_provider_timeout_falls_back_to_retrieved_excerpts(
    seeded_app, test_evidence_excerpt
) -> None:
    seeded_app.state.research_service.store.import_records(
        [], [], evidence_excerpts=[test_evidence_excerpt]
    )

    class TimeoutProvider:
        def answer(self, _question, _evidence, _scenario):
            assert "test cellulose" in _question
            assert _evidence
            assert _scenario is None
            raise TimeoutError("provider timed out")

    seeded_app.state.research_service.chat_provider = TimeoutProvider()
    with TestClient(seeded_app) as seeded_client:
        response = seeded_client.post(
            "/api/chat",
            json={"question": "What happened to test cellulose?"},
        )
    assert response.status_code == 200
    payload = response.json()
    assert payload["answer_status"] == "grounded"
    assert payload["evidence"][0]["excerpt"] == test_evidence_excerpt.excerpt
    assert any("timed out or failed" in item for item in payload["limitations"])


def test_chat_provider_failure_falls_back_to_retrieved_excerpts(
    seeded_app, test_evidence_excerpt
) -> None:
    seeded_app.state.research_service.store.import_records(
        [], [], evidence_excerpts=[test_evidence_excerpt]
    )

    class FailedProvider:
        def answer(self, _question, _evidence, _scenario):
            assert "test cellulose" in _question
            assert _evidence
            assert _scenario is None
            raise ProviderError("provider unavailable")

    seeded_app.state.research_service.chat_provider = FailedProvider()
    with TestClient(seeded_app) as seeded_client:
        response = seeded_client.post(
            "/api/chat",
            json={"question": "What happened to test cellulose?"},
        )
    assert response.status_code == 200
    assert response.json()["answer_status"] == "grounded"
    assert any("timed out or failed" in item for item in response.json()["limitations"])


def test_chat_response_rejects_citations_not_in_retrieved_evidence() -> None:
    evidence = ChatEvidence(
        source_id="source-1",
        investigation_id="investigation-1",
        document_title="Test source",
        source_url="https://example.test/source",
        excerpt="Retrieved excerpt.",
    )
    bad_citation = SourceCitation(
        source_id=evidence.source_id,
        document_title=evidence.document_title,
        source_url=evidence.source_url,
        quote_or_supported_excerpt="Different, unretrieved excerpt.",
    )
    with pytest.raises(ValidationError, match="map to a retrieved evidence excerpt"):
        ChatResponse(
            answer="Grounded answer",
            evidence=[evidence],
            citations=[bad_citation],
            limitations=[],
            answer_status="grounded",
        )


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


def test_import_file_accepts_verified_evidence_excerpts(
    tmp_path, test_investigation, test_evidence_excerpt
) -> None:
    path = tmp_path / "verified-records.json"
    path.write_text(
        json.dumps(
            {
                "investigations": [test_investigation.model_dump(mode="json")],
                "measurements": [],
                "evidence_excerpts": [test_evidence_excerpt.model_dump(mode="json")],
            }
        ),
        encoding="utf-8",
    )
    investigations, measurements, excerpts = load_import_file(path)
    assert investigations[0].investigation_id == test_investigation.investigation_id
    assert measurements == []
    assert excerpts == [test_evidence_excerpt]


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
        "ChatEvidence",
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
