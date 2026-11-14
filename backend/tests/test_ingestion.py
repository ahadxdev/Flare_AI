import json
import hashlib

import pytest

from app.ingestion import ingest, normalize_investigation, stable_id
from app.download_nasa_sources import _file_metadata
from app.models import Source


def test_stable_ids_and_missing_scientific_fields_are_preserved() -> None:
    raw = {
        "title": "Curated PSI record",
        "sources": [
            {
                "document_title": "NASA PSI record",
                "source_url": "https://example.nasa.gov/record",
                "source_type": "NASA_PSI",
            }
        ],
    }
    record = normalize_investigation(raw)
    assert record.investigation_id == stable_id(
        "psi", "Curated PSI record", "https://example.nasa.gov/record"
    )
    assert record.sources[0].source_id == stable_id(
        "src", "https://example.nasa.gov/record", "NASA PSI record"
    )
    assert record.environment == "unknown"
    assert record.data_availability == "unknown"
    assert record.conditions.oxygen_pct is None


def test_csv_input_and_duplicate_detection(tmp_path) -> None:
    csv_path = tmp_path / "records.csv"
    csv_path.write_text(
        "title,research_area,source_url,document_title,source_type\n"
        "Record,other,https://example.nasa.gov/a,Source,NASA_PSI\n"
        "Record,other,https://example.nasa.gov/a,Source,NASA_PSI\n",
        encoding="utf-8",
    )
    investigations, measurements, report = ingest(csv_path)
    assert len(investigations) == 1
    assert measurements == []
    assert report.duplicate_investigations
    assert not report.valid


def test_invalid_provenance_and_enum_are_reported(tmp_path) -> None:
    path = tmp_path / "bad.json"
    path.write_text(
        json.dumps(
            {
                "investigations": [
                    {
                        "title": "Bad record",
                        "research_area": "made_up",
                        "sources": [
                            {
                                "document_title": "Unsafe source",
                                "source_url": "http://example.test",
                                "source_type": "NASA_PSI",
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    investigations, measurements, report = ingest(path)
    assert investigations == []
    assert measurements == []
    assert len(report.issues) == 1


def test_source_archive_is_byte_for_byte_and_reported(tmp_path) -> None:
    source_dir = tmp_path / "sources"
    source_dir.mkdir()
    original = source_dir / "record.txt"
    original.write_bytes(b"original source bytes\n")
    archive_dir = tmp_path / "archive"
    _, _, report = ingest([], source_dir=source_dir, archive_dir=archive_dir)
    assert (archive_dir / "record.txt").read_bytes() == original.read_bytes()
    assert report.archived_files[0]["size_bytes"] == original.stat().st_size


def test_source_provenance_fields_require_valid_hash_and_status() -> None:
    source = Source(
        source_id="source-1",
        document_title="NASA PDF",
        source_url="https://ntrs.nasa.gov/citations/1",
        source_type="NASA_REPORT",
        local_file_path="data/raw/nasa/report.pdf",
        downloaded_at="2026-11-14T10:00:00Z",
        sha256=hashlib.sha256(b"source").hexdigest(),
        file_size_bytes=6,
        mime_type="application/pdf",
        last_verified_at="2026-11-14T10:01:00Z",
        verification_status="verified",
    )
    assert source.verification_status == "verified"
    with pytest.raises(ValueError):
        Source(
            source_id="source-2",
            document_title="NASA PDF",
            source_url="https://ntrs.nasa.gov/citations/2",
            source_type="NASA_REPORT",
            sha256="not-a-sha256",
        )


def test_original_pdf_metadata_requires_existing_unchanged_file(tmp_path) -> None:
    pdf = tmp_path / "source.pdf"
    pdf.write_bytes(b"%PDF-1.7\noriginal\n%%EOF\n")
    metadata = _file_metadata(
        pdf,
        {
            "source_id": "source-1",
            "investigation_ids": ["record-1"],
            "source_url": "https://ntrs.nasa.gov/citations/1/downloads/source.pdf",
            "document_title": "Original NASA PDF",
            "file_name": "source.pdf",
        },
    )
    assert metadata["file_size_bytes"] == pdf.stat().st_size
    assert metadata["sha256"] == hashlib.sha256(pdf.read_bytes()).hexdigest()


def test_measurement_must_reference_investigation_and_source(tmp_path) -> None:
    path = tmp_path / "records.json"
    path.write_text(
        json.dumps(
            {
                "investigations": [
                    {
                        "investigation_id": "record-1",
                        "title": "Record",
                        "research_area": "other",
                        "sources": [
                            {
                                "source_id": "source-1",
                                "document_title": "Source",
                                "source_url": "https://ntrs.nasa.gov/citations/1",
                                "source_type": "NASA_REPORT",
                            }
                        ],
                    }
                ],
                "measurements": [
                    {
                        "measurement_id": "measurement-1",
                        "investigation_id": "record-1",
                        "variable": "temperature",
                        "value": 1,
                        "unit": "K",
                        "source_id": "missing-source",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    _, measurements, report = ingest(path)
    assert measurements == []
    assert any("Unknown source_id" in issue.message for issue in report.issues)
