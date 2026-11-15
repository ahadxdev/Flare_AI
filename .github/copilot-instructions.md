# Copilot Instructions

Follow the repository guidance in [AGENTS.md](../AGENTS.md). Use
[docs/architecture.md](../docs/architecture.md) and
[docs/development.md](../docs/development.md) for verified implementation and
workflow details; use the
[NASA provenance audit](../NASA_DATA_PROVENANCE_AUDIT.md) for source status.

Treat `backend/app/models.py` as the backend schema source of truth and
`api/openapi.json` as its generated contract. Frontend types in `src/api.ts`
are manually mirrored. Preserve scientific provenance and the constraints in
`AGENTS.md`; never fabricate NASA facts or citations.

For code changes, inspect the current worktree first, update relevant docs,
and run the focused existing checks. Do not edit application code for
documentation-only requests.
