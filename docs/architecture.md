# Architecture and Current Boundaries

This page describes the implementation currently present in the repository. It
does not define a future production architecture or requirements that are not
implemented.

## System flow

```text
Curated NASA metadata and preserved source files
        |
        v
Ingestion and provenance validation
        |
        v
Shared Pydantic records -> SQLite investigation/source payloads
        |                             |
        |                             +-> source-linked measurements
        |                             +-> staged measurement candidates -> review/approval
        |                             +-> extracted evidence excerpts -> FTS5
        v
Research service
  +-- metadata-based relevance ranking
  +-- comparison and measurement lookup
  +-- excerpt retrieval -> optional LLM synthesis with evidence-only fallback
  +-- metadata-based research brief
        |
        v
FastAPI routes -> React/TypeScript client
```

The ingestion pipeline validates canonical records and local source-file
provenance in [ingestion.py](../backend/app/ingestion.py). The CLI importer is
[import_data.py](../backend/app/import_data.py); PDF/metadata extraction and
excerpt generation are in [document_index.py](../backend/app/document_index.py).
The NASA source manifest is
[source_manifest.json](../data/raw/nasa/source_manifest.json).

## Backend boundaries

- Shared request and response models are defined in
  [models.py](../backend/app/models.py). The API contract is generated from the
  FastAPI application into [api/openapi.json](../api/openapi.json).
- Routers are grouped under [backend/app/routers](../backend/app/routers).
  [main.py](../backend/app/main.py) creates the app, configures CORS and
  logging, installs standard error handlers, and wires the routers.
- [services.py](../backend/app/services.py) defines the research service
  protocol and its SQLite implementation. [store.py](../backend/app/store.py)
  persists canonical Pydantic payloads in SQLite tables for investigations,
  measurements, staged measurement candidates, evidence excerpts, and scenario
  analyses.
- The default SQLite file is `backend/flare_ai.sqlite3`; it is local state and
  is git-ignored. A fresh checkout must import the starter catalog.
- Evidence search uses SQLite FTS5. It selects up to 12 terms from the user
  question, joins terms with OR, ranks excerpts with BM25, and returns at most
  eight hits by default. This is lexical retrieval; no vector database or
  embedding model is configured in the current implementation.
- When configured, the OpenAI-compatible provider receives the question and
  retrieved evidence. If it is unconfigured or fails, the service returns an
  evidence-only response. Citations are built from retrieved records and are
  checked against the response evidence.

## Research relevance and scientific boundaries

Scenario analysis ranks the imported investigation records using four
components: objective match, parameter similarity, measurement usefulness, and
context/hardware. Default weights are 0.40, 0.30, 0.20, and 0.10. Unavailable
components are excluded from the weighted average; missing oxygen, pressure,
materials, or source-linked numeric measurements are reported as limitations
rather than inferred.

For available components, the score is `100 * sum(component_score *
available_weight) / sum(available_weight)`, rounded to two decimal places.
`evidence_completeness` reports the fraction of total configured weight
supported by available components. If no component is available, both values
are zero. Objective matching uses exact research-area alignment; the general
objective has no specific objective component. Parameter similarity compares
only requested oxygen and pressure values that can be compared, and pressure
conversion is limited to psi, kPa, bar, and atm. If only some requested
parameters are comparable, the parameter component's weight is reduced in
proportion to the comparable parameters. Measurement usefulness requires
actual source-linked measurements; declaring `numeric_dataset` alone is not
enough. Equal scores are ordered by stable investigation ID.

The score is research relevance, not fire risk, probability, or a safety
verdict. Scenario inputs are hypothetical. Microgravity evidence does not
establish lunar or Martian partial-gravity performance. Do not add or document
NASA facts, measurements, or source citations without source evidence.
The Moon Base demo's 30% oxygen and 10.2 psi values are user-entered
hypothetical assumptions, not NASA measurements.

## API and client

The API currently exposes health, investigation listing/detail, scenario
analysis, comparison, chat, measurement lookup, and report creation. See
[openapi.json](../api/openapi.json) for the complete request and response
contract; do not copy schemas into this document.

The React client is under [src](../src). Route selection is hash-based in
[AppLayout.tsx](../src/components/AppLayout.tsx), and the shared fetch client
and TypeScript interfaces are in [api.ts](../src/api.ts). The TypeScript
interfaces mirror the backend models manually; they are not generated from
OpenAPI.

Comparison requires at least two distinct investigation IDs. It returns
source-linked investigation summaries and raw field values with `same`,
`different`, or `not_comparable` status. Missing/incomplete values are not
treated as equivalent; pressure values with different units are not converted
or directly compared.

