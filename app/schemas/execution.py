"""
Pydantic schemas for the Execution API — these define the request/response
shapes, separate from the SQLAlchemy model (app/models/execution.py).
Keeping them separate means the DB schema can evolve without breaking the API contract.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel


class ExecutionCreate(BaseModel):
    """What the caller sends to POST /api/v1/executions/start (Step 5)."""

    workflow_name: str | None = None
    repository: str | None = None
    branch: str | None = None
    commit_sha: str | None = None
    event: str | None = None
    actor: str | None = None
    trigger_type: str | None = None
    test_type: str | None = None
    github_run_id: str | None = None


class ExecutionFinish(BaseModel):
    """What the GitHub workflow's 'Notify Finish' step sends."""

    result: str  # success / failure / cancelled / timed_out / skipped


class ExecutionRead(BaseModel):
    """What the API returns for a single execution."""

    id: uuid.UUID
    github_run_id: str | None
    workflow_name: str | None
    repository: str | None
    branch: str | None
    test_type: str | None
    status: str
    result: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True
