from fastapi.testclient import TestClient

from api.main import app


def test_dt_health_is_automatic():
    with TestClient(app) as client:
        response = client.get("/dt/health")

    assert response.status_code == 200
    body = response.json()
    assert body["runtime"]["status"] == "ready"
    assert body["runtime"]["memory_loaded"] is True


def test_dt_plan_uses_memory_and_decision_engine():
    with TestClient(app) as client:
        response = client.post(
            "/dt/plan",
            json={
                "request": (
                    "Implementar una API Python y validar QA."
                )
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["memory_loaded"] is True
    assert body["memory_qa_passed"] is True
    assert body["decision_plan"]["lead_specialist"] == "Developer"
