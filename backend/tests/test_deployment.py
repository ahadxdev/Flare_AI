import asyncio
import io
import logging
import time
from dataclasses import replace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Event, Thread

import pytest
from fastapi.testclient import TestClient

from app.bootstrap import seed_empty_catalog
from app.chat_provider import OpenAICompatibleChatProvider
from app.config import Settings
from app.ingestion import validate_source_files
from app.logging_config import JSONFormatter
from app.main import create_app
from app.request_limits import RequestLimitsMiddleware
from app.store import SQLiteStore


@pytest.mark.parametrize("origin", ["*", "https://*.example", "https://client.example/path", "null", "https://user:secret@client.example"])
def test_cors_rejects_broad_or_malformed_origins(monkeypatch, origin):
    monkeypatch.setenv("FLARE_CORS_ORIGINS", origin)
    with pytest.raises(ValueError, match="FLARE_CORS_ORIGINS"):
        Settings.from_env()


def test_cors_denies_unlisted_origin_and_covers_limit_errors(tmp_path):
    settings = replace(Settings.from_env(), cors_origins=("https://demo.example",))
    with TestClient(create_app(str(tmp_path / "cors.sqlite3"), settings)) as client:
        allowed = client.options("/api/chat", headers={"Origin": "https://demo.example", "Access-Control-Request-Method": "POST"})
        denied = client.options("/api/chat", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"})
        assert allowed.status_code == 200
        assert denied.status_code == 400
        assert "access-control-allow-origin" not in denied.headers
        oversized = client.post("/api/chat", content=b"x" * 65537, headers={"Content-Type": "application/json", "Origin": "https://demo.example"})
        assert oversized.status_code == 413
        assert oversized.headers["access-control-allow-origin"] == "https://demo.example"


def test_uploads_disabled_and_valid_json_still_validates(client):
    response = client.post("/api/chat", files={"file": ("test.pdf", b"%PDF-test", "application/pdf")})
    assert response.status_code == 415
    assert response.json()["error"]["code"] == "UNSUPPORTED_MEDIA_TYPE"
    assert client.post("/api/chat", json={}).status_code == 422
    assert client.post("/api/upload", json={}).status_code == 404


def test_streamed_body_limit_ignores_forged_content_length():
    sent = []

    async def unexpected_app(scope, receive, send):
        pytest.fail("Oversized bodies must not reach the application")

    async def exercise():
        chunks = iter([
            {"type": "http.request", "body": b"x" * 700, "more_body": True},
            {"type": "http.request", "body": b"x" * 700, "more_body": False},
        ])

        async def receive():
            return next(chunks)

        async def send(message):
            sent.append(message)

        await RequestLimitsMiddleware(unexpected_app, 1, 1024)(
            {"type": "http", "path": "/api/chat", "method": "POST", "headers": [(b"content-type", b"application/json"), (b"content-length", b"1")]}, receive, send
        )

    asyncio.run(exercise())
    assert sent[0]["status"] == 413


def test_request_timeout_returns_standard_error(tmp_path):
    settings = replace(Settings.from_env(), request_timeout_seconds=0.03)
    app = create_app(str(tmp_path / "timeout.sqlite3"), settings)

    @app.get("/api/test-stall")
    async def stall():
        await asyncio.sleep(5)

    with TestClient(app) as client:
        response = client.get("/api/test-stall")
        assert response.status_code == 504
        assert response.json()["error"]["code"] == "REQUEST_TIMEOUT"


def test_request_timeout_bounds_sync_response(tmp_path):
    settings = replace(Settings.from_env(), request_timeout_seconds=0.03)
    app = create_app(str(tmp_path / "sync-timeout.sqlite3"), settings)

    @app.get("/api/test-sync-stall")
    def stall():
        time.sleep(0.3)
        return {"late": True}

    with TestClient(app) as client:
        started = time.monotonic()
        response = client.get("/api/test-sync-stall")
        assert response.status_code == 504
        assert time.monotonic() - started < 0.25


def test_health_and_readiness_are_distinct(client):
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/ready").status_code == 503


def test_readiness_checks_local_database(seeded_client):
    assert seeded_client.get("/api/ready").json() == {"status": "ok"}
    def broken(*args):
        raise OSError("secret database details")
    seeded_client.app.state.research_service.list_investigations = broken
    response = seeded_client.get("/api/ready")
    assert response.status_code == 503
    assert "secret" not in response.text


def test_logging_omits_secrets_and_raw_paths(tmp_path):
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JSONFormatter())
    logger = logging.getLogger("flare")
    logger.addHandler(handler)
    app = create_app(str(tmp_path / "logging.sqlite3"))

    @app.post("/api/test-failure/{value}")
    def failure(value: str):
        raise RuntimeError("secret-key private-question")

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.post("/api/test-failure/private-path?key=secret-query", json={"question": "private-question"}, headers={"Authorization": "Bearer secret-key"})
            assert response.status_code == 500
            client.get("/api/missing-private-path?key=secret-query")
        output = stream.getvalue()
        for secret in ["secret-key", "private-question", "private-path", "secret-query", "missing-private-path"]:
            assert secret not in output
        assert "RuntimeError" in output
    finally:
        logger.removeHandler(handler)


