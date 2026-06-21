from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_creates_task_run() -> None:
    payload = {
        "title": "API vendor selection",
        "request": "Review the approved vendor documents, calculate cost, and prepare a cited decision brief with policy gaps.",
        "model_profile": "enterprise-balanced",
    }
    with TestClient(app) as client:
        response = client.post("/api/v1/tasks/runs", json=payload)
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["status"] == "waiting_for_review"
    assert body["verification"]["citation_coverage"] >= 0.5
