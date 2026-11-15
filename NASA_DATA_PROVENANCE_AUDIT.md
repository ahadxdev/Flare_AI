# FLARE AI NASA Data Provenance Audit

**Audit/remediation date:** 2026-11-15
**Scope:** Repository, ingestion code, raw source directory, normalized records, SQLite database, API responses, frontend flow, fixtures, and source manifest.

## Final status

**PARTIAL — strict original-source remediation is not complete.**

The application now preserves and hashes four original NASA-hosted source files:

- Three original NTRS PDFs for SAFFIRE and FLEX.
- One original NTRS citation-metadata JSON file for BASS-II.

The BASS-II publication PDF was requested from its official NTRS download URL, but the transfer ended at 41,054,208 bytes while the server reported 48,972,416 bytes. The server did not support byte-range resume. That incomplete file was not retained or marked verified. The official NTRS metadata response was preserved instead, and the publication remains explicitly unavailable.

The source-backed numeric-candidate scanner processes all locally preserved
verified source files. The database contains three previously approved FLEX
extinction-diameter observations; the latest scan added review candidates only
and did not approve or alter any observation value.

## Totals

| Metric | Result |
|---|---:|
| NASA-linked investigations in live database | 4 |
| Original source files preserved | 4 |
| Investigations with a preserved original NASA publication file | 3 |
| Verified datasets/CSVs | 0 |
| Verified numeric measurements | 3 |
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
| `psi-flex` | Flame Extinguishment Experiment (FLEX) | `data/raw/nasa/20130014061.pdf`; `data/raw/nasa/20150023456.pdf` | Verified PDFs | Documents | Three approved extinction-diameter observations; reviewer attribution unknown |

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
- The existing process on port 8000 was not stopped or reloaded. Its health
  route returns `{"status":"ok"}`, but its live `GET /api/measurements`
  currently returns `INTERNAL_ERROR`. The current FastAPI application was
  verified in-process: it returns the `data` contract and all three approved
  observations with source URLs, pages, sections, excerpts, and reviewer-audit
  notes. Restart the existing process to load the current code; no running
  process was modified.
- No API route contains a production hardcoded investigation list.
- The frontend requests catalog data through [src/api.ts](./src/api.ts), renders it in [src/App.tsx](./src/App.tsx), and links source URLs from the returned records.

## Measurement audit

**Status: PASS for source provenance, duplicate prevention, and review gating.**

The SQLite database contains four investigations, 2,423 candidate rows, and
three measurements. Candidate statuses are 2,420 `pending_review`, 3
`approved`, and 0 `rejected`. Database classifications are 726
`experimental_observation`, 1,385 `boundary_condition`, 284 `setup_parameter`,
25 `ambiguous`, 2 `reported_summary`, and 1 `simulation_input`. Three verified
NASA PDFs and the verified BASS-II NTRS metadata JSON were processed. The
reconciled scan contains 2,420 pending nonduplicate candidates: 2,375 newly
staged rows plus 45 pending rows from the earlier scan. The three approved
candidate records bring the database candidate total to 2,423. The
scanner examined 338 source/investigation page records (the SAFFIRE PDF is
attached to two investigations), corresponding to 328 unique PDF pages with
extractable text plus one metadata abstract. Six pages of
`20150023456.pdf` had no text layer (PDF pages 1, 6, 24, 312, 313, and 314);
OCR was not run. There were no page extraction exceptions or source-integrity
issues.

The three existing approved observations remain unchanged:

| Investigation | Run | Reported observation | Source |
|---|---:|---|---|
| `psi-flex` | `#204` | 1.10 mm extinction diameter | [20130014061.pdf](./data/raw/nasa/20130014061.pdf), PDF p. 5, section 3.1 |
| `psi-flex` | `#110` | 1.57 mm extinction diameter | [20130014061.pdf](./data/raw/nasa/20130014061.pdf), PDF p. 5, section 3.1 |
| `psi-flex` | `#263` | 1.42 mm extinction diameter | [20130014061.pdf](./data/raw/nasa/20130014061.pdf), PDF p. 5, section 3.1 |

The existing reviewer fields were the placeholders `Your Name`/`YOUR NAME`.
They were cleared from both candidate and measurement records, not replaced
with an invented person. Original review timestamps and approval status were
preserved, and an audit note records that the actual reviewer could not be
established. The UI now shows the unknown attribution and audit note.

The principal coverage expansion is Table IX, “Results by Test Number and FLEX
Identifier,” in `20150023456.pdf`, PDF pages 26–34. The row parser found 276
distinct FLEX test IDs in the extracted text. Four IDs in the 001–280 range
(156, 205, 213, and 228) do not occur in the extracted text and were not
inferred. The parser staged 2,370 Table IX candidates with the row conditions,
test ID, FLEX identifier, fuel, exact source row/header excerpt, original unit,
page, and table reference:

