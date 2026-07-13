"""
End-to-end tests of the vertical slice:
API -> service -> rule engine -> repository -> model -> DB.
Uses isolated in-memory SQLite via dependency override.
"""

import hashlib
import hmac
import json

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app

test_engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestSession = sessionmaker(bind=test_engine)
Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

SECRET = get_settings().github_webhook_secret


def sign(body: bytes) -> str:
    return "sha256=" + hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()


# ---------- Executions API ----------

def test_start_execution_manual_trigger():
    response = client.post(
        "/api/v1/executions/start",
        json={
            "workflow_name": "Regression Tests",
            "repository": "company/sample-app",
            "branch": "master",
            "event": "push",
            "actor": "sagar",
            "trigger_type": "manual",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "queued"
    # Rule engine decided the test types (master push -> full suite)
    assert body["test_type"] == "e2e,api,regression"


def test_finish_execution():
    created = client.post(
        "/api/v1/executions/start", json={"branch": "feature/x", "event": "push"}
    ).json()

    response = client.post(
        f"/api/v1/executions/{created['id']}/finish", json={"result": "success"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["result"] == "success"
    assert body["finished_at"] is not None


def test_finish_missing_execution_returns_404():
    response = client.post(
        "/api/v1/executions/00000000-0000-0000-0000-000000000000/finish",
        json={"result": "success"},
    )
    assert response.status_code == 404


def test_list_executions():
    response = client.get("/api/v1/executions/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


def test_get_missing_execution_returns_404():
    response = client.get("/api/v1/executions/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


# ---------- GitHub Webhook ----------

def test_webhook_rejects_missing_signature():
    response = client.post("/api/v1/webhooks/github", json={"action": "completed"})
    assert response.status_code == 401


def test_webhook_rejects_bad_signature():
    body = json.dumps({"action": "completed"}).encode()
    response = client.post(
        "/api/v1/webhooks/github",
        content=body,
        headers={
            "X-Hub-Signature-256": "sha256=deadbeef",
            "X-GitHub-Event": "workflow_run",
            "Content-Type": "application/json",
        },
    )
    assert response.status_code == 401


def test_webhook_completes_matching_execution():
    # Create an execution as if a Notify Start step registered it
    created = client.post(
        "/api/v1/executions/start",
        json={"branch": "master", "event": "push", "github_run_id": "9999001"},
    ).json()

    # GitHub sends workflow_run completed
    payload = json.dumps(
        {"action": "completed", "workflow_run": {"id": 9999001, "conclusion": "success"}}
    ).encode()
    response = client.post(
        "/api/v1/webhooks/github",
        content=payload,
        headers={
            "X-Hub-Signature-256": sign(payload),
            "X-GitHub-Event": "workflow_run",
            "Content-Type": "application/json",
        },
    )
    assert response.status_code == 200
    assert response.json()["processed"] is True

    detail = client.get(f"/api/v1/executions/{created['id']}").json()
    assert detail["status"] == "completed"
    assert detail["result"] == "success"


def test_webhook_ignores_unmatched_run():
    payload = json.dumps(
        {"action": "completed", "workflow_run": {"id": 424242, "conclusion": "failure"}}
    ).encode()
    response = client.post(
        "/api/v1/webhooks/github",
        content=payload,
        headers={
            "X-Hub-Signature-256": sign(payload),
            "X-GitHub-Event": "workflow_run",
            "Content-Type": "application/json",
        },
    )
    assert response.status_code == 200
    assert response.json()["processed"] is False
