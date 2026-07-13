# Test Automation Control Plane — Project Brief

Read this top to bottom. It's self-contained: no other context is assumed.
Hand it to a teammate or paste it into an AI coding agent — either can pick
up from here.

## What this is

A platform that tracks every automated test run (Playwright, API, Cypress,
etc.) no matter how it started (manual, scheduled, GitHub Action). Two
repos, two phases:

1. **`test-control-backend/`** — FastAPI + PostgreSQL API, rule engine,
   GitHub webhook. Source of truth: every execution is a row in the
   `executions` table.
2. **`test-control-dashboard/`** — NiceGUI frontend that calls the backend
   API to start executions and watch them live.

## Current state (as of 2026-07-14)

Backend:
- Pushed to GitHub: https://github.com/khunsagar/testdashboard
- Runs on Python 3.12 + PostgreSQL 16 (installed locally, service
  `postgresql-x64-16`, superuser `postgres` / password `dev`, database
  `test_control`)
- Alembic owns the schema now (`alembic upgrade head`) — the old
  `Base.metadata.create_all()` placeholder in `app/main.py` has been removed
- Implemented: executions API (start/list/detail/finish), rule engine
  (master/main/PR → e2e+api+regression, feature branch push → unit only,
  fallback → smoke), HMAC-verified GitHub webhook
- 14 tests passing (`pytest tests/ -v`), using an isolated SQLite fixture
  independent of the dev Postgres DB

Dashboard:
- Single-page NiceGUI app (`main.py`): a form to start an execution, a table
  that lists executions and auto-refreshes every 5 seconds
- Verified working end-to-end against the live backend + Postgres
- No auth yet (matches backend, which has no auth until Phase 2)

## How to run everything locally

```bash
# 1. Postgres must be running (Windows service "postgresql-x64-16" starts automatically)

# 2. Backend
cd test-control-backend
python -m venv .venv && .venv\Scripts\activate      # Windows
pip install -r requirements.txt
# .env already has DATABASE_URL pointing at postgres/dev@localhost/test_control
alembic upgrade head
uvicorn app.main:app --reload                        # http://localhost:8000/docs

# 3. Dashboard (separate terminal)
cd test-control-dashboard
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
python main.py                                        # http://localhost:8080
```

## Next steps — do these in order, one at a time

Each step should be its own small PR/commit. Don't skip ahead — each one
only introduces one new unknown. Full detail for backend steps is in
`test-control-backend/STEP_BY_STEP.md` and `CLAUDE.md`; this brief is the
short version covering both repos.

### Backend

1. **More models** — copy the `Execution` pattern (model, repository,
   service, router, schema, tests) for `Project`, `Repository`,
   `TestResult`, `Artifact`. Add FK relationships
   (`Execution.project_id`, `TestResult.execution_id`). One Alembic
   migration per model.
2. **Data-driven rule engine** — `app/rule_engine/engine.py` currently
   works but isn't config-driven. Refactor rules into a `RULES`
   list/dict so a QA lead can add a rule without touching engine code.
   Keep it a pure function: no DB, no HTTP imports.
3. **Auto-create execution rows** — when a GitHub webhook arrives for a
   `github_run_id` with no matching row (e.g. a workflow that didn't call
   "Notify Start"), create the Execution row on the fly instead of
   silently ignoring it.
4. **Auth (Phase 2)** — GitHub OAuth + JWT, roles (Admin, QA Lead, QA
   Engineer, Viewer). Don't start this until 1–3 are done and stable.

### Dashboard

1. **Execution detail view** — click a row to see full detail: test
   results, artifacts, logs (once those models exist on the backend).
2. **Filtering/sorting** — filter the executions table by branch,
   status, result; sort by created_at.
3. **Wire up auth** — once backend Phase 2 lands, add a login flow and
   send the JWT on every API call.

## Rules that never change (both repos)

1. Never commit secrets — `.env` is gitignored, only `.env.example` is
   tracked.
2. Every feature ships with tests. No exceptions on the backend.
3. Backend layering is strict: router → service → (rule_engine +
   repository) → model. Never skip layers, never call upward.
4. Rule engine stays pure — no DB, no HTTP inside it.
5. Small PRs, one step per PR.
6. Don't add libraries without asking the lead.
7. Stuck for more than 2 hours → ask, with what you've tried.

## Explicitly out of scope for now

- Redis caching
- Cypress/mobile/perf runners
- AI features
- Anything not listed in "Next steps" above — say "not yet, it's in the
  plan" whenever tempted to build ahead.
