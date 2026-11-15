"""Download the public NASA NTRS source files used by the starter catalog.

The downloader never overwrites an existing file. It writes a manifest only
after a file exists, starts with a PDF signature, and has a SHA-256 digest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError


SOURCES = (
    {
        "source_id": "src-ntrs-saffire-status",
        "investigation_ids": ["psi-98", "psi-99"],
        "source_url": "https://ntrs.nasa.gov/api/citations/20170000230/downloads/20170000230.pdf",
        "document_title": "Operation and Development Status of the Spacecraft Fire Experiments (Saffire)",
        "file_name": "20170000230.pdf",
    },
    {
        "source_id": "src-ntrs-bass-metadata",
        "investigation_ids": ["psi-bass-ii"],
        "source_url": "https://ntrs.nasa.gov/api/citations/20210011385",
        "document_title": "NASA NTRS citation metadata for BASS-II",
        "file_name": "20210011385.json",
        "mime_type": "application/json",
    },
    {
        "source_id": "src-ntrs-flex",
        "investigation_ids": ["psi-flex"],
        "source_url": "https://ntrs.nasa.gov/api/citations/20130014061/downloads/20130014061.pdf",
        "document_title": "Methanol Droplet Combustion in Oxygen-Inert Environments in Microgravity",
        "file_name": "20130014061.pdf",
    },
    {
        "source_id": "src-ntrs-flex-results",
        "investigation_ids": ["psi-flex"],
        "source_url": "https://ntrs.nasa.gov/api/citations/20150023456/downloads/20150023456.pdf",
        "document_title": "Detailed Results from the Flame Extinguishment Experiment (FLEX) March 2009 to December 2011",
        "file_name": "20150023456.pdf",
    },
)

UNAVAILABLE_SOURCES = (
    {
        "source_id": "src-ntrs-bass-ii",
        "investigation_ids": ["psi-bass-ii"],
        "source_url": "https://ntrs.nasa.gov/api/citations/20210011385/downloads/TM-20210011385.pdf",
        "document_title": "Burning and Suppression of Solids-II (BASS-II) Summary Report",
        "verification_status": "unavailable",
        "failure_reason": (
            "The public server reported 48,972,416 bytes, but the transfer ended "
            "at 41,054,208 bytes and the server did not support byte-range resume."
        ),
        "manual_action": "Download the PDF manually from the source URL and verify its SHA-256.",
    },
)


def _file_metadata(path: Path, source: dict[str, object]) -> dict[str, object]:
    data = path.read_bytes()
    mime_type = str(source.get("mime_type") or mimetypes.guess_type(path.name)[0] or "")
    if mime_type == "application/pdf":
        if not data.startswith(b"%PDF-"):
            raise ValueError(f"{path} is not a PDF file.")
        if b"%%EOF" not in data[-4096:]:
            raise ValueError(f"{path} does not have a PDF EOF marker.")
        try:
            reader = PdfReader(str(path), strict=True)
            if not reader.pages:
                raise ValueError("PDF has no pages.")
            for page in reader.pages:
                page.extract_text()
        except (PdfReadError, OSError, ValueError) as exc:
            raise ValueError(f"{path} is incomplete or cannot be parsed as a PDF.") from exc
    elif mime_type == "application/json":
        json.loads(data.decode("utf-8"))
    return {
        **source,
        "local_file_path": path.as_posix(),
        "downloaded_at": datetime.fromtimestamp(
            path.stat().st_mtime, timezone.utc
        ).isoformat(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "file_size_bytes": len(data),
        "mime_type": mime_type,
        "last_verified_at": datetime.now(timezone.utc).isoformat(),
        "verification_status": "verified",
    }


def download(output_dir: Path, manifest_path: Path) -> list[dict[str, object]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, object]] = []
    for source in SOURCES:
        path = output_dir / str(source["file_name"])
        if not path.exists():
            temporary = path.with_suffix(path.suffix + ".part")
            try:
                with urllib.request.urlopen(str(source["source_url"]), timeout=120) as response:
                    data = response.read()
                    content_length = response.headers.get("Content-Length")
                    if content_length is not None and len(data) != int(content_length):
                        raise ValueError(
                            f"Incomplete download for {source['file_name']}: "
                            f"expected {content_length} bytes, received {len(data)}."
                        )
                    temporary.write_bytes(data)
                temporary.replace(path)
            finally:
                temporary.unlink(missing_ok=True)
        manifest.append(_file_metadata(path, source))
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "sources": manifest,
                "unavailable_sources": list(UNAVAILABLE_SOURCES),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir", default="data/raw/nasa", type=Path
    )
    parser.add_argument(
        "--manifest", default="data/raw/nasa/source_manifest.json", type=Path
    )
    args = parser.parse_args()
    for item in download(args.output_dir, args.manifest):
        print(
            f"{item['file_name']}|{item['file_size_bytes']}|"
            f"{item['sha256']}|{item['source_url']}"
        )


if __name__ == "__main__":
    main()
