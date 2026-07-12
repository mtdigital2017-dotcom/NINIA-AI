from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class GuardianBlockError(RuntimeError):
    """Impide iniciar NINIA cuando existe corrupción crítica."""


@dataclass(frozen=True)
class GuardianFinding:
    severity: str
    code: str
    path: str
    message: str


class RuntimeGuardian:
    """Valida la integridad operativa del DT Runtime.

    No modifica conocimiento aprobado.
    No restaura automáticamente archivos sin una copia verificada.
    """

    CRITICAL_JSON = (
        "NINIA_OS/DT_RUNTIME/project_state.json",
        "NINIA_OS/DT_RUNTIME/decision_registry.json",
        "NINIA_OS/DT_RUNTIME/runtime_rules.json",
        "NINIA_OS/DT_RUNTIME/current_context.json",
        "NINIA_OS/PROJECT_MANIFEST.json",
    )

    REQUIRED_MODULES = (
        "dt_runtime/bootstrap.py",
        "dt_runtime/memory_manager.py",
        "dt_runtime/decision_engine.py",
        "dt_runtime/executive_controller.py",
        "dt_runtime/project_manifest.py",
    )

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.runtime_dir = self.root / "NINIA_OS" / "DT_RUNTIME"
        self.report_path = self.runtime_dir / "GUARDIAN_REPORT.json"

    def _validate_json(
        self,
        relative_path: str,
    ) -> list[GuardianFinding]:
        path = self.root / relative_path

        if not path.exists():
            return [
                GuardianFinding(
                    severity="critical",
                    code="missing_json",
                    path=relative_path,
                    message="Archivo JSON crítico ausente.",
                )
            ]

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            return [
                GuardianFinding(
                    severity="critical",
                    code="invalid_json",
                    path=relative_path,
                    message=str(exc),
                )
            ]

        findings: list[GuardianFinding] = []

        if not isinstance(data, (dict, list)):
            findings.append(
                GuardianFinding(
                    severity="warning",
                    code="unexpected_json_root",
                    path=relative_path,
                    message="La raíz JSON no es objeto ni lista.",
                )
            )

        return findings

    def _validate_modules(self) -> list[GuardianFinding]:
        findings: list[GuardianFinding] = []

        for relative_path in self.REQUIRED_MODULES:
            if not (self.root / relative_path).exists():
                findings.append(
                    GuardianFinding(
                        severity="critical",
                        code="missing_module",
                        path=relative_path,
                        message="Módulo obligatorio ausente.",
                    )
                )

        return findings

    def _validate_manifest(self) -> list[GuardianFinding]:
        path = self.root / "NINIA_OS" / "PROJECT_MANIFEST.json"

        if not path.exists():
            return []

        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []

        runtime = manifest.get("runtime", {})

        expected = {
            "memory_manager",
            "decision_engine",
            "executive_controller",
        }

        findings: list[GuardianFinding] = []

        for name in expected:
            if runtime.get(name) is not True:
                findings.append(
                    GuardianFinding(
                        severity="critical",
                        code="manifest_runtime_mismatch",
                        path="NINIA_OS/PROJECT_MANIFEST.json",
                        message=f"El manifiesto no confirma {name}.",
                    )
                )

        return findings

    def inspect(self) -> dict[str, Any]:
        findings: list[GuardianFinding] = []

        for relative_path in self.CRITICAL_JSON:
            findings.extend(
                self._validate_json(relative_path)
            )

        findings.extend(self._validate_modules())
        findings.extend(self._validate_manifest())

        critical_count = sum(
            item.severity == "critical"
            for item in findings
        )

        report = {
            "schema_version": "1.0",
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "status": (
                "blocked"
                if critical_count
                else "healthy"
            ),
            "critical_count": critical_count,
            "warning_count": sum(
                item.severity == "warning"
                for item in findings
            ),
            "findings": [
                asdict(item)
                for item in findings
            ],
        }

        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        self.report_path.write_text(
            json.dumps(
                report,
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        return report

    def assert_healthy(self) -> dict[str, Any]:
        report = self.inspect()

        if report["critical_count"] > 0:
            raise GuardianBlockError(
                "Runtime Guardian bloqueó el inicio por "
                f"{report['critical_count']} hallazgo(s) crítico(s)."
            )

        return report
