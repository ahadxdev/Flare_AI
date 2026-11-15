---
name: documentation-maintenance
description: Maintain repository documentation from verified code and project evidence while avoiding duplication and unsupported claims.
---

# Documentation Maintenance

Use this skill when asked to create, revise, or review project documentation.

## Workflow

1. Inspect the worktree and read the relevant implementation, tests,
   configuration, and existing documentation before editing.
2. Identify the authoritative source for each claim: code/schema, generated
   contract, manifest, test, or confirmed team decision.
3. Keep each fact in one primary location. Link to canonical schemas and
   generated API contracts instead of copying them into prose.
4. Separate implemented behavior from intended or proposed behavior. Mark
   missing decisions as open questions and ask for confirmation when they
   affect design or support policy.
5. Preserve unrelated and uncommitted changes. Make documentation-only edits
   when that is the requested scope.
6. Update directly related documentation with a behavior or configuration
   change, and avoid broad rewrites that obscure provenance or ownership.
7. Verify changed links, commands, and generated-contract instructions against
   the repository. Run documentation checks if configured; otherwise report
   why no code test was needed.

## FLARE AI constraints

- Never invent NASA data, measurements, source details, findings, or citations.
- Keep missing scientific values missing and preserve source provenance.
- Keep research relevance distinct from fire risk or safety certification.
- Do not claim microgravity results prove lunar or Martian partial-gravity
  behavior.
- Do not represent a test fixture or ignored local database as production
  data.
