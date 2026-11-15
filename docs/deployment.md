# Hackathon deployment

FLARE AI is a student-built research prototype, **not affiliated with or endorsed
by NASA**. Scores express research relevance, not fire risk or safety certification.
Mission values are hypothetical; microgravity findings do not establish lunar or
Martian performance.

The demo serves the production React build and `/api` on one origin, using SQLite
and the bundled [curated catalog](../data/psi_starter.json). Startup, catalog
browsing, ranking, evidence retrieval, and briefs need no live NASA connection.
Optional LLM synthesis falls back to local excerpts on connection failure,
timeout, HTTP errors, redirects, or malformed output. When excerpts are missing,
the response explicitly reports insufficient evidence.

## Configuration

Copy [.env.example](../.env.example) to `.env` only on first setup. Example values
are public defaults or placeholders; key/model values are empty. Keep credentials
in runtime environment variables or an ignored local `.env`, never in source,
Docker build arguments, or frontend `VITE_*` variables. Process environment values
override values loaded through `--env-file`.

Set `FLARE_CORS_ORIGINS` to the **exact deployed frontend origin**, for example
`https://your-demo.example`, without a trailing slash, path, wildcard, or
credentials. For local production use `http://localhost:8000`. The actual deployed
hostname was not supplied; replace the placeholder before publishing. Credentials
remain disabled. The frontend uses relative `/api` URLs. A separately hosted
frontend must proxy `/api` to the backend; CORS alone does not configure that
proxy or authenticate clients.

Leave `FLARE_LLM_API_KEY` and `FLARE_LLM_MODEL` empty for the offline evidence-only
demo. To enable synthesis, set both on the server and use an HTTPS
`FLARE_LLM_BASE_URL`. HTTP is accepted only for loopback testing. Provider calls
send the question, hypothetical scenario, and retrieved excerpts to that endpoint;
use inputs appropriate for the provider's privacy policy.

## Native production startup

Use Python 3.13 and Node.js >=22.20.0. Local validation used Python 3.13.1 and
Node.js 23.6.0. Key Python dependencies and all direct Node dependencies are pinned;
`npm ci` uses the committed lockfile. Python transitive dependencies and container
base-image patch versions are not fully locked.

PowerShell, repository root:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
npm ci
npm run build
Copy-Item .env.example .env
# Edit .env: FLARE_CORS_ORIGINS=http://localhost:8000
$env:PYTHONPATH = 'backend'
.\.venv\Scripts\python.exe -m app.run --env-file .env --host 127.0.0.1 --port 8000
```

POSIX equivalent:

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
npm ci
npm run build
cp -n .env.example .env
# Edit .env: FLARE_CORS_ORIGINS=http://localhost:8000
PYTHONPATH=backend .venv/bin/python -m app.run --env-file .env --host 127.0.0.1 --port 8000
```

Open <http://localhost:8000>. The [entrypoint](../backend/app/run.py) loads the
environment before creating the app, uses one worker, disables Uvicorn
access/exception logging, and emits sanitized application logs. `PORT` supplies
the default port; `--port` overrides it. Use the platform's HTTPS ingress for
public access. Vite development/preview servers are not the production server.

`FLARE_DATABASE_PATH` is operator-controlled; relative paths resolve from the
working directory. Use an absolute path in a persistent writable directory on a
host. `FLARE_SEED_ON_START=true` seeds only an empty catalog, verifies local source
files, and indexes the preserved text without network calls. Existing catalogs
are preserved; invalid seed provenance aborts startup. Missing/scanned text is not
inferred. The seed retains four investigations and the existing three approved
observations. Pending candidates and synthetic QA chart data are not imported.

## Container deployment

The [Dockerfile](../Dockerfile) builds with Node and runs Python as a non-root
user. The allowlisted [.dockerignore](../.dockerignore) excludes environment files,
keys, local databases, dependencies, and QA fixtures. The runtime includes the
curated catalog and preserved sources. No provider key is needed during build.

After configuring `.env`, from the repository root (PowerShell or POSIX):

```bash
docker build --pull -t flare-ai:demo .
docker volume create flare-ai-state
docker run -d --name flare-ai --restart unless-stopped --env-file .env --env FLARE_DATABASE_PATH=/state/flare_ai.sqlite3 --mount source=flare-ai-state,target=/state -p 8000:8000 flare-ai:demo
docker inspect --format '{{json .State.Health}}' flare-ai
```

The database override is required because the example dotenv file uses a relative
path for native startup. Keep one instance/worker with this SQLite volume. These
same commands deploy on a Docker-capable host; route its HTTPS ingress to port
8000 and set `FLARE_CORS_ORIGINS=https://your-actual-frontend-host` at runtime.
For ephemeral hosting without a volume, set
`FLARE_DATABASE_PATH=/tmp/flare_ai.sqlite3`; restarts recreate the seed and lose
saved scenarios. Image pulls and dependency installation need network; the built
demo runtime operates offline once its files/image are available.

To update a running version while preserving the named database volume:

