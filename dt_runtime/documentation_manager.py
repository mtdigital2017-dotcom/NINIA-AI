from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class DocumentationManager:
    """Actualiza automáticamente el estado documental generado por el Runtime."""

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.runtime_dir = self.root / "NINIA_OS" / "DT_RUNTIME"
        self.status_path = self.runtime_dir / "AUTOMATION_STATUS.json"

    def update(
        self,
        *,
        context: dict[str, Any],
        manifest: dict[str, Any],
        health: dict[str, Any],
    ) -> dict[str, Any]:
        status = {
            "schema_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "automation_active": True,
            "source_of_truth": context.get("source_of_truth"),
            "memory_qa_passed": context.get("qa", {}).get("passed"),
            "manifest_module_count": manifest.get("module_count"),
            "executive_health": health,
            "generated_files": [
                "NINIA_OS/DT_RUNTIME/current_context.json",
                "NINIA_OS/PROJECT_MANIFEST.json",
                "NINIA_OS/DT_RUNTIME/AUTOMATION_STATUS.json",
            ],
        }

        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        self.status_path.write_text(
            json.dumps(status, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return status
