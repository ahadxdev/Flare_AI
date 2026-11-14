import argparse

from app.store import SQLiteStore, load_import_file


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import validated canonical FLARE AI investigation and measurement records."
    )
    parser.add_argument("file", help="JSON file containing investigations and measurements")
    parser.add_argument(
        "--replace", action="store_true", help="Replace the existing local catalog"
    )
    args = parser.parse_args()
    investigations, measurements = load_import_file(args.file)
    SQLiteStore().import_records(investigations, measurements, replace=args.replace)
    print(
        f"Imported {len(investigations)} investigations and "
        f"{len(measurements)} measurements."
    )


if __name__ == "__main__":
    main()
