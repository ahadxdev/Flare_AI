# Integration QA and offline demo

QA scope: the browser journey and HTTP contract, including provenance and
failure handling. Canonical fields remain defined by the
[backend models](../backend/app/models.py), generated
[OpenAPI contract](../api/openapi.json), and manually maintained
[frontend interfaces](../src/api.ts). This work changes test/demo tooling and
documentation only; it does not fix application behavior or rename fields.

## Run the checks

Install [requirements-dev.txt](../requirements-dev.txt) into your chosen Python
environment, then from the repository root:

```powershell
npm ci
npx playwright install chromium
$env:FLARE_QA_PYTHON = (Get-Command python).Source
npm run test:e2e:types
npm run test:e2e
npm run test:e2e:report
```

On POSIX shells use `export FLARE_QA_PYTHON=/absolute/path/to/python` instead.
If the chosen Python is not on PATH, set its absolute path explicitly. The
[Playwright configuration](../playwright.config.ts) starts both disposable
servers and stops them when the run ends. Ports 5178 and 8011 must be free;
existing servers are not reused. Chromium is the automated browser in this scope.

`npm run test:e2e` is a strict integration gate. Known defects in
[blockers.spec.ts](../qa/e2e/blockers.spec.ts) remain failures, without skips,
expected-failure markers, or retries. A red exit is currently expected; see the
[bug log](qa-bugs.md). Screenshots, browser state and traces are retained for
failures in the ignored test-results directory. The ignored HTML report is
opened by the report command above. Machine-readable results are also written
to the ignored `test-results/qa-results.json`.

For a focused downstream check while a frontend owner fixes navigation:

```powershell
npm run test:e2e -- qa/e2e/journey.spec.ts
```

This explicitly named test returns to Explorer after ranked matches because
the results currently provide no details control. It verifies downstream
behavior but is **not** evidence that the exact requested journey passes.
The separate strict journey gate requires stable-ID navigation directly from
the ranking.

## Seeded offline demo

Start these in separate repository-root terminals after dependencies are
installed:

```powershell
python qa/server.py
```

```powershell
npm run demo:qa
```

Open <http://127.0.0.1:5178>. A sticky **FIXTURE / OFFLINE DEMO** banner describes
the data limits. API responses carry `X-FLARE-Data-Mode: fixture-offline-demo`;
the seed profile is available at <http://127.0.0.1:8011/__qa__/info>.

The versioned [demo profile](../qa/fixtures/demo.json) selects four unchanged
records from the [curated catalog](../data/psi_starter.json), keeping actual
investigation/source IDs, URLs, missing values and provenance. The
[QA server](../qa/server.py) verifies source files against recorded hashes and
indexes the locally preserved SAFFIRE PDF and BASS-II NTRS metadata. FLEX is
browsable and ranked but its documents are outside this deliberately small
demo evidence index. Source provenance remains governed by the
[manifest](../data/raw/nasa/source_manifest.json) and
[provenance audit](../NASA_DATA_PROVENANCE_AUDIT.md).

The server uses a temporary SQLite directory, forces the external LLM
configuration off, and never reads, replaces, or copies the user's local
catalog database. On exit the demo database is discarded. No numeric
measurements are seeded; no pending review candidate is approved. This is a
repeatable source-backed fixture, not a claim about any live database.
The 30% oxygen / 10.2 psi Moon Base inputs remain hypothetical.

No successful-response cache is needed: catalog, ranking, local retrieval and
brief generation use the real backend entirely offline. Source links may
require internet access; an unavailable publication remains unavailable.
There is no automatic data fallback when the backend goes down.

The separate [chart probe](../qa/fixtures/chart.json) is synthetic, visibly
labelled **FIXTURE / not NASA**, and used only by a browser response-injection
test. It is never imported by the demo or production backend. That test checks
exact point count, reported precision, units and source identity. Chart axis
ticks are display scaling, not additional observations.

## Automated coverage

