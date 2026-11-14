# FLARE AI NASA Data Provenance Audit

**Audit/remediation date:** 2026-11-14  
**Scope:** Repository, ingestion code, raw source directory, normalized records, SQLite database, API responses, frontend flow, fixtures, and source manifest.

## Final status

**PARTIAL — strict original-source remediation is not complete.**

The application now preserves and hashes four original NASA-hosted source files:

- Three original NTRS PDFs for SAFFIRE and FLEX.
- One original NTRS citation-metadata JSON file for BASS-II.

The BASS-II publication PDF was requested from its official NTRS download URL, but the transfer ended at 41,054,208 bytes while the server reported 48,972,416 bytes. The server did not support byte-range resume. That incomplete file was not retained or marked verified. The official NTRS metadata response was preserved instead, and the publication remains explicitly unavailable.

No numeric measurements were added because no source CSV/table extraction was completed with row/page/figure provenance. The production measurement collection remains empty.

## Totals

| Metric | Result |
|---|---:|
| NASA-linked investigations in live database | 4 |
| Original source files preserved | 4 |
| Investigations with a preserved original NASA publication file | 3 |
| Verified datasets/CSVs | 0 |
| Verified numeric measurements | 0 |
| Investigations with complete publication source traceability | 3 |
| Investigations with partial traceability | 1 (`psi-bass-ii`) |
| Unverified production investigation records | 0 at URL/metadata level; 1 partial at publication-file level |
| Production mock/synthetic investigations | 0 |
| Production synthetic measurements | 0 |
| Test-only fixture investigations | 1 |

## Investigation audit

| ID | Title | Supporting source file(s) | File status | Data availability | Measurement status |
|---|---|---|---|---|---|
| `psi-98` | Spacecraft Fire Experiment-I (SAFFIRE-I) | `data/raw/nasa/20170000230.pdf` | Verified PDF | Documents | No verified measurements |
| `psi-99` | Spacecraft Fire Experiment-II (SAFFIRE-II) | `data/raw/nasa/20170000230.pdf` | Verified PDF | Documents | No verified measurements |
| `psi-bass-ii` | Burning and Suppression of Solids-II (BASS-II) | `data/raw/nasa/20210011385.json`; report PDF unavailable | Metadata JSON verified; publication unavailable | Documents | No verified measurements |
| `psi-flex` | Flame Extinguishment Experiment (FLEX) | `data/raw/nasa/20130014061.pdf`; `data/raw/nasa/20150023456.pdf` | Verified PDFs | Documents | No verified measurements |

### Source URLs and exact evidence

| Investigation | Source ID | Exact source URL | Document title | Supported fields |
|---|---|---|---|---|
| `psi-98`, `psi-99` | `src-ntrs-saffire-status` | <https://ntrs.nasa.gov/api/citations/20170000230/downloads/20170000230.pdf> | Operation and Development Status of the Spacecraft Fire Experiments (Saffire) | Saffire objectives, low-gravity context, Cygnus operation, low-g flammability objective |
| `psi-98` | `src-psi-98` | <https://psi.nasa.gov/physci/repo/data/investigations/PSI-98> | NASA PSI investigation PSI-98 | Official PSI investigation link/identifier only; response is the PSI application shell |
| `psi-99` | `src-psi-99` | <https://psi.nasa.gov/physci/repo/data/investigations/PSI-99> | NASA PSI investigation PSI-99 | Official PSI investigation link/identifier only; response is the PSI application shell |
| `psi-bass-ii` | `src-ntrs-bass-metadata` | <https://ntrs.nasa.gov/api/citations/20210011385> | NASA NTRS citation metadata for BASS-II | Official NTRS metadata and abstract supporting hardware, sensors, variables, and findings |
| `psi-bass-ii` | `src-ntrs-bass-ii` | <https://ntrs.nasa.gov/api/citations/20210011385/downloads/TM-20210011385.pdf> | Burning and Suppression of Solids-II (BASS-II) Summary Report | Official publication URL; **unavailable locally because transfer was incomplete** |
| `psi-flex` | `src-ntrs-flex` | <https://ntrs.nasa.gov/api/citations/20130014061/downloads/20130014061.pdf> | Methanol Droplet Combustion in Oxygen-Inert Environments in Microgravity | FLEX fuels, apparatus, oxygen/pressure ranges, diluents, diagnostics, variables, LOI finding |
| `psi-flex` | `src-ntrs-flex-results` | <https://ntrs.nasa.gov/api/citations/20150023456/downloads/20150023456.pdf> | Detailed Results from the Flame Extinguishment Experiment (FLEX) March 2009 to December 2011 | FLEX hardware, diagnostics, procedures, and reported test scope |
| `psi-bass-ii`, `psi-flex` | `src-nasa-combustion-areas` | <https://www.nasa.gov/physical-sciences-informatics-psi/psi-investigations-by-research-area/> | PSI Investigations by Research Area | Official NASA portfolio membership and names, not experimental measurements |

The normalized records are [data/psi_starter.json](./data/psi_starter.json). The source inventory is [data/source_inventory.json](./data/source_inventory.json).

## Raw file inventory

All files below are under [data/raw/nasa/](./data/raw/nasa/) and were downloaded from official NASA/NTRS endpoints. The downloader refuses to overwrite an existing file and validates PDF signatures/EOF markers.

