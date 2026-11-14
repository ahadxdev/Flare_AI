"""Safe, provenance-preserving normalization for manually curated PSI records."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from app.models import Investigation, Measurement


LIST_FIELDS = {
    "objectives",
    "materials_or_fuels",
    "hardware",
    "sensors",
    "variables_measured",
    "findings",
}
JSON_FIELDS = {"conditions", "sources"}
@dataclass
class IngestionIssue:
    record: str
    message: str


@dataclass
class IngestionReport:
    input_files: list[str] = field(default_factory=list)
    archived_files: list[dict[str, Any]] = field(default_factory=list)
    investigations_read: int = 0
    investigations_written: int = 0
    measurements_read: int = 0
    measurements_written: int = 0
    duplicate_investigations: list[str] = field(default_factory=list)
    duplicate_sources: list[str] = field(default_factory=list)
    issues: list[IngestionIssue] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.issues

    def as_dict(self) -> dict[str, Any]:
        return {
            "input_files": self.input_files,
            "archived_files": self.archived_files,
            "investigations_read": self.investigations_read,
            "investigations_written": self.investigations_written,
            "measurements_read": self.measurements_read,
            "measurements_written": self.measurements_written,
            "duplicate_investigations": self.duplicate_investigations,
            "duplicate_sources": self.duplicate_sources,
            "issues": [
                {"record": issue.record, "message": issue.message}
                for issue in self.issues
            ],
        }


def stable_id(prefix: str, *parts: str) -> str:
    """Create a deterministic ID from curated identity fields."""
    identity = "\x1f".join(part.strip().casefold() for part in parts if part.strip())
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}-{digest}"


def normalize_investigation(raw: dict[str, Any]) -> Investigation:
    """Assign missing IDs and defaults, then validate the canonical model."""
    record = dict(raw)
    sources = [_normalize_source(source) for source in _as_list_of_dicts(record.get("sources"))]
    record["sources"] = sources
    first_source = sources[0] if sources else {}
    record.setdefault(
        "investigation_id",
        stable_id(
            "psi",
            str(record.get("title", "")),
            str(first_source.get("source_url", "")),
        ),
    )
    record.setdefault("title", "")
    record.setdefault("research_area", "other")
    record.setdefault("environment", "unknown")
    record.setdefault("data_availability", "unknown")
    for field_name in LIST_FIELDS:
        record[field_name] = _as_string_list(record.get(field_name))
    record.setdefault("conditions", {"oxygen_pct": None, "pressure": {}, "other": []})
    record.setdefault("last_verified_at", None)
    return Investigation.model_validate(record)


def normalize_measurement(raw: dict[str, Any]) -> Measurement:
    record = dict(raw)
    record.setdefault(
        "measurement_id",
        stable_id(
            "measurement",
            str(record.get("investigation_id", "")),
            str(record.get("variable", "")),
            str(record.get("value", "")),
            str(record.get("unit", "")),
        ),
    )
    record.setdefault("conditions", {})
    return Measurement.model_validate(record)


def ingest(
    input_paths: str | Path | list[str | Path],
    *,
    source_dir: str | Path | None = None,
    archive_dir: str | Path | None = None,
) -> tuple[list[Investigation], list[Measurement], IngestionReport]:
    if isinstance(input_paths, (str, Path)):
        input_paths = [input_paths]
    report = IngestionReport(input_files=[str(Path(path)) for path in input_paths])
    raw_investigations: list[dict[str, Any]] = []
    raw_measurements: list[dict[str, Any]] = []
    for input_path in input_paths:
        path = Path(input_path)
        try:
            investigations, measurements = _read_input(path)
        except (OSError, ValueError, UnicodeError) as exc:
            report.issues.append(IngestionIssue(str(path), str(exc)))
            continue
        raw_investigations.extend(investigations)
        raw_measurements.extend(measurements)

    if source_dir is not None:
        _archive_sources(Path(source_dir), archive_dir, report)

    investigations: list[Investigation] = []
    seen_investigation_ids: set[str] = set()
    report.investigations_read = len(raw_investigations)
    for index, raw in enumerate(raw_investigations, start=1):
        try:
            investigation = normalize_investigation(raw)
        except (ValidationError, TypeError, ValueError) as exc:
            report.issues.append(IngestionIssue(f"investigation[{index}]", str(exc)))
            continue
        if investigation.investigation_id in seen_investigation_ids:
            report.duplicate_investigations.append(investigation.investigation_id)
            report.issues.append(
                IngestionIssue(
                    f"investigation[{index}]",
                    f"Duplicate investigation_id: {investigation.investigation_id}",
                )
            )
            continue
        seen_investigation_ids.add(investigation.investigation_id)
        if not investigation.sources:
            report.issues.append(
                IngestionIssue(
                    f"investigation[{index}].sources",
                    "At least one HTTPS source is required for every investigation.",
                )
            )
            continue
        record_source_ids: set[str] = set()
        for source in investigation.sources:
            if source.source_id in record_source_ids:
                report.duplicate_sources.append(source.source_id)
                report.issues.append(
                    IngestionIssue(
                        f"investigation[{index}].sources",
                        f"Duplicate source_id: {source.source_id}",
                    )
                )
            record_source_ids.add(source.source_id)
        investigations.append(investigation)
    report.investigations_written = len(investigations)

    measurements: list[Measurement] = []
    seen_measurement_ids: set[str] = set()
    known_ids = {item.investigation_id for item in investigations}
    report.measurements_read = len(raw_measurements)
    for index, raw in enumerate(raw_measurements, start=1):
        try:
            measurement = normalize_measurement(raw)
            if measurement.investigation_id not in known_ids:
                raise ValueError(
                    f"Unknown investigation_id: {measurement.investigation_id}"
                )
            known_sources = {
                source.source_id
                for item in investigations
                if item.investigation_id == measurement.investigation_id
                for source in item.sources
            }
            if measurement.source_id not in known_sources:
                raise ValueError(f"Unknown source_id: {measurement.source_id}")
        except (ValidationError, TypeError, ValueError) as exc:
            report.issues.append(IngestionIssue(f"measurement[{index}]", str(exc)))
            continue
        if measurement.measurement_id in seen_measurement_ids:
            report.issues.append(
                IngestionIssue(
                    f"measurement[{index}]",
                    f"Duplicate measurement_id: {measurement.measurement_id}",
                )
            )
            continue
        seen_measurement_ids.add(measurement.measurement_id)
        measurements.append(measurement)
    report.measurements_written = len(measurements)
    return investigations, measurements, report


def write_report(report: IngestionReport, path: str | Path) -> None:
    Path(path).write_text(
        json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def validate_source_files(
    investigations: list[Investigation], repository_root: str | Path | None = None
) -> list[IngestionIssue]:
    """Verify every declared local source file without changing it."""
    root = Path(repository_root) if repository_root else Path.cwd()
    issues: list[IngestionIssue] = []
    for investigation in investigations:
        for source in investigation.sources:
            if not source.local_file_path:
                continue
            path = root / source.local_file_path
            if not path.exists():
                issues.append(
                    IngestionIssue(
                        source.source_id,
                        f"Original source file does not exist: {source.local_file_path}",
                    )
                )
                continue
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if source.sha256 and digest.casefold() != source.sha256.casefold():
                issues.append(
                    IngestionIssue(
                        source.source_id,
                        f"SHA-256 mismatch for {source.local_file_path}.",
                    )
                )
            if source.file_size_bytes is not None and path.stat().st_size != source.file_size_bytes:
                issues.append(
                    IngestionIssue(
                        source.source_id,
                        f"File size mismatch for {source.local_file_path}.",
                    )
                )
            if source.verification_status == "verified" and not source.sha256:
                issues.append(
                    IngestionIssue(
                        source.source_id,
                        "A verified source file must include sha256.",
                    )
                )
    return issues


def _read_input(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if path.suffix.casefold() == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as handle:
            return [_parse_csv_row(row) for row in csv.DictReader(handle)], []
    if path.suffix.casefold() != ".json":
        raise ValueError("Input must be a .json or .csv file.")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload, []
    if not isinstance(payload, dict) or set(payload) - {"investigations", "measurements"}:
        raise ValueError(
            "JSON input must be a list or contain only investigations and measurements."
        )
    return payload.get("investigations", []), payload.get("measurements", [])


def _parse_csv_row(row: dict[str, str]) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for key, value in row.items():
        if value is None or value.strip() == "":
            continue
        if key in LIST_FIELDS or key in JSON_FIELDS:
            try:
                parsed[key] = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError(f"CSV field {key!r} must contain JSON.") from exc
        else:
            parsed[key] = value
    if "source_url" in parsed:
        source = {
            "source_url": parsed.pop("source_url"),
            "document_title": parsed.pop("document_title", ""),
            "source_type": parsed.pop("source_type", "OTHER"),
        }
        for field_name in ("page_number", "section", "source_id"):
            if field_name in parsed:
                source[field_name] = parsed.pop(field_name)
        parsed["sources"] = [source]
    return parsed


def _normalize_source(raw: dict[str, Any]) -> dict[str, Any]:
    source = dict(raw)
    source.setdefault(
        "source_id",
        stable_id(
            "src",
            str(source.get("source_url", "")),
            str(source.get("document_title", "")),
        ),
    )
    return source


def _as_list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise ValueError("sources must be a list of objects.")
    return value


def _as_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError("List fields must be arrays of strings.")
    return value


def _archive_sources(
    source_dir: Path, archive_dir: str | Path | None, report: IngestionReport
) -> None:
    if not source_dir.is_dir():
        report.issues.append(IngestionIssue(str(source_dir), "Source directory not found."))
        return
    if archive_dir is None:
        return
    destination = Path(archive_dir)
    destination.mkdir(parents=True, exist_ok=True)
    for path in sorted(item for item in source_dir.rglob("*") if item.is_file()):
        relative = path.relative_to(source_dir)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        report.archived_files.append(
            {
                "path": str(relative),
                "sha256": digest,
                "size_bytes": path.stat().st_size,
                "archived_at": datetime.now(timezone.utc).isoformat(),
            }
        )
