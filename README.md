# FLARE AI

FLARE AI (Fire & Life-safety Analysis and Research Engine) is a student-built,
evidence-first science-intelligence prototype for exploring NASA Physical
Sciences Informatics (PSI) microgravity combustion research. It ranks research
relevance, not fire risk, and does not treat microgravity findings as proven
lunar or Martian partial-gravity performance. FLARE AI is not an official NASA
system.

The prototype includes a React/TypeScript client and a modular FastAPI backend
using shared Pydantic models and a local SQLite catalog. Its current starter
dataset has four NASA-linked investigations and three approved FLEX
extinction-diameter observations. Their former placeholder reviewer labels have
been cleared and the unknown attribution is documented. Additional source-backed
candidates are staged for explicit review; they are not exposed as measurements
until approved.

## Get started

See [Development](docs/development.md) for environment setup, source import,
run commands, environment variables, and validation.

## Environment variables

The frontend uses the same-origin `/api` path and needs no separate API URL
setting in development; Vite proxies it to the backend. The backend reads
`FLARE_CORS_ORIGINS`, `FLARE_CORS_ALLOW_METHODS`,
`FLARE_CORS_ALLOW_HEADERS`, `FLARE_CORS_ALLOW_CREDENTIALS`,
`FLARE_LOG_LEVEL`, and `FLARE_DATABASE_PATH`. Optional chat synthesis uses
`FLARE_LLM_API_KEY`, `FLARE_LLM_MODEL`, `FLARE_LLM_BASE_URL`, and
`FLARE_LLM_TIMEOUT_SECONDS`. Copy `.env.example` to `.env`; see
[Development](docs/development.md#environment-variables) for descriptions and
defaults. Keep provider credentials out of version control.

## Project documentation

- [Architecture and current limitations](docs/architecture.md)
- [Development and testing](docs/development.md)
- [Numeric candidate extraction and review workflow](docs/development.md#extract-and-review-numeric-candidates)
- [Four-member documentation workflow](docs/contributing.md)
- [NASA data provenance audit](NASA_DATA_PROVENANCE_AUDIT.md)
- [Generated API contract](api/openapi.json)
- [Repository agent guidance](AGENTS.md)

The interactive API documentation is served at `http://localhost:8000/docs`
when the backend is running.