```bash
docker build --pull -t flare-ai:demo .
docker stop flare-ai
docker rm flare-ai
docker run -d --name flare-ai --restart unless-stopped --env-file .env --env FLARE_DATABASE_PATH=/state/flare_ai.sqlite3 --mount source=flare-ai-state,target=/state -p 8000:8000 flare-ai:demo
```

## Health, limits, and file access

- `GET /api/health`: process liveness, 200 with `{"status":"ok"}`.
- `GET /api/ready`: checks local database access and a non-empty catalog;
  returns a sanitized 503 when unavailable/empty. External LLM/NASA uptime does
  not affect readiness. Docker probes readiness with a 120-second startup grace.
- HTTP uploads are disabled. API mutations accept `application/json` only;
  multipart/file bodies return 415. `FLARE_MAX_REQUEST_BYTES` defaults to 65,536
  bytes, configurable from 1 KiB to 1 MiB. Streamed bytes are counted independently
  of Content-Length; oversized bodies return 413.
- `FLARE_REQUEST_TIMEOUT_SECONDS` defaults to 30 (maximum 120), including API
  body receipt and handling. A deadline exceeded before response headers returns
  504. A timeout cannot undo a completed SQLite write or terminate an
  already-running synchronous worker thread.
- `FLARE_LLM_TIMEOUT_SECONDS` defaults to 10 and must be shorter than the API
  deadline to allow fallback. Provider sockets have timeouts, redirects are
  rejected, and responses are capped at 1 MiB. Browser requests/response reads
  abort after 130 seconds. Uvicorn limits concurrency to 64 and idle keep-alive
  to five seconds. Configure ingress limits at least as strictly.
- Static serving is confined to the production build, with symlink following
  disabled. It does not expose environment files, backend source, databases,
  or archives. No API accepts a filesystem path. Operator ingestion/indexing
  CLIs resolve source paths within the repository and verify hashes/sizes.
- Application logs contain method, route template, status, duration, and
  exception class. They omit keys, bodies, raw path parameters, query strings,
  and exception text/tracebacks. Configure ingress logging similarly; hosting
  logs are outside this application process.

## Validation and rehearsal

PowerShell, repository root:

```powershell
$env:PYTHONPATH = 'backend'
.\.venv\Scripts\python.exe -m pytest backend/tests -q
npm run build
npm run test:e2e:types
```

After startup:

```powershell
Invoke-RestMethod http://localhost:8000/api/health
Invoke-RestMethod http://localhost:8000/api/ready
Invoke-RestMethod http://localhost:8000/api/investigations
Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/chat -ContentType 'application/json' -Body '{"question":"What does Saffire report about flammability and combustion?","investigation_ids":["psi-98"]}'
```

With no provider configured, chat must show local excerpts, original citations,
and the explicit fallback limitation. Disconnect external network access and
rehearse Explorer, scenarios, comparison, chat, and briefs. Original source links
and Google Fonts need network; CSS has system font fallbacks. App server/storage
outages remain visible errors. The [QA harness](qa.md) also tests a real loopback
provider timeout. [Deployment tests](../backend/tests/test_deployment.py) exercise
seeded startup and real HTTP timeout, unavailable, malformed, and redirect
responses without external provider calls.

Existing [integration blockers](qa-bugs.md) concern ranked-match navigation,
visible stable IDs, pressure units, and exported IDs. They remain open; a
successful build does not mean every browser acceptance gate passes. Public
endpoints have no authentication or per-user rate limits; leave paid synthesis
disabled for an unrestricted public demo, or add ingress access controls/quotas.

## Review verification — 2026-11-15

The review started from a clean `main` worktree at `e08e248`. The resulting
configuration was checked on Windows with Python 3.13.1 and Node.js 23.6.0:

- `PYTHONPATH=backend python -m pytest backend/tests -q`: **109 passed**,
  with existing AnyIO/pytest and Starlette/httpx deprecation warnings.
- `npm ci`, `npm run build`, and `npm run test:e2e:types`: **passed**.
- `npm run test:e2e -- qa/e2e/contract.spec.ts qa/e2e/failures.spec.ts`:
  **17 passed** in Chromium. This focused run excludes the documented blocker
  suite; it is not a full acceptance pass.
- Native `python -m app.run --env-file ...` startup and serving of the built
  frontend: **passed**, using a disposable database.
- Production-build browser smoke with external browser requests blocked:
  **passed** for dashboard, Explorer, hypothetical scenario ranking, two-record
  comparison, provider-failure chat fallback, and cited brief generation.
  The seeded catalog had four investigations, chat returned eight local evidence
  hits, and Chromium reported no JavaScript errors. The workflow used Explorer
  navigation rather than the unavailable ranked-match detail control.
- Documentation links, `git diff --check`, and editor diagnostics: **passed**.
- Container build/startup: **not verified**. Docker CLI 29.3.0 was present, but
  the Docker Desktop Linux engine was unavailable. Hosted deployment, HTTPS
  ingress, and a real frontend hostname were not available for validation.

Implementation references: [Docker multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
and [FastAPI static files](https://fastapi.tiangolo.com/tutorial/static-files/).
