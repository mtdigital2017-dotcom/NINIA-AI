from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ProjectManifest:
    """Genera el inventario ejecutable del proyecto NINIA-AI."""

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.output_path = self.root / "NINIA_OS" / "PROJECT_MANIFEST.json"

    def _module_records(self) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        directories = ("api", "engine", "dt_runtime", "tests", "docs")

        for directory in directories:
            base = self.root / directory
            if not base.exists():
                continue

            for path in sorted(base.rglob("*")):
                if not path.is_file():
                    continue
                if "__pycache__" in path.parts or path.suffix == ".pyc":
                    continue

                records.append(
                    {
                        "path": path.relative_to(self.root).as_posix(),
                        "category": directory,
                        "extension": path.suffix.lower(),
                    }
                )

        return records

    def build(self) -> dict[str, Any]:
        modules = self._module_records()
        manifest = {
            "schema_version": "1.0",
            "project": "NINIA-AI",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_of_truth": "repository",
            "module_count": len(modules),
            "modules": modules,
            "runtime": {
                "memory_manager": (self.root / "dt_runtime" / "memory_manager.py").exists(),
                "decision_engine": (self.root / "dt_runtime" / "decision_engine.py").exists(),
                "executive_controller": (self.root / "dt_runtime" / "executive_controller.py").exists(),
                "backup_manager": (self.root / "dt_runtime" / "backup_manager.py").exists(),
            },
        }

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return manifest

    def load(self) -> dict[str, Any]:
        if not self.output_path.exists():
            return self.build()
        return json.loads(self.output_path.read_text(encoding="utf-8"))
