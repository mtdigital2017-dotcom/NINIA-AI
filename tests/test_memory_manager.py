from pathlib import Path
from dt_runtime.memory_manager import MemoryManager

ROOT = Path(__file__).resolve().parents[1]

def test_builds_context_from_official_sources():
    manager = MemoryManager(ROOT)
    context = manager.build_context()
    assert context["source_of_truth"] == "NINIA_OS"
    assert "project_state" in context
    assert "qa" in context

def test_context_has_traceable_sources():
    manager = MemoryManager(ROOT)
    context = manager.build_context()
    assert context["sources"]
    assert all(source.startswith("NINIA_OS/") for source in context["sources"])

def test_context_is_persisted():
    manager = MemoryManager(ROOT)
    manager.build_context()
    assert manager.output_path.exists()
    assert manager.load_context()["schema_version"] == "1.0"

def test_summary_reports_qa_state():
    manager = MemoryManager(ROOT)
    manager.build_context()
    summary = manager.summary()
    assert "qa_passed" in summary
    assert summary["context_path"] == "NINIA_OS/DT_RUNTIME/current_context.json"
