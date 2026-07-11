from pathlib import Path
from dt_runtime.orchestrator import DTRuntimeOrchestrator

ROOT = Path(__file__).resolve().parents[1]

def test_runtime_refresh_is_valid():
    context = DTRuntimeOrchestrator(ROOT).refresh()
    assert context["qa"]["valid"] is True
    assert context["project"] == "NINIA-AI"
    assert context["version"] == "v1.1.0"

def test_guardian_blocks_duplicate_decision():
    result = DTRuntimeOrchestrator(ROOT).review(
        "NINIA_OS es la memoria operativa versionada del proyecto."
    )
    assert result["guardian"]["allowed"] is False
    assert "DT-001" in result["guardian"]["duplicate_decisions"]

def test_guardian_blocks_unresolved_drive_auth_proposal():
    result = DTRuntimeOrchestrator(ROOT).review(
        "Implementar OAuth para el backup de Drive."
    )
    assert result["guardian"]["allowed"] is False
    assert "ISSUE-001" in result["guardian"]["blocking_conflicts"]

def test_learning_advisor_limits_manual_steps_for_beginner():
    result = DTRuntimeOrchestrator(ROOT).review("Propuesta técnica nueva", True)
    assert result["guidance"]["max_actions"] == 1