| File | Source URL | Downloaded at | Size | SHA-256 | Status |
|---|---|---|---:|---|---|
| `20170000230.pdf` | <https://ntrs.nasa.gov/api/citations/20170000230/downloads/20170000230.pdf> | `2026-11-14T10:33:30.061869Z` | 556,175 | `34c6a5a3a2f3dcca7eec796596dee842a59d029635416cbf5b4916516bd7218c` | Verified original PDF |
| `20130014061.pdf` | <https://ntrs.nasa.gov/api/citations/20130014061/downloads/20130014061.pdf> | `2026-11-14T10:51:50.048102Z` | 2,314,383 | `1488bbb461f2ea0f97c2c2fab6ac0a01603a6837509ab6ac6d1ef02bbf72050b` | Verified original PDF |
| `20150023456.pdf` | <https://ntrs.nasa.gov/api/citations/20150023456/downloads/20150023456.pdf> | `2026-11-14T10:55:16.796137Z` | 42,900,650 | `b4f6ca983e2792c33a0b92220a791a818f426bb635b94f7fd33dc8c9c471e79d` | Verified original PDF |
| `20210011385.json` | <https://ntrs.nasa.gov/api/citations/20210011385> | `2026-11-14T10:58:08.292380Z` | 7,042 | `3fcf1e93014a6c0e210bc77714c5a7f95b0ccbedb7e28390184e051d517ab9e9` | Verified original NTRS metadata response |

The machine-readable manifest is [data/raw/nasa/source_manifest.json](./data/raw/nasa/source_manifest.json). The timestamps are filesystem acquisition timestamps recorded immediately after download, not NASA publication dates.

### Missing source file

`TM-20210011385.pdf` remains unavailable locally:

- URL: <https://ntrs.nasa.gov/api/citations/20210011385/downloads/TM-20210011385.pdf>
- Server-reported length: 48,972,416 bytes
- Transfer received: 41,054,208 bytes
- Resume attempt: rejected because the server did not support byte ranges
- Required manual action: download the PDF manually, verify the PDF opens and the SHA-256, then update the manifest and record.

## Provenance implementation

- Extended the existing `Source` model with `local_file_path`, `downloaded_at`, `sha256`, `file_size_bytes`, `mime_type`, `last_verified_at`, and `verification_status`.
- Extended `SourceCitation` so scenario/report responses retain file provenance.
- Added [download_nasa_sources.py](./backend/app/download_nasa_sources.py), which uses exact NTRS download URLs, refuses silent overwrites, validates files, hashes them, and records unavailable sources.
- Added `validate_source_files()` to verify existence, byte size, and SHA-256 before CLI import.
- Re-imported the four records into the existing SQLite store with the explicit `--replace` flag; no migration was needed because the database stores canonical JSON payloads.
- Frontend detail citations now show verification status and whether an original file is preserved. Additional conditions and last verification time are displayed.

## API and frontend verification

The live API was queried after re-import:

- `GET /api/investigations` returned `4`.
- `GET /api/investigations/psi-flex` returned both verified PDF paths, MIME types, hashes, and `verification_status: "verified"`, plus the unverified PSI portfolio source.
- `GET /api/measurements` returned `{ "items": [] }`.
- No API route contains a production hardcoded investigation list.
- The frontend requests catalog data through [src/api.ts](./src/api.ts), renders it in [src/App.tsx](./src/App.tsx), and links source URLs from the returned records.

## Measurement audit

**Status: PASS for no-synthetic-data behavior; EMPTY for verified numeric observations.**

The production measurements table contains zero rows. No numeric observation was created from prose findings. Statements such as BASS-II heat-release results and FLEX limiting-oxygen results remain source-backed findings, not measurement rows. A future measurement import must include source ID, value, unit, extraction status, and page/table/figure/section evidence.

## PSI extraction status

**PARTIAL / NOT RELIABLE FOR DIRECT RECORD EXTRACTION.**

The PSI URLs are official and reachable, but returned the Angular application shell in this environment. The PSI client exposed a public repository service base (`/geode-py/ws`) and a studies list, but direct study detail access returned an authorization response. No access control was bypassed and no aggressive scraping was performed. PSI detail payloads were therefore not treated as extracted records. The project retains PSI links as unverified navigation/provenance references and uses preserved NTRS evidence for supported facts.

## Mock-data separation

No production mock investigation or synthetic measurement was found. The only mock-like record is the explicitly isolated test fixture in [backend/tests/conftest.py](./backend/tests/conftest.py), stored in a temporary test database. README examples use `example.nasa.gov`/`example.test` but are not imported.

## Tests and build

- Backend: **17 tests passed**
- Frontend production build: **passed**
- Starter ingestion: **4 investigations, 0 measurements, 0 ingestion issues**
- File validation: **all declared preserved files passed existence, size, and SHA-256 checks**
- API provenance check: **passed**

## Category status

| Category | Status | Reason |
|---|---|---|
| Original NASA file preservation | **PARTIAL** | Three publication PDFs and one official metadata JSON preserved; BASS-II publication PDF unavailable. |
| File-level hashes and sizes | **PASS** | Manifest and source records contain computed hashes and sizes; validation passes. |
| Source-to-investigation traceability | **PARTIAL** | SAFFIRE/FLEX complete; BASS-II has metadata-file traceability but not the publication PDF. |
| Verified datasets/CSVs | **FAIL / 0** | No original numeric dataset was publicly retrieved and verified. |
| Verified measurements | **PASS / EMPTY** | No measurements are displayed or stored, preventing synthetic claims. |
| API provenance exposure | **PASS** | Source file status, path, MIME type, and citations flow through API. |
| Frontend provenance display | **PASS / PARTIAL** | Status and preserved-file indicators display; local paths are not download links. |
| PSI direct extraction | **PARTIAL** | Official shell/repository endpoints observed; detail payload extraction remains unavailable without authenticated access. |
| Overall remediation | **PARTIAL** | Genuine NASA files are now preserved, but one publication and all numeric datasets remain blocked. |

