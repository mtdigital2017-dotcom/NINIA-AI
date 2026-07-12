from __future__ import annotations

from pathlib import Path
from typing import Any

from .documentation_manager import DocumentationManager
from .executive_controller import ExecutiveController
from .memory_manager import MemoryManager
from .project_manifest import ProjectManifest
from .runtime_guardian import RuntimeGuardian


class BootstrapError(RuntimeError):
    """Impide iniciar NINIA si memoria, manifiesto o QA fallan."""


class RuntimeBootstrap:
    """Arranque único y obligatorio de NINIA CORE Runtime."""

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.memory = MemoryManager(self.root)
        self.manifest = ProjectManifest(self.root)
        self.executive = ExecutiveController(self.root)
        self.documentation = DocumentationManager(self.root)
        self.guardian = RuntimeGuardian(self.root)

    def run(self) -> dict[str, Any]:
        context = self.memory.build_context()
        manifest = self.manifest.build()
        guardian = self.guardian.assert_healthy()

        if context.get("source_of_truth") != "NINIA_OS":
            raise BootstrapError("La fuente de verdad no es NINIA_OS.")

        if context.get("qa", {}).get("passed") is not True:
            raise BootstrapError("La memoria no superó QA.")

        health = self.executive.health()
        documentation = self.documentation.update(
            context=context,
            manifest=manifest,
            health=health,
        )

        return {
            "status": "ready",
            "memory_loaded": True,
            "memory_qa_passed": True,
            "manifest_ready": True,
            "executive_ready": health.get("status") == "ok",
            "documentation_updated": True,
            "guardian_status": guardian["status"],
            "context_path": "NINIA_OS/DT_RUNTIME/current_context.json",
            "manifest_path": "NINIA_OS/PROJECT_MANIFEST.json",
            "automation_status_path": (
                "NINIA_OS/DT_RUNTIME/AUTOMATION_STATUS.json"
            ),
            "documentation": documentation,
        }
