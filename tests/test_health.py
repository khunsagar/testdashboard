"""
This is the first test the intern should be able to run successfully
(Step 1). If this passes, the environment is set up correctly.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
