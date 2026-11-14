import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.models import Investigation


@pytest.fixture
def test_investigation() -> Investigation:
    """Clearly labeled test-only fixture; never loaded by the live application."""
    return Investigation.model_validate(
        {
            "investigation_id": "test-only-combustion",
            "title": "TEST FIXTURE — combustion study",
            "research_area": "fundamentals",
            "environment": "microgravity",
            "materials_or_fuels": ["test cellulose"],
            "conditions": {"oxygen_pct": 30, "pressure": {"value": 10.2, "unit": "psi"}},
            "variables_measured": ["test burn time"],
            "data_availability": "numeric_dataset",
            "sources": [
                {
                    "source_id": "test-only-source",
                    "document_title": "Test-only source",
                    "source_url": "https://example.test/fixture",
                    "source_type": "OTHER",
                }
            ],
        }
    )


@pytest.fixture
def app(tmp_path):
    return create_app(str(tmp_path / "test.sqlite3"))


@pytest.fixture
def client(app):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def seeded_app(app, test_investigation):
    app.state.research_service.store.import_records(
        [test_investigation], [], replace=True
    )
    return app


@pytest.fixture
def seeded_client(seeded_app):
    with TestClient(seeded_app) as test_client:
        yield test_client
