# Development

These commands reflect the current local prototype. The backend uses SQLite;
the application imports its curated catalog into a local database rather than
fetching NASA data on startup.

## Prerequisites and version note

- Python 3.10 or newer is the version recommended in the README.
- The README recommends Node.js 20 or newer. However, the current worktree
  includes an uncommitted direct `skills` dependency whose package metadata
  declares Node.js `>=22.20.0`; application source does not import it. Confirm
  whether that dependency is intentional before treating Node 20 as a
  supported install environment. The frontend build has been verified in the
  current environment.

Dependencies are declared in [requirements.txt](../requirements.txt),
[requirements-dev.txt](../requirements-dev.txt), and
[package.json](../package.json). There is no separate frontend test or lint
script currently configured.

## Configure and run

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Start the API in terminal 1:

```bash
cd backend
python -m app.import_data ../data/psi_starter.json --replace
uvicorn app.main:app --reload --env-file ../.env
```

Start the frontend in terminal 2, from the repository root:

```bash
npm install
npm run dev
```

The UI is served at `http://localhost:5173`; Vite proxies `/api` to
`http://127.0.0.1:8000`. FastAPI's interactive docs are at
`http://localhost:8000/docs`.

The default SQLite database is `backend/flare_ai.sqlite3`. Its path can be
overridden with `FLARE_DATABASE_PATH`; relative paths are resolved from the
backend working directory. The database is local and ignored by Git.

## Environment variables

See [.env.example](../.env.example) for the complete set of supported
variables:

- `FLARE_CORS_ORIGINS`, `FLARE_CORS_ALLOW_METHODS`,
  `FLARE_CORS_ALLOW_HEADERS`, and `FLARE_CORS_ALLOW_CREDENTIALS` configure
  browser access. Wildcard origins are rejected when credentials are enabled.
- `FLARE_LOG_LEVEL` configures application logging.
- `FLARE_DATABASE_PATH` selects the SQLite database.
- `FLARE_LLM_API_KEY`, `FLARE_LLM_MODEL`, `FLARE_LLM_BASE_URL`, and
  `FLARE_LLM_TIMEOUT_SECONDS` configure the optional OpenAI-compatible chat
  provider. Leave the key and model empty for the evidence-only fallback.

When a provider is configured, chat sends the question and retrieved excerpts
to that endpoint. The repository does not specify a provider data-retention or
privacy policy; the team should confirm one before using sensitive inputs.
Never commit `.env` or provider credentials.

## Import source-backed records

The importer accepts curated JSON or CSV records and validates them against
the shared models in [models.py](../backend/app/models.py). JSON can include
`investigations`, `measurements`, and `evidence_excerpts`; measurements and
excerpts must reference a source attached to the corresponding investigation.
The importer validates enums and HTTPS provenance, reports duplicates, can
assign deterministic IDs when IDs are omitted, and preserves missing
scientific values rather than filling them with zero or inference.

Run import commands from `backend/`:

```bash
python -m app.import_data ../data/psi_starter.json --replace --report ../data/ingestion-report.json
python -m app.import_data /path/to/records.csv --source-dir /path/to/source-documents --archive-dir ../data/source-archive
```

Use `--replace` only when intentionally replacing the local catalog. Verified
local PDF and NASA metadata files are checked against recorded size and
SHA-256 before extraction. Original source files are preserved; the importer
does not scrape PSI.

## Extract and review numeric candidates

The measurement pipeline scans only locally preserved sources whose records
are marked verified. It stages candidates separately from measurements; the
Part H API does not expose pending candidates. From `backend/`, run:

```bash
python -m app.measurement_review scan
python -m app.measurement_review list --status pending_review \
  --classification experimental_observation \
  --source-id src-ntrs-flex-results
python -m app.measurement_review list --priority --status pending_review
python -m app.measurement_review show CANDIDATE_ID
python -m app.measurement_review history CANDIDATE_ID
python -m app.measurement_review review CANDIDATE_ID \
  --decision needs-more-evidence --reviewer "Actual Reviewer" \
  --rationale "Explain what remains unresolved." \
  --evidence-notes "Record the source pages, figures, and excerpts inspected."
python -m app.measurement_review review CANDIDATE_ID \
  --decision approve --reviewer "Reviewer Name" \
  --classification experimental_observation \
  --confirm-source-review \
  --rationale "Explain why this is an eligible direct observation." \
  --evidence-notes "Record the PDF page, table row, and supporting evidence checked."
python -m app.measurement_review review CANDIDATE_ID \
  --decision reject --reviewer "Reviewer Name" \
  --rationale "Explain why this candidate is not eligible." \
  --evidence-notes "Record the source evidence inspected."
```

