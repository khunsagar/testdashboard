"""
GitHub webhook receiver — REAL implementation.

Verifies X-Hub-Signature-256 (HMAC-SHA256) against GITHUB_WEBHOOK_SECRET,
then processes `workflow_run` events to sync execution status.

This is the "reliability" half of the hybrid design: even if a workflow
crashes before its Notify Finish step, GitHub's webhook still tells us
the run completed/failed.
"""

import hashlib
import hmac

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.services.execution_service import ExecutionService

router = APIRouter()


def verify_signature(payload_body: bytes, secret: str, signature_header: str | None) -> None:
    """Reject the request unless the HMAC signature matches. Never skip this."""
    if not signature_header:
        raise HTTPException(status_code=401, detail="Missing X-Hub-Signature-256 header")

    expected = "sha256=" + hmac.new(
        secret.encode("utf-8"), payload_body, hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, signature_header):
        raise HTTPException(status_code=401, detail="Invalid signature")


@router.post("/github")
async def github_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_hub_signature_256: str | None = Header(default=None),
    x_github_event: str | None = Header(default=None),
):
    settings = get_settings()
    body = await request.body()
    verify_signature(body, settings.github_webhook_secret, x_hub_signature_256)

    payload = await request.json()

    # We only care about workflow_run lifecycle events for now.
    if x_github_event != "workflow_run":
        return {"received": True, "processed": False, "reason": f"ignored event: {x_github_event}"}

    action = payload.get("action", "")
    run = payload.get("workflow_run", {}) or {}
    github_run_id = str(run.get("id", ""))
    conclusion = run.get("conclusion")  # success / failure / cancelled / None while running

    if not github_run_id:
        return {"received": True, "processed": False, "reason": "no workflow_run.id in payload"}

    service = ExecutionService(db)
    execution = service.apply_github_workflow_event(github_run_id, action, conclusion)

    if execution is None:
        # No matching row: workflow ran without a Notify Start step.
        # (Later phase: auto-create the execution here instead of ignoring.)
        return {"received": True, "processed": False, "reason": "no matching execution"}

    return {"received": True, "processed": True, "execution_id": str(execution.id)}
