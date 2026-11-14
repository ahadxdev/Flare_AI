import argparse
from pathlib import Path

from app.ingestion import ingest, validate_source_files, write_report
from app.store import SQLiteStore


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import validated canonical FLARE AI investigation and measurement records."
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
<<<<<<< Updated upstream
    investigations, measurements, report = ingest(
        args.file, source_dir=args.source_dir, archive_dir=args.archive_dir
    )
    repository_root = (
        Path.cwd().parent if Path.cwd().name.casefold() == "backend" else Path.cwd()
    )
    report.issues.extend(validate_source_files(investigations, repository_root))
    if report.issues:
        report.investigations_written = 0
        report.measurements_written = 0
    write_report(report, args.report)
    if not report.valid:
        for issue in report.issues:
            print(f"ERROR {issue.record}: {issue.message}")
        raise SystemExit(1)
    SQLiteStore().import_records(investigations, measurements, replace=args.replace)
=======
    investigations, measurements, evidence_excerpts = load_import_file(args.file)
    SQLiteStore().import_records(
        investigations,
        measurements,
        replace=args.replace,
        evidence_excerpts=evidence_excerpts,
    )
>>>>>>> Stashed changes
    print(
        f"Imported {len(investigations)} investigations and "
        f"{len(measurements)} measurements and "
        f"{len(evidence_excerpts)} evidence excerpts."
    )


if __name__ == "__main__":
    main()
