from pathlib import Path

import pytest

from dt_runtime.runtime_guardian import (
    GuardianBlockError,
    RuntimeGuardian,
)

ROOT = Path(__file__).resolve().parents[1]


def test_guardian_reports_healthy_repository():
    report = RuntimeGuardian(ROOT).inspect()

    assert report["status"] == "healthy"
    assert report["critical_count"] == 0


def test_guardian_creates_report():
    guardian = RuntimeGuardian(ROOT)
    guardian.inspect()

    assert guardian.report_path.exists()


def test_guardian_blocks_invalid_json(tmp_path):
    root = tmp_path / "repo"
    (root / "NINIA_OS" / "DT_RUNTIME").mkdir(parents=True)
    (root / "dt_runtime").mkdir()

    for relative in RuntimeGuardian.REQUIRED_MODULES:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# test\n", encoding="utf-8")

    for relative in RuntimeGuardian.CRITICAL_JSON:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}", encoding="utf-8")

    corrupted = (
        root
        / "NINIA_OS"
        / "DT_RUNTIME"
        / "decision_registry.json"
    )
    corrupted.write_text("{invalid", encoding="utf-8")

    guardian = RuntimeGuardian(root)

    with pytest.raises(GuardianBlockError):
        guardian.assert_healthy()
