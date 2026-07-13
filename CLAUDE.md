# CLAUDE.md — Test Automation Control Plane (Backend)

## What this project is
Centralized Test Execution Platform backend (FastAPI + PostgreSQL). It is the
source of truth for ALL test executions across frameworks (Playwright, API,
Cypress...). GitHub workflows notify it on start/finish; GitHub webhooks
provide reliable lifecycle events; a Rule Engine decides which test types run.

## Architecture — STRICT layering (never violate)
```
api (routers)  ->  services  ->  repositories  ->  models (SQLAlchemy)
                      |
                 rule_engine (pure functions, NO db/http imports)
```
- Routers: HTTP validation only. No business logic, no queries.
- Services: business logic. The ONLY layer that calls rule_engine + repositories.
- Repositories: DB queries only. Never import services.
- schemas/ = Pydantic (API shapes). models/ = SQLAlchemy (DB tables). Keep separate.

## Commands
```bash
pip install -r requirements.txt
pytest tests/ -v                      # must stay green — run before every commit
uvicorn app.main:app --reload         # Swagger at /docs
```

## Conventions
- Python 3.12, type hints everywhere, Pydantic v2 (`model_validate`, `model_dump`).
- Every new feature ships with tests in tests/. No exceptions.
- DB default is SQLite placeholder (zero setup). Postgres via DATABASE_URL in .env.
- `Base.metadata.create_all` in main.py is temporary; Alembic replaces it (see STEP_BY_STEP.md Step 4).
- Secrets only via .env (gitignored). Never hardcode, never commit.
- Webhook endpoints MUST verify X-Hub-Signature-256 (see webhooks/router.py).

## Current state (implemented)
- Executions vertical slice: POST /api/v1/executions/start, GET list/detail,
  POST /{id}/finish
- Rule engine: master|main|PR -> e2e,api,regression; feature push -> unit; fallback smoke
- GitHub webhook: HMAC-verified, processes workflow_run events, correlates by github_run_id

## Roadmap (work in this order — see STEP_BY_STEP.md)
1. Postgres via .env + Alembic migrations (replace create_all)
2. Models: Project, Repository, TestResult, Artifact (copy Execution pattern)
3. Data-driven rule engine (rules as config, not nested ifs)
4. Auto-create execution rows for webhook events with no matching run
5. Auth: GitHub OAuth + JWT, roles (Admin, QA Lead, QA Engineer, Viewer)

## Rules for AI-assisted changes
- One step/feature per branch and PR. Small diffs.
- Do not add libraries without asking the lead.
- Do not touch alembic/versions manually — always autogenerate.
- If tests fail after your change, fix them before anything else.
