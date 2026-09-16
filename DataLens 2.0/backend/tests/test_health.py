"""Smoke test — verifies the FastAPI app boots and responds.

This is the one test that isn't a TODO placeholder: it exists to
prove the scaffolding itself (config, router wiring, main.py) works
before any real feature logic is added.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_returns_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
