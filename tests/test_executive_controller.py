from pathlib import Path
import pytest

from dt_runtime.executive_controller import ExecutiveController, ExecutiveControllerError

ROOT = Path(__file__).resolve().parents[1]

def test_health_requires_valid_memory():
    controller = ExecutiveController(ROOT)
    health = controller.health()
    assert health["status"] == "ok"
    assert health["source_of_truth"] == "NINIA_OS"
    assert health["memory_qa_passed"] is True

def test_process_always_loads_memory_first():
    controller = ExecutiveController(ROOT)
    result = controller.process("Implementar una API en Python con pruebas.")
    assert result.memory_loaded is True
    assert result.memory_qa_passed is True
    assert result.decision_plan["lead_specialist"] == "Developer"

def test_process_creates_trace():
    controller = ExecutiveController(ROOT)
    result = controller.process("Validar arquitectura.")
    assert (ROOT / result.trace_path).exists()

def test_empty_request_is_rejected():
    with pytest.raises(ValueError):
        ExecutiveController(ROOT).process("   ")

def test_evidence_approval_is_blocked():
    result = ExecutiveController(ROOT).process("Aprobar evidencia e incorporar como aprobado.")
    assert result.decision_plan["blocked"] is True

def test_controller_fails_when_context_qa_fails(monkeypatch):
    controller = ExecutiveController(ROOT)
    monkeypatch.setattr(
        controller.memory,
        "build_context",
        lambda: {"source_of_truth": "NINIA_OS", "qa": {"passed": False}},
    )
    with pytest.raises(ExecutiveControllerError):
        controller.process("Implementar módulo.")
