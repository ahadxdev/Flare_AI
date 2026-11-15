from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.ingestion import IngestionIssue
from app.models import EvidenceExcerpt, Investigation, Source


_CHUNK_SIZE = 1800
_CHUNK_OVERLAP = 200


@dataclass(frozen=True)
class VerifiedSourcePage:
    page_number: int | None
    section: str | None
    text: str
    error: str | None = None


def index_verified_sources(
    investigations: list[Investigation],
    repository_root: str | Path,
) -> tuple[list[EvidenceExcerpt], list[IngestionIssue]]:
    root = Path(repository_root).resolve()
    pages_by_path: dict[Path, list[tuple[int | None, str | None, str]]] = {}
    excerpts: list[EvidenceExcerpt] = []
    issues: list[IngestionIssue] = []

    for investigation in investigations:
        for source in investigation.sources:
            if source.verification_status != "verified" or not source.local_file_path:
                continue
            path = (root / source.local_file_path).resolve()
            try:
                path.relative_to(root)
            except ValueError:
                issues.append(
                    IngestionIssue(
                        source.source_id,
                        "Verified source path must remain inside the repository.",
                    )
                )
                continue
            if path not in pages_by_path:
                try:
                    pages_by_path[path] = read_verified_source(path, source)
                except (OSError, ValueError, PdfReadError, json.JSONDecodeError) as exc:
                    issues.append(IngestionIssue(source.source_id, str(exc)))
                    continue
            for page_number, section, text in pages_by_path[path]:
                for chunk_number, chunk in enumerate(_chunks(text), start=1):
                    excerpt_identity = "\x1f".join(
                        (
                            investigation.investigation_id,
                            source.source_id,
                            str(page_number),
                            str(chunk_number),
                            chunk,
                        )
                    )
                    excerpt_id = (
                        "excerpt-"
                        + hashlib.sha256(excerpt_identity.encode("utf-8")).hexdigest()[:24]
                    )
                    excerpts.append(
                        EvidenceExcerpt(
                            excerpt_id=excerpt_id,
                            investigation_id=investigation.investigation_id,
                            source_id=source.source_id,
                            excerpt=chunk,
                            page_number=page_number,
                            section=section,
                        )
                    )
    return excerpts, issues


def read_verified_source(
    path: Path,
    source: Source,
    *,
    layout: bool = False,
    include_empty_pages: bool = False,
) -> list[tuple[int | None, str | None, str]]:
    if not path.is_file():
        raise ValueError(f"Verified source file does not exist: {source.local_file_path}")
    raw = path.read_bytes()
    if source.file_size_bytes is None or len(raw) != source.file_size_bytes:
        raise ValueError("Verified source file size does not match its provenance metadata.")
    if source.sha256 is None or hashlib.sha256(raw).hexdigest() != source.sha256.casefold():
        raise ValueError("Verified source SHA-256 does not match its provenance metadata.")

    if source.mime_type == "application/pdf":
        if not raw.startswith(b"%PDF-") or b"%%EOF" not in raw[-4096:]:
            raise ValueError("Verified PDF is incomplete or has an invalid PDF signature.")
        reader = PdfReader(str(path), strict=True)
        if reader.is_encrypted:
            raise ValueError("Encrypted source PDFs are not indexed.")
        pages: list[tuple[int | None, str | None, str]] = []
        for page_number, page in enumerate(reader.pages, start=1):
            text = (
                page.extract_text(extraction_mode="layout")
                if layout
                else page.extract_text()
            ) or ""
            if text.strip() or include_empty_pages:
                pages.append((page_number, None, text))
        if not any(text.strip() for _, _, text in pages) and not include_empty_pages:
            raise ValueError("PDF contains no extractable text; no excerpts were indexed.")
        return pages

    if source.mime_type == "application/json":
        payload = json.loads(raw.decode("utf-8"))
        abstract = payload.get("abstract") if isinstance(payload, dict) else None
        if not isinstance(abstract, str) or not abstract.strip():
            raise ValueError("NASA metadata JSON has no extractable abstract.")
        return [(None, "Abstract", abstract)]

    raise ValueError(
        f"Unsupported source MIME type for text indexing: {source.mime_type or 'unknown'}."
    )


def iter_verified_source_pages(
    path: Path,
    source: Source,
    *,
    layout: bool = False,
    include_empty_pages: bool = False,
) -> Iterator[VerifiedSourcePage]:
    _verify_source_integrity(path, source)

    if source.mime_type == "application/pdf":
        reader = PdfReader(str(path), strict=True)
        if reader.is_encrypted:
            raise ValueError("Encrypted source PDFs are not indexed.")
        for page_number, page in enumerate(reader.pages, start=1):
            try:
                text = (
                    page.extract_text(extraction_mode="layout")
                    if layout
                    else page.extract_text()
                ) or ""
            except Exception as exc:
                yield VerifiedSourcePage(
                    page_number,
                    None,
                    "",
                    f"{type(exc).__name__}: {exc}",
                )
                continue
            if text.strip() or include_empty_pages:
                yield VerifiedSourcePage(page_number, None, text)
        return

    if source.mime_type == "application/json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        abstract = payload.get("abstract") if isinstance(payload, dict) else None
        if not isinstance(abstract, str) or not abstract.strip():
            raise ValueError("NASA metadata JSON has no extractable abstract.")
        yield VerifiedSourcePage(None, "Abstract", abstract)
        return

    raise ValueError(
        f"Unsupported source MIME type for text indexing: {source.mime_type or 'unknown'}."
    )


def _verify_source_integrity(path: Path, source: Source) -> None:
    if not path.is_file():
        raise ValueError(f"Verified source file does not exist: {source.local_file_path}")
    size = path.stat().st_size
    if source.file_size_bytes is None or size != source.file_size_bytes:
        raise ValueError("Verified source file size does not match its provenance metadata.")

    digest = hashlib.sha256()
    with path.open("rb") as file:
        prefix = file.read(5)
        if source.mime_type == "application/pdf":
            file.seek(max(0, size - 4096))
            tail = file.read(4096)
            if not prefix.startswith(b"%PDF-") or b"%%EOF" not in tail:
                raise ValueError("Verified PDF is incomplete or has an invalid PDF signature.")
        file.seek(0)
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    if source.sha256 is None or digest.hexdigest() != source.sha256.casefold():
        raise ValueError("Verified source SHA-256 does not match its provenance metadata.")


def _chunks(text: str) -> Iterable[str]:
    normalized = " ".join(text.split())
    position = 0
    while position < len(normalized):
        end = min(position + _CHUNK_SIZE, len(normalized))
        if end < len(normalized):
            boundary = normalized.rfind(" ", position + _CHUNK_SIZE // 2, end)
            if boundary > position:
                end = boundary
        chunk = normalized[position:end].strip()
        if chunk:
            yield chunk
        if end == len(normalized):
            break
        position = max(position + 1, end - _CHUNK_OVERLAP)
