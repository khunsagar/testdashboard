"""
Entry point for the Test Automation Control Plane backend.

This is intentionally minimal in Phase 1 — it wires up the app,
config, logging, and a health check. Real routers get included here
as they're built (Step 5+).
"""

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging import configure_logging

settings = get_settings()
configure_logging()

app = FastAPI(
    title="Test Automation Control Plane",
    version="0.1.0",
    description="Backend API, rule engine, and data layer for managing test executions.",
)


@app.get("/health", tags=["health"])
def health_check() -> dict:
    """Basic liveness check. Confirm this responds before building anything else."""
    return {"status": "ok", "env": settings.environment}


# --- Routers ---
from app.api.v1.executions.router import router as executions_router  # noqa: E402
from app.api.v1.webhooks.router import router as webhooks_router  # noqa: E402

app.include_router(executions_router, prefix="/api/v1/executions", tags=["executions"])
app.include_router(webhooks_router, prefix="/api/v1/webhooks", tags=["webhooks"])


# --- PLACEHOLDER table creation ---
# create_all is fine for the SQLite dev DB. In Step 7 this is REPLACED
# by Alembic migrations (`alembic upgrade head`) — never use create_all
# against real Postgres in dev/staging/prod.
from app.db.base import Base  # noqa: E402
from app.db.session import engine  # noqa: E402
from app.models import execution  # noqa: F401, E402  (import registers the model)

Base.metadata.create_all(bind=engine)
