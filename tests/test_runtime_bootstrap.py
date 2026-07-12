from pathlib import Path

from dt_runtime.bootstrap import RuntimeBootstrap

ROOT = Path(__file__).resolve().parents[1]


def test_bootstrap_loads_memory_and_manifest():
    result = RuntimeBootstrap(ROOT).run()

    assert result["status"] == "ready"
    assert result["memory_loaded"] is True
    assert result["memory_qa_passed"] is True
    assert result["manifest_ready"] is True
    assert result["executive_ready"] is True


def test_bootstrap_generates_required_files():
    RuntimeBootstrap(ROOT).run()

    assert (ROOT / "NINIA_OS" / "PROJECT_MANIFEST.json").exists()
    assert (
        ROOT
        / "NINIA_OS"
        / "DT_RUNTIME"
        / "AUTOMATION_STATUS.json"
    ).exists()