Replace the candidate ID and reviewer with the actual candidate and person who
checked the original document; placeholder or unknown reviewer names are
rejected. `--notes` remains an alias for `--rationale`. Every review decision
requires rationale and evidence notes. `list` supports `--priority`,
`--classification`, `--source-id`, `--investigation-id`, `--variable`, and
`--status` filters. The priority queue is read from the latest
[Table IX audit CSV](../data/reports/table_ix_review_audit.csv); its 28
ambiguous candidates include the original source excerpts, PDF pages, table
rows, figure references, source hashes, and finding rationales. The audit file
is cross-checked against the candidate's investigation, source, value, unit,
URL, and hash before it is displayed or used during review.
`--classification` filters the stored extraction classification;
`--audit-classification` filters the scientific classification in the Table IX
audit without silently rewriting existing candidate records.

`show` prints the candidate's provenance and flags, its row from the scientific
audit when available, any matching already-approved run (including its own
source and excerpt), and recorded review history. `history` displays only the
append-only decisions. Prior approvals made before the history feature have no
fabricated history event; the candidate's existing reviewer attribution,
timestamp, and notes remain as stored.

Approval requires an actual reviewer name, non-empty rationale and evidence
notes, `--confirm-source-review`, an eligible
`experimental_observation` classification, an exact supporting excerpt, and
current source-file size/hash verification. A classification change requires
`--classification-reason`. Burn-time approval additionally requires
`--confirm-measurement-definition` after checking the source's timing
definition/reporting convention. A Table IX priority candidate requires
`--resolve-priority`; a candidate flagged against an existing approved value
also requires `--resolve-conflict` and a documented source comparison.
The candidate detail view includes the audit's figure reference, caption, and
quality flags when available, so field-of-view limitations are visible before
review. A zero-valued extinction diameter additionally requires
`--resolve-zero-extinction-diameter` and separately cited supporting evidence.
An audit caption stating that no extinction diameter was reported likewise
requires additional supporting evidence before approval. In either case, cite
the additional NASA source with `--additional-evidence-source-id`, its page or
section and excerpt, and pass `--confirm-additional-evidence-review`. The
additional source must be a different, currently verified source attached to
the investigation; its local file size and SHA-256 are checked. The review
history records the figure caption, audit flags, resolution confirmation, and
additional source provenance. A checkbox or high extraction-confidence score
alone does not resolve a scientific conflict.
Derived quantities, approximate values, boundary conditions, initial
conditions, and setup parameters cannot enter the direct-observation
measurements dataset. They may be reviewed, classified, rejected, or marked as
needing more evidence without being silently promoted to observations.

`needs_more_evidence` preserves the candidate outside the measurements API and
can be revisited after additional evidence is obtained. Approved and rejected
decisions are terminal in this CLI. Every completed decision is recorded in
`measurement_review_history`; database triggers reject updates and deletes to
that table. The SQLite store creates the table and triggers idempotently on
initialization. Existing candidate and measurement payloads are not
reclassified or backfilled by this schema migration. Re-running `scan` remains
idempotent. Use `--database PATH` before the command to select a non-default
SQLite file.

For the currently preserved sources, the scanner processes three verified
NASA PDFs plus the verified BASS-II NTRS metadata JSON. It streams text/layout
one PDF page at a time and parses the explicitly tabular rows in Table IX of
`20150023456.pdf` (PDF pages 26–34). That table contains individual FLEX test
conditions and per-test result fields; values retain the table's reported
precision and units. The table parser keeps the row's FLEX test ID, engineering
identifier, fuel, conditions, test-end status, source excerpt, page, and table
reference together. A dash-valued cell is omitted; approximate values remain
ambiguous and blocked from approval. Existing approved runs are deduplicated
against the table; differing values for the same run are flagged for review,
not merged or converted.

The scanner does not OCR pages without a text layer or digitize figure-only
values. It reports page-level extraction failures, blank-text pages, rejected
quantities, and unavailable/unverified sources. Table rows are source-backed
candidates, not approved measurements; pending candidates are never exposed by
the Part H API.

If a previous database contains placeholder reviewer labels and the original
reviewer cannot be established, the explicit metadata correction is:

```bash
python -m app.measurement_review correct-reviewer-placeholders \
  --confirm-reviewer-attribution-unknown
```

It clears only known placeholder names, preserves measurement values, approval
status and original review timestamps, and appends an audit note. It does not
assert who performed the review.

The source downloader can refresh manifest entries without overwriting
existing files:

```bash
python -m app.download_nasa_sources --output-dir ../data/raw/nasa --manifest ../data/raw/nasa/source_manifest.json
```

The BASS-II report PDF is currently marked unavailable in the manifest. Do not
mark an incomplete download verified.

## Validation and API contract

From the repository root:

```bash
PYTHONPATH=backend pytest backend/tests -q
npm run build
```

There is no configured frontend unit/e2e test runner, linter, or CI workflow.
Backend tests use temporary SQLite databases and test-only fixtures.

When backend API models or routes change, regenerate the OpenAPI contract:

```bash
cd backend
../.venv/bin/python export_openapi.py
```

The generated contract is at [api/openapi.json](../api/openapi.json). The
backend Pydantic models are canonical; frontend interfaces in
[src/api.ts](../src/api.ts) are maintained manually and should be kept
consistent.
