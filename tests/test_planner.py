from pathlib import Path

import pytest

from cognitive.planner import Planner, PlannerError

ROOT = Path(__file__).resolve().parents[1]


def test_planner_creates_ordered_tasks():
    plan = Planner(ROOT).build(
        {
            "request": "Implementar un módulo Python.",
            "lead_specialist": "Developer",
            "support_specialists": ["QA"],
            "blocked": False,
            "reason": "Plan permitido.",
        }
    )
    assert len(plan.tasks) == 5
    assert plan.tasks[1].depends_on == ["T1"]
    assert plan.tasks[-1].depends_on == ["T4"]


def test_planner_limits_support_specialists():
    plan = Planner(ROOT).build(
        {
            "request": "Diseñar e implementar un componente.",
            "lead_specialist": "Architect",
            "support_specialists": ["Developer", "QA", "Research"],
            "blocked": False,
            "reason": "Plan permitido.",
        }
    )
    assert len(plan.support_specialists) == 2


def test_planner_blocks_automatic_evidence_work():
    plan = Planner(ROOT).build(
        {
            "request": "Aprobar evidencia automáticamente.",
            "lead_specialist": "Evidence",
            "support_specialists": ["QA"],
            "blocked": True,
            "reason": "Requiere validación humana.",
        }
    )
    assert plan.blocked is True
    assert plan.tasks[0].status == "blocked"


def test_planner_persists_plan():
    planner = Planner(ROOT)
    plan = planner.build(
        {
            "request": "Preparar un plan de pruebas.",
            "lead_specialist": "QA",
            "support_specialists": [],
            "blocked": False,
            "reason": "Plan permitido.",
        }
    )
    matches = list(
        (ROOT / "NINIA_OS" / "PLANS").glob(f"{plan.plan_id}_*.json")
    )
    assert len(matches) == 1


def test_planner_rejects_incomplete_decision():
    with pytest.raises(PlannerError):
        Planner(ROOT).build({"request": "Incompleto"})
