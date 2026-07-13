# test-control-backend

Backend for the Test Automation Control Plane: API layer, rule engine, and
data layer for managing test executions and integrating with GitHub Actions.

This repo is scaffolded with placeholders. **Build it in this order —
do not skip ahead.** Each step only introduces one new unknown.

## Step 1 — Get it running
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```
Visit `http://localhost:8000/health` — should return `{"status": "ok", ...}`.
Then run `pytest` — `tests/test_health.py` should pass. If both work, your
environment is good and you can stop worrying about setup.

## Step 2 — Understand the folder structure (already done for you)
Every folder below has one job. Don't put logic in the wrong layer.

```
app/
├── api/            # HTTP layer only — no DB queries, no business logic
├── core/           # config, logging, exceptions — cross-cutting concerns
├── integrations/   # outbound (GitHub client) vs inbound (webhook parsing)
├── rule_engine/     # pure decision logic — no I/O, easy to unit test
├── services/        # business logic — calls rule_engine + repositories
├── repositories/     # DB queries only — no business logic
├── models/          # SQLAlchemy tables
├── schemas/          # Pydantic request/response shapes
├── db/               # engine, session, declarative base
└── cache/            # Redis client (if this service needs it directly)
```

## Step 3 — Wire up Postgres
Edit `.env` with real `DATABASE_URL`. Confirm the app can connect:
```python
from app.db.session import engine
engine.connect()  # should not raise
```

## Step 4 — First model + migration
`app/models/execution.py` is already written for you as the one table to
start with (matches the whiteboard's `workflow_run` design). Run:
```bash
alembic revision --autogenerate -m "create executions table"
alembic upgrade head
```
Confirm the `executions` table exists in Postgres before moving on.

## Step 5 — First real endpoint (the vertical slice)
Uncomment the router include in `app/main.py`:
```python
from app.api.v1.executions.router import router as executions_router
app.include_router(executions_router, prefix="/api/v1/executions", tags=["executions"])
```
Test with:
```bash
curl -X POST localhost:8000/api/v1/executions/start \
  -H "Content-Type: application/json" \
  -d '{"workflow_name": "regression", "branch": "main", "event": "push"}'
```
This proves every layer works together: api -> service -> repository -> model -> db.

## Step 6 — Rule Engine
`app/rule_engine/engine.py` has placeholder rules. Replace with real ones,
write unit tests for it in isolation (no DB needed — it's a pure function).
Then wire it into `ExecutionService.start_execution` (there's a comment
showing exactly where).

## Step 7+ — Everything else
Once Steps 1–6 work, the rest (more models, GitHub OAuth, webhooks,
reporting) follows the same pattern repeatedly. Ask before starting
Phase 6 (GitHub integration) — that needs a decision on OAuth app setup.

## Not yet implemented (by design — don't build ahead)
- `app/integrations/github/*` — Phase 6
- `app/api/v1/webhooks/*` — Phase 6
- Auth / JWT / roles — Phase 2
- Redis usage — only if this service (not just the dashboard) needs it
