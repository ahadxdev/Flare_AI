"""Seed an empty demo catalog from checked-in sources, with no network calls."""

import logging
from pathlib import Path

from app.document_index import index_verified_sources
from app.ingestion import ingest_bundle, validate_source_files
from app.store import SQLiteStore


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
logger = logging.getLogger("flare.bootstrap")


def seed_empty_catalog(store: SQLiteStore) -> None:
    if store.list_investigations(page_size=1)[1]:
        return
    bundle = ingest_bundle(REPOSITORY_ROOT / "data/psi_starter.json")
    issues = [*bundle.report.issues, *validate_source_files(bundle.investigations, REPOSITORY_ROOT)]
    if issues or not bundle.investigations:
        raise RuntimeError("The bundled demo catalog failed source validation; startup aborted.")
    excerpts, indexing_issues = index_verified_sources(bundle.investigations, REPOSITORY_ROOT)
    if not excerpts:
        raise RuntimeError("No verified local demo evidence could be indexed; startup aborted.")
    store.import_records(
        bundle.investigations, bundle.measurements,
        evidence_excerpts=[*bundle.evidence_excerpts, *excerpts],
    )
    logger.info("Seeded local curated demo catalog")
    if indexing_issues:
        logger.warning("Some bundled document pages could not be indexed; no text was inferred")
