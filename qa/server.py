"""Disposable QA/demo server; never import or replace the user's catalog database."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event, Thread
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))


def serve(port: int) -> None:
    # Set before importing app.main, whose module-level app otherwise opens the default DB.
    with TemporaryDirectory(prefix="flare-qa-demo-") as directory:
        os.environ["FLARE_DATABASE_PATH"] = str(Path(directory) / "demo.sqlite3")
        os.environ["FLARE_LLM_API_KEY"] = ""
        os.environ["FLARE_LLM_MODEL"] = ""

        import uvicorn
        from app.config import Settings
        from app.document_index import index_verified_sources
        from app.ingestion import ingest_bundle, validate_source_files
        from app.main import create_app
        from app.services import SQLiteResearchService
        from app.store import SQLiteStore

        profile = json.loads((ROOT / "qa/fixtures/demo.json").read_text(encoding="utf-8"))
        bundle = ingest_bundle(ROOT / profile["catalog"])
        investigations = [
            item for item in bundle.investigations
            if item.investigation_id in profile["investigation_ids"]
        ]
        if len(investigations) != len(profile["investigation_ids"]):
            raise RuntimeError("Demo profile references missing investigation IDs")
        issues = validate_source_files(investigations, ROOT)
        if issues:
            raise RuntimeError(f"Source verification failed: {issues}")
        # Only narrow indexing inputs; the catalog's source records stay unchanged.
        indexing_records = [
            item.model_copy(update={"sources": [
                source for source in item.sources
                if source.source_id in profile["indexed_source_ids"]
            ]}) for item in investigations
        ]
        excerpts, issues = index_verified_sources(indexing_records, ROOT)
        if issues or not excerpts:
            raise RuntimeError(f"Demo evidence indexing failed: {issues}")
        settings = replace(Settings.from_env(), log_level="WARNING")
        store = SQLiteStore(Path(directory) / "demo.sqlite3")
        store.import_records(investigations, [], replace=True, evidence_excerpts=excerpts)
        app = create_app(settings=settings, research_service=SQLiteResearchService(store))
        empty_store = SQLiteStore(Path(directory) / "empty.sqlite3")
        app.mount("/__qa__/empty", create_app(
            settings=settings, research_service=SQLiteResearchService(empty_store)
        ))

        # Exercise the real HTTP provider adapter against a loopback server that stalls.
        # No API key, question, or source excerpt is sent to an external service.
        stop = Event()

        class StalledProvider(BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers.get("Content-Length", "0")))
                stop.wait(2)
                self.close_connection = True

            def log_message(self, *_args):
                pass

        provider = ThreadingHTTPServer(("127.0.0.1", 0), StalledProvider)
        Thread(target=provider.serve_forever, daemon=True).start()
        timeout_settings = replace(
            settings, llm_api_key="fixture-loopback-only", llm_model="fixture-timeout",
            llm_base_url=f"http://127.0.0.1:{provider.server_port}",
            llm_timeout_seconds=0.05,
        )
        app.mount("/__qa__/timeout", create_app(
            database_path=str(Path(directory) / "demo.sqlite3"), settings=timeout_settings
        ))

        @app.get("/__qa__/info", include_in_schema=False)
        def info():
            return {**profile, "evidence_count": len(excerpts)}

        @app.middleware("http")
        async def label_demo(request, call_next):
            response = await call_next(request)
            response.headers["X-FLARE-Data-Mode"] = "fixture-offline-demo"
            return response

        print(profile["label"], flush=True)
        try:
            uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
        finally:
            stop.set()
            provider.shutdown()
            provider.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8011)
    serve(parser.parse_args().port)