- 1,380 ambient pressure and gas mole-fraction boundary-condition candidates.
- 264 initial droplet diameter setup-parameter candidates.
- 723 per-test visible flame extinction diameter, burning rate, and burn-time
  result candidates.
- 3 ambiguous values: one conflicting run and two explicitly approximate
  burn-time entries (`~6` and `~9`).

All new candidates remain pending review. Table IX rows for FLEX tests 110 and
263 exactly duplicate existing approved run/value/unit records and were
suppressed. Test FLEX–204 reports 1.11 mm versus the already approved 1.10 mm;
that candidate remains ambiguous, carries a conflict flag, and cannot be
approved as a second observation. The source values were not reconciled,
rounded, converted, or overwritten.

The BASS-II abstract’s aggregate “well below 100 W” statement was classified as
a reported summary, not an individual experimental observation. The scanner
also recorded 8,671 numeric tokens without a supported unit and 452
unit-bearing quantities without a nearby recognized variable; these are
rejection counts, not unique scientific candidate counts. Three duplicate
detections within the extraction batch and five candidates matching approved
measurements were suppressed. One unavailable and four unverified sources
were skipped. No OCR or figure digitization was performed.

Database integrity checks found zero duplicate measurement IDs/groups, zero
approved measurements missing source/page/evidence provenance, zero
measurements linked to unverified sources, and zero placeholder reviewer
labels. The single BASS-II abstract candidate has no page number because the
verified source is JSON metadata, not a paginated report; its section is
`Abstract`. No new observations were approved during this scan. A repeat scan
against the unchanged source files staged zero additional candidates. No
missing value was replaced with zero.

## PSI extraction status

**PARTIAL / NOT RELIABLE FOR DIRECT RECORD EXTRACTION.**

The PSI URLs are official and reachable, but returned the Angular application shell in this environment. The PSI client exposed a public repository service base (`/geode-py/ws`) and a studies list, but direct study detail access returned an authorization response. No access control was bypassed and no aggressive scraping was performed. PSI detail payloads were therefore not treated as extracted records. The project retains PSI links as unverified navigation/provenance references and uses preserved NTRS evidence for supported facts.

## Mock-data separation

No production mock investigation or synthetic measurement was found. The only mock-like record is the explicitly isolated test fixture in [backend/tests/conftest.py](./backend/tests/conftest.py), stored in a temporary test database. README examples use `example.nasa.gov`/`example.test` but are not imported.

## Tests and build

- Backend: **69 tests passed** (`PYTHONPATH=backend .venv/bin/pytest backend/tests -q`).
- Frontend production build: **passed** (`npm run build`).
- OpenAPI/runtime contract: **passed**; regenerated with `cd backend && ../.venv/bin/python export_openapi.py`, then the full test suite confirmed the checked-in JSON exactly matches `default_app.openapi()`.
- Starter JSON ingestion: **4 investigations, 0 measurements, 0 ingestion issues**; this is separate from the live SQLite database.
- Source integrity: **all four candidate source files passed local existence and SHA-256 checks**.
- In-process measurements API: **HTTP 200, three approved FLEX observations with the current `data` contract and complete available provenance**.
- Existing port-8000 process: health returns HTTP 200, but `/api/measurements?investigation_id=psi-flex` returns HTTP 500; it was not restarted or modified.
- `git diff --check`: **passed**.

## Category status

| Category | Status | Reason |
|---|---|---|
| Original NASA file preservation | **PARTIAL** | Three publication PDFs and one official metadata JSON preserved; BASS-II publication PDF unavailable. |
| File-level hashes and sizes | **PASS** | Manifest and source records contain computed hashes and sizes; validation passes. |
| Source-to-investigation traceability | **PARTIAL** | SAFFIRE/FLEX complete; BASS-II has metadata-file traceability but not the publication PDF. |
| Verified datasets/CSVs | **FAIL / 0** | No original numeric dataset was publicly retrieved and verified. |
| Verified measurements | **PASS / 3 APPROVED** | Three pre-existing FLEX observations are retained; all new candidates remain pending review. |
| API provenance exposure | **PASS** | Source file status, path, MIME type, and citations flow through API. |
| Frontend provenance display | **PASS / PARTIAL** | Measurement values retain source labels, links, run IDs, pages/references, excerpts, and reviewer-attribution audit notes; local paths are not download links. |
| PSI direct extraction | **PARTIAL** | Official shell/repository endpoints observed; detail payload extraction remains unavailable without authenticated access. |
| Overall remediation | **PARTIAL** | Three source-backed measurements are available; one NASA publication is unavailable, figure-only observations are not digitized, and the live port-8000 measurements route must be brought onto the verified current backend before the website can display the records. |