def test_static_serving_cannot_read_repository_files(tmp_path, monkeypatch):
    import app.main as main
    (tmp_path / "dist").mkdir()
    (tmp_path / "dist/index.html").write_text("<html>production fixture</html>")
    (tmp_path / ".env").write_text("secret-key")
    monkeypatch.setattr(main, "REPOSITORY_ROOT", tmp_path)
    settings = replace(Settings.from_env(), serve_frontend=True)
    with TestClient(create_app(str(tmp_path / "static.sqlite3"), settings)) as client:
        assert "production fixture" in client.get("/").text
        for path in ["/.env", "/%2e%2e/.env", "/backend/app/config.py", "/data/psi_starter.json"]:
            response = client.get(path)
            assert response.status_code == 404
            assert "secret-key" not in response.text
        assert client.get("/api/health").status_code == 200


def test_source_path_traversal_rejected(tmp_path, test_investigation):
    test_investigation.sources[0].local_file_path = "../outside.pdf"
    issues = validate_source_files([test_investigation], tmp_path)
    assert any("inside the repository" in issue.message for issue in issues)


def test_seed_preserves_existing_catalog(tmp_path, test_investigation):
    store = SQLiteStore(tmp_path / "owned.sqlite3")
    store.import_records([test_investigation], [])
    seed_empty_catalog(store)
    assert store.list_investigations()[1] == 1
    assert store.get_investigation(test_investigation.investigation_id) == test_investigation


@pytest.fixture(scope="module")
def local_demo(tmp_path_factory):
    settings = replace(Settings.from_env(), seed_on_start=True)
    with TestClient(create_app(str(tmp_path_factory.mktemp("deployment") / "seed.sqlite3"), settings)) as client:
        yield client


@pytest.mark.parametrize("mode", ["timeout", "unavailable", "malformed", "redirect"])
def test_seeded_demo_keeps_evidence_when_real_http_provider_fails(local_demo, mode):
    stopped = Event()
    received_paths = []

    class FailedProvider(BaseHTTPRequestHandler):
        def do_POST(self):
            received_paths.append(self.path)
            if mode == "timeout":
                stopped.wait(2)
                self.close_connection = True
                return
            self.send_response(302 if mode == "redirect" else 503 if mode == "unavailable" else 200)
            if mode == "redirect":
                self.send_header("Location", f"http://127.0.0.1:{self.server.server_port}/redirected")
            self.end_headers()
            self.wfile.write(b"not JSON")

        def do_GET(self):
            received_paths.append(self.path)
            self.send_response(200)
            self.end_headers()

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), FailedProvider)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    service = local_demo.app.state.research_service
    service.chat_provider = OpenAICompatibleChatProvider("test-only-loopback", "test-only", f"http://127.0.0.1:{server.server_port}", 0.05)
    try:
        assert local_demo.get("/api/ready").status_code == 200
        assert local_demo.get("/api/investigations").json()["total"] == 4
        response = local_demo.post("/api/chat", json={"question": "What does Saffire report about flammability and combustion?", "investigation_ids": ["psi-98"]})
        assert response.status_code == 200
        body = response.json()
        assert body["evidence"] and body["citations"]
        assert any("timed out or failed" in item for item in body["limitations"])
        assert received_paths == ["/chat/completions"]
        scenario = local_demo.post("/api/scenarios/analyze", json={"environment": "spacecraft", "objective": "general"}).json()
        report = local_demo.post("/api/reports", json={"scenario_id": scenario["scenario_id"], "investigation_ids": ["psi-98"], "format": "html"})
        assert report.status_code == 200 and report.json()["citations"]
        assert "not affiliated with or endorsed by NASA" in report.json()["content"]
    finally:
        service.chat_provider = None
        stopped.set()
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
