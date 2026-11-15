# Repository Agent Guidance

Read [README.md](README.md) for the project entry point and the relevant
documents under [docs/](docs/) before making changes.

## Source of truth

- Backend request/response and domain schemas: `backend/app/models.py`.
- Generated HTTP contract: `api/openapi.json`; regenerate it after API changes
  with `cd backend && python export_openapi.py`.
- NASA source availability and provenance: `data/raw/nasa/source_manifest.json`
  and `NASA_DATA_PROVENANCE_AUDIT.md`.
- Frontend API interfaces are manually maintained in `src/api.ts`; keep them
  aligned with the backend models/OpenAPI.

Do not duplicate canonical schemas or claim an unimplemented capability is
available. Treat worktree changes as user-owned: inspect `git status` and
preserve unrelated or uncommitted edits.

## Scientific and product constraints

- Never invent NASA values, conditions, materials, measurements, findings,
  sources, or citations. Keep unknown values unknown.
- Distinguish NASA-reported facts from generated interpretation and retain
  provenance through ingestion, API, UI, chat, and reports.
- Describe scenario scores as research relevance, never fire risk,
  probability, or safety certification.
- Do not present microgravity results as proven lunar or Martian
  partial-gravity performance. Clearly label user-entered mission values as
  hypothetical.

## Validation

Use the smallest relevant existing checks. Current backend and frontend
commands are documented in [docs/development.md](docs/development.md):

```bash
PYTHONPATH=backend pytest backend/tests -q
npm run build
```

Update directly related documentation when behavior, configuration, or API
contracts change. Do not edit application code for a documentation-only task.
