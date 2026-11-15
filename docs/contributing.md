# Documentation and Collaboration Workflow

This workflow is intended for the four developers currently collaborating on
FLARE AI. It assigns documentation responsibilities by area, not by feature
part number; the repository does not define ownership or scope for the
lettered parts.

## Responsibilities

1. **Documentation coordinator:** maintains the source-of-truth map, records
   unanswered decisions, and checks that the overview links to current docs.
2. **Backend and data owner:** verifies API, Pydantic, SQLite, ingestion, and
   NASA provenance statements against code and source records.
3. **Frontend and developer-experience owner:** verifies UI behavior, setup,
   environment, and build instructions against the actual client and scripts.
4. **Integration reviewer:** checks cross-layer consistency, generated
   OpenAPI, links, and validation commands before merge.

Rotate these responsibilities as needed; the role names do not assume
individual team members or permanent ownership.

## Change workflow

- Update directly related documentation in the same pull request as the
  behavior or contract change.
- Cite or link the code, manifest, generated contract, or test that supports a
  technical statement. Mark unknowns explicitly instead of converting them
  into requirements.
- Use [models.py](../backend/app/models.py) for backend schemas and
  [openapi.json](../api/openapi.json) for the generated API contract. Do not
  maintain a second prose schema.
- Use [NASA_DATA_PROVENANCE_AUDIT.md](../NASA_DATA_PROVENANCE_AUDIT.md) and
  [source_manifest.json](../data/raw/nasa/source_manifest.json) for source
  availability and provenance; do not change a source's verification status
  based only on documentation edits.
- The code-area owner reviews technical accuracy. The integration reviewer
  checks cross-layer consistency and runs the relevant documented commands.
- The coordinator confirms links and that changes did not silently duplicate
  or contradict an existing source of truth.

## Current unresolved documentation decisions

- No blueprint or Section 18.4 is tracked in this repository.
- Ownership and requirements for the lettered product parts are not defined
  here.
- The intended Node.js support floor needs confirmation because the current
  worktree's uncommitted `skills` dependency declares Node.js `>=22.20.0`,
  while the README recommends Node.js 20+.
- Deployment target, production database choice, and external LLM provider
  privacy/retention requirements are not defined by the current local setup.