| Boundary | Check |
|---|---|
| Contract | Runtime OpenAPI equals committed contract; named frontend wire fields and shared enums match schema properties. This is not a full TypeScript-to-Pydantic type-equivalence proof. |
| Dashboard and catalog | API-derived counts; stable IDs; verified original-source label; detail route survives reload. |
| Scenario and ranking | Lunar habitat, 30%, 10.2 psi request; saved scenario context; ordered matches; nullable score components shown as unavailable; research relevance and partial-gravity limitations. |
| Comparison | Exactly two selected IDs, field-level missingness, unchanged citation identity and URLs. |
| RAG | Selected IDs and saved scenario reach chat; excerpts match citations; page/section agree with evidence; source hashes/URLs/status remain consistent. |
| Brief | Same saved scenario and selected ranking; citations retain identity/provenance; deterministic report ID on repeat; hypothetical inputs and numeric gaps disclosed. |
| Missing data and no results | Unknown scientific fields are not zero-filled; zero search matches do not overwrite dashboard total; empty backend yields no fabricated ranking or citations. |
| Numeric data | Empty dataset has no chart or points; malformed numeric response is rejected; synthetic chart probe adds no sample observations. |
| Invalid inputs | Oxygen above 100, negative pressure and empty unit rejected; browser validation errors recover after correction. Unknown or omitted units are strict failing gates. |
| Backend unavailable | Browser connection aborts show unavailable/error state without counts or records; retries recover against the actual server. |
| Source unavailable | Existing BASS-II unavailable record retained; simulated 503 opens the original URL and does not change verification status. This does not assert current external NASA uptime. |
| LLM timeout | Real provider adapter calls a loopback HTTP fixture that stalls beyond its deadline; browser receives evidence-only fallback and intact citations. |
| Stale/missing IDs | Missing investigation, stale scenario and empty comparison return canonical errors. |

## Manual smoke checklist

- [ ] Start the isolated offline demo and confirm its banner and API mode
  header. Keep it separate from the production API.
- [ ] Open Dashboard: indexed count matches the catalog response; no placeholder
  measurement count or chart appears.
- [ ] Open Explorer, browse `psi-98`, inspect its verified source URL and original
  file status. Reload its detail route; the investigation ID stays unchanged.
  Missing oxygen/pressure/sensors remain "Not reported".
- [ ] Submit Lunar habitat with 30% oxygen and 10.2 psi. Inspect the request and
  response, hypothetical label, research-relevance disclaimer, ranking order,
  source references, and unavailable score components.
- [ ] Open a ranked match's details by its stable ID. **Blocked by QA-01**;
  returning through Explorer is an explicit demo detour only.
- [ ] Select `psi-98` and `psi-bass-ii`, compare them, and check IDs, missing
  fields and original citation URLs. Visible source IDs are **QA-02**.
- [ ] Ask "What does Saffire report about flammability and combustion?" Inspect
  verbatim excerpts, source IDs in answer text, citation page/section,
  interpretation label and partial-gravity limitation. No external LLM is needed.
- [ ] Generate a brief including verified measurements. Check the saved
  scenario, both titles, original citations, hypothetical inputs and explicit
  absence of measurements. Exported investigation IDs are **QA-04**.
- [ ] Search a nonsense term, then revisit Dashboard: zero results and the full
  catalog total remain distinct. Open Verified measurements: no chart or points.
- [ ] Run failure tests for invalid units (**QA-03**), missing optional numbers,
  empty catalogs, backend down/retry, unavailable links and LLM timeout.
- [ ] Repeat in the team's target browsers/viewports before release. Automated
  execution here covers desktop Chromium only.

## Audit evidence and limits

The branch audit on 2026-11-15 began with a clean worktree at
`93ac697b753dd9c6bff19dcfbf12804d00f5ceac`. Local `main`, `origin/main`,
and the sole remote head advertised by `git ls-remote --heads origin` all
pointed to that commit. No separate frontend/backend branches were advertised;
both implementations were inspected on that shared branch. Unpublished local
branches belonging to other developers were unavailable for inspection.

The trace covered request models, OpenAPI, frontend API calls and screen state,
API routers, services/store, RAG provider, preserved sources, existing tests and
development/architecture documentation. No local ignored database was used as
evidence of production data or scientific approval.

See the [dated run results and bug log](qa-bugs.md) for the integration verdict.
