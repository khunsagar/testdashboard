# Step-by-Step Build Guide — Test Automation Control Plane (Backend)

Read this top to bottom before writing any code. Each step has a
**Definition of Done** — do not move to the next step until it's met.
Everything marked PLACEHOLDER in the code is intentional: it makes the
app runnable on day one, and you replace placeholders step by step.

---

## The big picture (from the whiteboard)

```
Triggers (Manual / Scheduled / GitHub Action)
        │
        ▼
   Rule Engine  ──  decides WHICH tests run (branch + event → test types)
        │
        ▼
  Backend Service (this repo)
        │
        ├── PostgreSQL  → every execution stored here (source of truth)
        ├── Redis       → cache/session (later)
        └── S3/Blob     → artifacts, reports (later)
        ▲
        │
  ARC GitHub Runners POST results back (start/finish + webhooks)
```

One sentence to remember: **every test run, no matter how it started,
must end up as a row in the `executions` table.**

---

## Step 0 — Run what already exists (Day 1)

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest tests/ -v            # all 10 tests must pass
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs — FastAPI gives you a free Swagger UI.
Try it:

```bash
curl -X POST localhost:8000/api/v1/executions/start \
  -H "Content-Type: application/json" \
  -d '{"branch":"master","event":"push","trigger_type":"manual"}'

curl localhost:8000/api/v1/executions/
```

**Definition of Done:** tests pass, server runs, you created and listed
an execution through Swagger. No code written yet.

---

## Step 1 — Trace the vertical slice (Day 1–2, read-only)

Follow ONE request through the code, in this order:

1. `app/api/v1/executions/router.py`  — HTTP layer (validates input, nothing else)
2. `app/services/execution_service.py` — business logic (calls rule engine)
3. `app/rule_engine/engine.py`         — pure decision function (no DB, no HTTP)
4. `app/repositories/execution_repository.py` — DB queries only
5. `app/models/execution.py`           — the table definition
6. `app/schemas/execution.py`          — API request/response shapes

**The rule of the codebase:** each layer only calls the layer below it.
Router → Service → (Rule Engine + Repository) → Model. Never skip layers,
never call upward.

**Definition of Done:** you can explain to your lead, without notes, why
schemas and models are separate files.

---

## Step 2 — Add one small thing yourself (Day 2–3)

Add a `PATCH /api/v1/executions/{id}/finish` endpoint that sets
`status="completed"`, `result` (success/failure), and `finished_at`.
This mirrors the "Notify Finish" curl step every GitHub workflow will call.

You'll need to touch all the layers you traced in Step 1:
- schema: `ExecutionFinish` (result field)
- repository: `update_status()`
- service: `finish_execution()`
- router: the PATCH endpoint
- tests: at least 2 (happy path + 404)

**Definition of Done:** `pytest` green, endpoint works in Swagger.
This step proves you understand the architecture. Everything after
this is just repetition of the same pattern.

---

## Step 3 — Real PostgreSQL (Week 2)

1. Run Postgres locally (Docker is easiest):
   ```bash
   docker run -d --name pg -e POSTGRES_PASSWORD=dev -e POSTGRES_DB=test_control -p 5432:5432 postgres:16
   ```
2. Create `.env` from `.env.example`, set:
   ```
   DATABASE_URL=postgresql+psycopg2://postgres:dev@localhost:5432/test_control
   ```
3. Restart the app. The SQLite placeholder is now bypassed.

**Definition of Done:** POST an execution, then see the row with
`psql -h localhost -U postgres test_control -c "select * from executions;"`

---

## Step 4 — Alembic migrations (Week 2)

`Base.metadata.create_all()` in `main.py` is a PLACEHOLDER. Replace it:

1. `alembic revision --autogenerate -m "create executions table"`
2. `alembic upgrade head`
3. Delete the `create_all` block from `app/main.py`.

**Definition of Done:** dropping and recreating the DB, then running
`alembic upgrade head`, rebuilds the schema with no code changes.

---

## Step 5 — More models (Week 2–3)

Copy the `Execution` pattern for: `Project`, `Repository`, `TestResult`,
`Artifact`. One model → one repository → one service → one router each.
Add FK relationships (`Execution.project_id`, `TestResult.execution_id`).
One Alembic migration per model.

**Definition of Done:** each new entity has full CRUD in Swagger + tests.

---

## Step 6 — Real Rule Engine (Week 3)

Replace the placeholder logic in `app/rule_engine/engine.py` with the
whiteboard rules, and make rules data-driven (a RULES list/dict, not
nested ifs) so QA leads can add rules without touching engine code later.

Whiteboard rules to implement:
- master / main / PR merge / PPR branch → e2e, api, regression
- feature branch commit push → unit tests only
- (agree with lead on: release/* branches? schedule events?)

**Definition of Done:** every rule has its own unit test; the engine
remains a pure function (no imports from db/services).

---

## Step 7 — GitHub webhook for real (Week 3–4)

Replace the placeholder in `app/api/v1/webhooks/router.py`:
1. Verify `X-Hub-Signature-256` HMAC against `GITHUB_WEBHOOK_SECRET`
   (reject with 401 if invalid — this is NOT optional).
2. Parse `workflow_run` payload → extract `github_run_id`, status, conclusion.
3. Upsert the matching Execution row.

Test locally without GitHub using curl with a manually computed HMAC
header (write a small helper in tests for this).

**Definition of Done:** a signed fake payload updates an execution's
status; an unsigned one gets 401.

---

## Step 8 — GitHub Actions integration (Week 4)

In a sample repo, add the Notify Start / Notify Finish curl steps
(see the platform doc) pointing at your backend. Then trigger a
`workflow_dispatch` and watch the execution appear and complete.

**Definition of Done:** a real GitHub workflow run creates and closes
an execution row without any manual API calls.

---

## Rules that never change

1. **Never commit secrets.** `.env` is gitignored; only `.env.example` goes in.
2. **Every feature ships with tests** — no exceptions.
3. **Layers only call downward** (router → service → repo).
4. **Rule engine stays pure** — no DB, no HTTP inside it.
5. **Small PRs, one step per PR** — makes review possible.
6. Stuck for more than 2 hours → ask, with what you tried.

---

## What is explicitly OUT of scope for now

- NiceGUI dashboard (separate repo/phase)
- Redis caching
- Auth/JWT (Phase 2 — will be added once CRUD is stable)
- Cypress/mobile/perf runners
- AI features

Say "not yet, it's in the plan" whenever tempted.
