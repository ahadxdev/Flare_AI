import hashlib
import json

from app.document_index import index_verified_sources
from app.models import Investigation
from app.store import SQLiteStore


def _fixture_investigation(root, source_id="approved-source") -> Investigation:
    source_path = root / "data" / "raw" / "nasa" / "source.json"
    payload = b'{"abstract":"NASA source reports droplet combustion observations."}'
    source_path.parent.mkdir(parents=True)
    source_path.write_bytes(payload)
    manifest_path = source_path.parent / "source_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "source_id": source_id,
                        "investigation_ids": ["fixture-investigation"],
                        "verification_status": "verified",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    return Investigation.model_validate(
        {
            "investigation_id": "fixture-investigation",
            "title": "Test indexed investigation",
            "research_area": "fundamentals",
            "environment": "microgravity",
            "data_availability": "documents",
            "sources": [
                {
                    "source_id": source_id,
                    "document_title": "NASA fixture source",
                    "source_url": "https://nasa.gov/fixture",
                    "source_type": "NASA_REPORT",
                    "local_file_path": "data/raw/nasa/source.json",
                    "file_size_bytes": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest(),
                    "mime_type": "application/json",
                    "verification_status": "verified",
                }
            ],
        }
    )


def test_index_requires_approved_manifest_and_preserves_citations(tmp_path):
    investigation = _fixture_investigation(tmp_path)
    excerpts, issues = index_verified_sources([investigation], tmp_path)

    assert not issues
    assert len(excerpts) == 1
    assert excerpts[0].investigation_id == investigation.investigation_id
    assert excerpts[0].source_id == "approved-source"
    assert excerpts[0].section == "Abstract"

    unapproved = investigation.model_copy(
        update={
            "sources": [
                investigation.sources[0].model_copy(update={"source_id": "not-approved"})
            ]
        }
    )
    excerpts, issues = index_verified_sources([unapproved], tmp_path)
    assert excerpts == []
    assert "not approved" in issues[0].message


def test_rebuild_replaces_generated_chunks_but_is_idempotent(tmp_path):
    investigation = _fixture_investigation(tmp_path)
    excerpts, _ = index_verified_sources([investigation], tmp_path)
    store = SQLiteStore(tmp_path / "test.sqlite3")
    store.import_records([investigation], [], replace=True, evidence_excerpts=excerpts)

    store.replace_evidence_index(excerpts)
    first = store.search_evidence("droplet combustion", ["fixture-investigation"])
    store.replace_evidence_index(excerpts)
    second = store.search_evidence("droplet combustion", ["fixture-investigation"])

    assert [(item.excerpt.excerpt_id, item.source.source_url) for item in first] == [
        (item.excerpt.excerpt_id, item.source.source_url) for item in second
    ]
