from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_health_endpoint_is_available():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_knowledge_endpoint_returns_items_container():
    response = client.get("/knowledge", params={"status": "approved"})
    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload
    assert isinstance(payload["items"], list)


def test_evidence_requests_support_owner_filter():
    response = client.get(
        "/evidence/requests",
        params={"researcher_email": "nobody@example.org"},
    )
    assert response.status_code == 200
    assert response.json()["items"] == []
