from pathlib import Path

from fastapi.testclient import TestClient

from api.main import app
from dt_runtime.executive_controller import ExecutiveController

ROOT = Path(__file__).resolve().parents[1]


def test_executive_controller_generates_execution_plan():
    result = ExecutiveController(ROOT).process(
        "Implementar un módulo Python y validar QA."
    )

    assert result.memory_loaded is True
    assert result.execution_plan["blocked"] is False
    assert len(result.execution_plan["tasks"]) == 5
    assert result.execution_plan["tasks"][0]["id"] == "T1"


def test_blocked_decision_creates_blocked_plan():
    result = ExecutiveController(ROOT).process(
        "Aprobar evidencia e incorporar como aprobado."
    )

    assert result.decision_plan["blocked"] is True
    assert result.execution_plan["blocked"] is True
    assert result.execution_plan["tasks"][0]["status"] == "blocked"


def test_dt_plan_endpoint_returns_execution_plan():
    with TestClient(app) as client:
        response = client.post(
            "/dt/plan",
            json={
                "request": (
                    "Diseñar e implementar un componente Python."
                )
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert "decision_plan" in body
    assert "execution_plan" in body
    assert body["execution_plan"]["tasks"]
