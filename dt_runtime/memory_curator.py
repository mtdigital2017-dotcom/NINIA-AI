from __future__ import annotations
import json
from pathlib import Path
from typing import Any

class MemoryCurator:
    """Carga y conserva la memoria estructurada del DT Runtime."""

    FILES = ("project_state.json", "decision_registry.json", "module_registry.json",
             "learning_profile.json", "runtime_rules.json")

    def __init__(self, root: Path):
        self.root = root
        self.runtime_dir = root / "NINIA_OS" / "DT_RUNTIME"

    def load(self) -> dict[str, Any]:
        memory: dict[str, Any] = {}
        for name in self.FILES:
            path = self.runtime_dir / name
            if not path.exists():
                raise FileNotFoundError(f"Falta memoria requerida: {path}")
            memory[name] = json.loads(path.read_text(encoding="utf-8"))
        return memory

    def write_context(self, context: dict[str, Any]) -> Path:
        path = self.runtime_dir / "current_context.json"
        path.write_text(json.dumps(context, ensure_ascii=False, indent=2), encoding="utf-8")
        return path
