import argparse
from pathlib import Path

from app.document_index import index_verified_sources
from app.ingestion import ingest_bundle, validate_source_files, write_report
from app.store import SQLiteStore


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Validate canonical FLARE AI records and index verified source documents."
        )
    )
    parser.add_argument(
        "file",
        nargs="+",
        help="Curated JSON or CSV file(s) containing investigation records",
    )
    parser.add_argument(
        "--source-dir",
        help="Directory of original source documents to inventory and optionally archive",
    )
    parser.add_argument(
        "--archive-dir",
        help="Copy source documents byte-for-byte into this directory",
    )
    parser.add_argument(
        "--report",
        default="ingestion-report.json",
        help="Path for the JSON ingestion report",
    )
    parser.add_argument(
        "--replace", action="store_true", help="Replace the existing local catalog"
    )
    args = parser.parse_args()

    bundle = ingest_bundle(
        args.file,
        source_dir=args.source_dir,
        archive_dir=args.archive_dir,
    )
    investigations = bundle.investigations
    measurements = bundle.measurements
    report = bundle.report
    repository_root = (
        Path.cwd().parent if Path.cwd().name.casefold() == "backend" else Path.cwd()
    )
    report.issues.extend(validate_source_files(investigations, repository_root))
    if report.issues:
        report.investigations_written = 0
        report.measurements_written = 0
        report.evidence_excerpts_written = 0
        for issue in report.issues:
            print(f"ERROR {issue.record}: {issue.message}")
        write_report(report, args.report)
        raise SystemExit(1)

    indexed_excerpts, indexing_issues = index_verified_sources(
        investigations,
        repository_root,
    )
    excerpts = [*bundle.evidence_excerpts, *indexed_excerpts]
    report.indexing_issues.extend(indexing_issues)
    report.evidence_excerpts_written = len(excerpts)
    SQLiteStore().import_records(
        investigations,
        measurements,
        replace=args.replace,
        evidence_excerpts=excerpts,
    )
    write_report(report, args.report)
    print(
        f"Imported {len(investigations)} investigations, "
        f"{len(measurements)} measurements, and {len(excerpts)} evidence excerpts."
    )
    for issue in report.indexing_issues:
        print(f"WARNING {issue.record}: {issue.message}")


if __name__ == "__main__":
    main()
