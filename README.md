# FLARE AI

FLARE AI (Fire & Life-safety Analysis and Research Engine) is an evidence-first science-intelligence prototype for exploring NASA Physical Sciences Informatics (PSI) microgravity combustion research. It ranks **research relevance**, not fire risk, and never treats microgravity data as proven partial-gravity performance.

## What is implemented

- React, Vite, and TypeScript client for investigation browsing, record comparison, hypothetical scenario analysis, verified measurements, evidence-aware chat, and research briefs.
- Modular FastAPI API with Pydantic request/response validation and consistent JSON errors.
- Reusable canonical schemas in `backend/app/models.py`, service protocols and SQLite implementation in `backend/app/services.py`, and independently testable routers under `backend/app/routers/`.
- SQLite-backed canonical investigation and source-linked measurement catalog.
- Preserved NASA NTRS source files under [`data/raw/nasa/`](./data/raw/nasa/) with
  SHA-256 manifests and explicit unavailable-source records.
- Environment-configurable CORS and JSON-structured request/error logging.
- Published OpenAPI contract at [`api/openapi.json`](./api/openapi.json); regenerate it after API changes with `cd backend && python export_openapi.py`.

- Transparent relevance components for objective alignment, comparable oxygen/pressure metadata, numeric-data usefulness, and context/hardware. Unknown context is scored as zero rather than inferred.
- The starter catalog contains four NASA-linked combustion investigations and preserved NTRS source artifacts. It does not ship fabricated NASA records. The Moon Base example values (30% oxygen and 10.2 psi) are explicitly user-entered hypothetical assumptions.
- Transparent relevance components for objective alignment, comparable oxygen/pressure metadata, numeric-data usefulness, and requested material/fuel context.
- Empty catalog by default. This repository does not ship fabricated NASA records. The Moon Base example values (30% oxygen and 10.2 psi) are explicitly user-entered hypothetical assumptions.


The starter catalog has investigation documents and metadata but no verified numeric dataset rows. The measurement list is therefore empty, and chat fails closed with `NO_EVIDENCE` until verified document excerpts can be indexed. The importer accepts canonical investigations and measurements; each measurement must reference a source already attached to its investigation.

The research-relevance score uses the configured objective, parameter, measurement, and context/hardware components with default weights of 40%, 30%, 20%, and 10%. The weights are centralized in `DEFAULT_RELEVANCE_WEIGHTS` in `backend/app/services.py` and may be overridden when constructing `SQLiteResearchService`; custom weights must be finite, non-negative, and sum to 1. For the available components, the formula is `100 * sum(component_score * available_weight) / sum(available_weight)`, rounded to two decimal places. A component that is unavailable is excluded, not treated as either a match or mismatch. When only some requested oxygen/pressure values are comparable, the parameter component's weight is reduced in proportion to the comparable requested values. The response includes `evidence_completeness`, which is the fraction of total configured weight supported by available evidence; if no component is available, score and completeness are both 0.

Objective match uses exact research-area alignment; the general objective has no specific objective component. Parameter similarity averages normalized closeness only across requested oxygen/pressure fields that can be compared; pressure is converted only for supported units (psi, kPa, bar, atm). Missing values are returned as `null` score-breakdown components and described in limitations. Measurement usefulness is 1 only when actual measurement observations in the store link to a source attached to that investigation. A `numeric_dataset` declaration without such observations is not enough to score the component; the response explains that the dataset is declared but observations are unavailable. Context/hardware is available only when a material/fuel is requested and the record reports materials; an actual non-match scores 0, while absent materials remain unavailable. Equal scores are ordered by stable investigation ID. This is research relevance only, not fire risk, probability, or safety certification.

## Run locally

Python 3.10+ and Node.js 20+ are recommended.

```bash
# Terminal 1: API
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
cd backend
uvicorn app.main:app --reload --env-file ../.env

# Terminal 2: frontend (from repository root)
npm install
npm run dev
```

The client runs at `http://localhost:5173`, proxies `/api` to FastAPI on port 8000, and the interactive API documentation is at `http://localhost:8000/docs`. Configure allowed origins, methods, headers, credentials, log level, and the database path in `.env`; see [`.env.example`](./.env.example). If credentials are enabled, wildcard CORS origins are rejected.

## Import verified catalog records

The ingestion pipeline accepts manually curated JSON or CSV and normalizes it into the canonical models without scraping PSI. It assigns deterministic IDs when they are omitted (`psi-...`, `src-...`), validates enums, HTTPS provenance and measurement references, reports duplicates, and leaves unknown scientific values empty. If original source files are available, pass `--source-dir` and `--archive-dir`; files are copied byte-for-byte and SHA-256 hashes are recorded in the report.

```json
{
  "investigations": [
    {
      "title": "Curated investigation title",
      "research_area": "other",
      "environment": "unknown",
      "data_availability": "metadata_only",
      "sources": [
        {
          "document_title": "Official source document",
          "source_url": "https://example.nasa.gov/source",
          "source_type": "NASA_PSI",
          "page_number": null,
          "section": "Metadata"
        }
      ]
    }
  ],
  "measurements": []
}
```

Run the importer from the `backend` directory:

```bash
python -m app.import_data ../data/psi_starter.json --replace --report ../data/ingestion-report.json
# Add original documents without changing them:
python -m app.import_data /path/to/records.csv --source-dir /path/to/source-documents --archive-dir ../data/source-archive
```

The verified starter source manifest can be regenerated without overwriting
existing files:

```bash
python -m app.download_nasa_sources --output-dir ../data/raw/nasa --manifest ../data/raw/nasa/source_manifest.json
```

The BASS-II report PDF is listed as unavailable in the manifest because the
public transfer ended before the server-reported content length and the server
did not support byte-range resume. The official NTRS metadata JSON is preserved
instead; download the report manually from its manifest URL before marking that
publication file verified.

The starter catalog in [`data/psi_starter.json`](./data/psi_starter.json) contains curated NASA combustion investigations: SAFFIRE-I, SAFFIRE-II, BASS-II, and FLEX. Technical details are linked to NASA Technical Reports Server abstracts and the official PSI research-area page. Scalar fields remain null when the source reports a range or does not publish a value; ranges and contextual details are retained in `conditions.other`. The source inventory is [`data/source_inventory.json`](./data/source_inventory.json). Add another investigation by adding a curated JSON object or one CSV row, linking at least one HTTPS source, setting `data_availability` explicitly, and running the importer; review the generated ingestion report before loading it.

## API routes

The shared response/request schema names are defined in `backend/app/models.py`. Routers consume these same models; the generated OpenAPI document is the importable API contract for frontend and service consumers.

- `GET /api/health`
- `GET /api/investigations?q=&research_area=&environment=&data_availability=&page=&page_size=`
- `GET /api/investigations/{investigation_id}`
- `POST /api/scenarios/analyze`
- `POST /api/compare`
- `POST /api/chat`
- `GET /api/measurements?investigation_id=&variable=`
- `POST /api/reports`

Validation errors, missing records, unavailable evidence, and internal errors use `{ "error": { "code", "message", "details" } }`.

## Tests and build

```bash
PYTHONPATH=backend pytest backend/tests -q
npm run build
```

`NO_EVIDENCE` from chat is an intentional safe response: the current catalog contract stores source links and metadata but not verified excerpts that can support an answer.