The measurements endpoint returns imported numeric observations only when
their source is a verified NASA source attached to the investigation. Points
retain their original reported value and unit, observation context, source URL,
document title, and available page/section/table reference and supporting
excerpt. The Explorer plots each variable/unit group separately and labels the
plotted values as reported observations, not predictions. With no eligible
observations, the API returns an empty `data` array, the catalog
`data_availability`, and an explanation; the UI displays an empty state rather
than a placeholder chart.

The deterministic candidate scanner in
[measurement_extraction.py](../backend/app/measurement_extraction.py) reads
only local sources already marked verified, checks their size/hash, and streams
PDF pages instead of retaining a full document's extracted text. In addition
to text quantities, it parses the row/column relationships in Table IX of the
verified FLEX results report, preserving each test ID, raw numeric precision,
header units, row conditions, page, table reference, and excerpt. Missing
dash-valued cells are skipped, not replaced with zero. Approximate entries,
initial conditions, derived quantities, setup values, and boundary conditions
remain distinct review classifications; conflicts with existing approved
observations are flagged. The scanner does not digitize figure images or run
OCR. The CLI in
[measurement_review.py](../backend/app/measurement_review.py) stages candidates
idempotently, filters candidates including the 28 priority Table IX findings,
and displays source audit context alongside any matching approved measurement.
Approval requires an actual reviewer name, explicit source-review confirmation,
documented rationale and evidence notes, eligible direct-observation
classification, and original source-file verification. Burn-time approval also
requires an explicit timing-definition confirmation. A priority finding or
approved-value conflict requires a separate documented resolution confirmation.
The candidate detail view includes figure captions and quality flags so
field-of-view limitations are visible during review. Zero-valued extinction
diameters and candidates whose figure caption says no extinction diameter was
reported require an explicit resolution plus additional evidence from a
different, currently verified NASA source attached to the investigation. The
reviewer must cite a page or section and supporting excerpt; the source file's
size and hash are checked. The immutable review event retains the inspected
caption, audit flags, resolution confirmation, and supplemental source
provenance. High extraction confidence does not bypass these gates.
The SQLite `measurement_review_history` table records decisions as immutable
events; `needs_more_evidence` candidates remain outside the measurements API
and may return to review when evidence is obtained. Existing pre-history
decisions are not fabricated or backfilled. Derived quantities, approximate
values, initial conditions, setup parameters, boundary conditions, simulation
inputs, summaries, hypothetical values, and unresolved ambiguous candidates
are excluded from the direct-observation measurements dataset.

The report endpoint returns a brief string with citations, limitations, and
research gaps. It does not create a PDF or other downloadable report file.
The health endpoint returns API process status; it does not report database or
LLM-provider readiness. When chat has no relevant retrieved excerpts, it
returns `answer_status: "insufficient_evidence"` rather than inventing an
answer.

## Current data and limitations

The curated starter catalog is
[psi_starter.json](../data/psi_starter.json). The provenance status and
source-level details are recorded in
[NASA_DATA_PROVENANCE_AUDIT.md](../NASA_DATA_PROVENANCE_AUDIT.md).

As recorded in that audit, the starter set contains four investigations, four
preserved original files (three PDFs and one NTRS metadata JSON), and one
unavailable BASS-II report PDF. Three previously approved FLEX extinction
diameters remain in the measurements table. The latest candidate scan extracted
per-test values from 276 rows in FLEX report Table IX; all new candidates remain
pending human review. Two table values duplicate existing approved runs and
were suppressed; a third run reports 1.11 mm versus the already approved
1.10 mm and is flagged as ambiguous. Figures are not digitized and six PDF
pages without extractable text are not OCRed.

The Explorer uses the API's text search, research-area, environment, and
data-availability filters, plus page/page-size pagination. Selecting an
investigation opens a hash route keyed by `investigation_id` and fetches its
detail record from the API. Scenario environment and the investigation
`hardware` field are present in the contracts; confirm their intended role in
ranking before changing or documenting that behavior as a requirement.

No CI workflow, deployment configuration, charting library, or frontend
test-runner configuration is tracked in the repository.
Error: (query) Execution failed: Failed to get response from the AI model; retried 5 times (total retry wait time: 23.00 seconds) Last error: Failed native model HTTP request: error sending request for url (https://api.individual.githubcopilot.com/responses): client error (Connect): dns error: error resolving DNS: failed to lookup address information: Temporary failure in name resolution [ENOTFOUND]