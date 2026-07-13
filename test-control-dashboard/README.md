# test-control-dashboard

Phase 1 GUI for the Test Automation Control Plane. A NiceGUI page that
talks to the `test-control-backend` API — start an execution, watch the
list refresh every 5 seconds.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# make sure the backend is running first (default http://localhost:8000)
python main.py
```

Open http://localhost:8080.

Set `BACKEND_URL` if the backend isn't on the default host/port:
```bash
BACKEND_URL=http://localhost:8000 python main.py
```

## What's here
- `main.py` — single-page dashboard: start-execution form + auto-refreshing table.
- No auth yet — matches the backend, which doesn't have auth until Phase 2.

## Not yet built
- Execution detail view (test results, artifacts, logs)
- Filtering/sorting the executions table
- Auth (once backend Phase 2 auth lands)
