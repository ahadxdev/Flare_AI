# Integration QA bug log

Audited 2026-11-15 against application commit
`93ac697b753dd9c6bff19dcfbf12804d00f5ceac`; fixes below remain open.
The [QA guide](qa.md) documents the isolated fixture, exact checks and scope.

| ID | Priority / proposed owner | Reproduction and observed result | Required behavior |
|---|---|---|---|
| QA-01 | P1 / frontend | Submit the Moon Base scenario; ranked cards display titles and citations but no investigation ID or detail-navigation control. The requested path stops at "open details". | Open the chosen investigation directly from its match using the unchanged canonical `investigation_id`; show its ID. |
| QA-02 | P2 / frontend | Open `psi-98` details. Citation rows show title, URL, section and verification status, but omit `source_id`. The same shared citation renderer is used by ranking, comparison, chat and brief. | Expose stable source IDs consistently so users can reconcile references across screens. API citation IDs and provenance are present. |
| QA-03 | P1 / backend lead | POST scenario with pressure `{value: 10.2, unit: "bananas"}`, or `{value: 10.2}`. Both return 200. Explicit empty unit returns 422. The canonical pressure model permits free text; its unit validator does not validate an omitted default. | Backend lead agrees supported units/unknown-unit behavior and ensures a unit is required when a value is supplied. Tests require 422 for these invalid scenarios; this desired behavior is not a claim that OpenAPI already specifies an enum. |
| QA-04 | P2 / backend brief owner | Generate HTML brief for `psi-98` and `psi-bass-ii`. Structured `ranked_investigations` retain IDs, but rendered/exported content omits investigation identifiers. | Include canonical investigation IDs alongside their titles in brief content, retaining source IDs and provenance. |

No canonical field names, API models, application screens, ranking behavior or
NASA records were changed to hide these failures. The strict gates in
[blockers.spec.ts](../qa/e2e/blockers.spec.ts) should remain red until the
relevant owner resolves each issue. QA-03 has two failing examples; the table
groups them as one unit-validation issue.

Implementation evidence: [ranking and citation UI](../src/App.tsx),
[canonical pressure model](../backend/app/models.py), and
[brief rendering](../backend/app/services.py).

## Validation results

Final run on 2026-11-15: **integration blocked**. The exact requested journey
cannot pass until QA-01 is resolved. All strict gates remain enabled.

- Chromium: `npm run test:e2e` — **18 passed, 5 failed**, exit 1. All five
  failures are the four open issues above; QA-03 has two examples. No skips or
  expected failures. The final run took about 1.2 minutes.
- Downstream journey with the explicitly documented Explorer detour —
  **passed**, including two-record comparison, grounded RAG, citation
  inspection and brief generation. This is not a pass for the exact journey.
- Backend: `PYTHONPATH=backend pytest backend/tests -q` — **89 passed**, two
  environment deprecation warnings (AnyIO/pytest and Starlette/httpx).
- Frontend: `npm run build` — **passed**.
- QA TypeScript: `npm run test:e2e:types` — **passed**.
- Local documentation links, `git diff --check` and editor diagnostics —
  **passed**.

Environment: Windows, Python 3.13.1, Node 23.6.0, Playwright 1.58.2 and its
Chromium build. This records the tested environment, not a new runtime support
policy. The HTML report opens with `npm run test:e2e:report`; machine-readable
results are written to the ignored `test-results/qa-results.json`.

Runtime OpenAPI and the checked frontend field names/shared enums match the
committed API contract. No field-name mismatch was found in that scope.
Stable investigation IDs and citation identity/provenance remain consistent
in the tested catalog, ranking, comparison, chat and report API responses;
the visible tracing gaps are QA-01, QA-02 and QA-04. Scientific values remain
missing where absent; the source-backed offline seed
has zero observations, and no numeric sample fallback is supplied. A separate,
explicitly synthetic chart probe verifies rendering without inventing NASA
observations. This does not certify an uninspected live database.

Known source limitation: the BASS-II publication PDF is unavailable locally,
as documented in the [manifest](../data/raw/nasa/source_manifest.json). RAG can
use its verified NTRS metadata; it must not imply that missing publication was
retrieved. External source uptime and successful external LLM synthesis are
outside this offline run.
