# FLARE AI

FLARE AI (Fire & Life-safety Analysis and Research Engine) is an evidence-first science-intelligence prototype for exploring NASA Physical Sciences Informatics (PSI) microgravity combustion research. It ranks **research relevance**, not fire risk, and never treats microgravity data as proven partial-gravity performance.

## What is implemented

- React, Vite, and TypeScript client for investigation browsing, record comparison, hypothetical scenario analysis, verified measurements, evidence-aware chat, and research briefs.
- Modular FastAPI API with Pydantic request/response validation and consistent JSON errors.
- Reusable canonical schemas in `backend/app/models.py`, service protocols and SQLite implementation in `backend/app/services.py`, and independently testable routers under `backend/app/routers/`.
- SQLite-backed canonical investigation and source-linked measurement catalog.
- Environment-configurable CORS and JSON-structured request/error logging.
- Published OpenAPI contract at [`api/openapi.json`](./api/openapi.json); regenerate it after API changes with `cd backend && python export_openapi.py`.
- Transparent relevance components for objective alignment, comparable oxygen/pressure metadata, numeric-data usefulness, and requested material/fuel context.
- Empty catalog by default. This repository does not ship fabricated NASA records. The Moon Base example values (30% oxygen and 10.2 psi) are explicitly user-entered hypothetical assumptions.

The prototype has no NASA records or document excerpts bundled. Consequently, its initial investigation and measurement lists are empty, scenarios return no matches, and chat fails closed with `NO_EVIDENCE`. The importer accepts canonical investigations and measurements; each measurement must reference a source already attached to its investigation. Chat remains unavailable until verified document excerpts can be indexed.

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

Prepare a JSON file with canonical `investigations` and optional `measurements` arrays. Fields are validated against `backend/app/models.py`; every imported investigation must include at least one HTTPS source, and each measurement must match a source ID on its investigation. Do not import unverified assumptions as source facts. Source URLs and IDs are preserved through API responses and reports.

```json
{
  "investigations": [],
  "measurements": []
}
```

Run the importer from the `backend` directory:

```bash
python -m app.import_data /path/to/verified-records.json
# Add --replace to replace the existing local catalog.
```

Importing an empty example is valid and does not add records. Keep provenance and source verification with the records during curation.

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
