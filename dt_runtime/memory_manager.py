from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class MemoryManager:
    """Construye el contexto operativo desde fuentes oficiales de NINIA_OS."""

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.runtime_dir = self.root / "NINIA_OS" / "DT_RUNTIME"
        self.output_path = self.runtime_dir / "current_context.json"

    def _read_json(self, relative_path: str, required: bool = True) -> Any:
        path = self.root / relative_path
        if not path.exists():
            if required:
                raise FileNotFoundError(f"Falta fuente obligatoria: {relative_path}")
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def _read_text(self, relative_path: str) -> str | None:
        path = self.root / relative_path
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8").strip()

    @staticmethod
    def _extract_decisions(registry: Any) -> list[dict[str, Any]]:
        if isinstance(registry, list):
            items = registry
        elif isinstance(registry, dict):
            items = registry.get("decisions") or registry.get("items") or registry.get("records") or []
        else:
            items = []
        return [item for item in items if isinstance(item, dict)]

    @staticmethod
    def _active_decisions(decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        active = {"approved", "active", "aprobado", "vigente"}
        return [d for d in decisions if str(d.get("status", "")).strip().lower() in active]

    @staticmethod
    def _duplicate_ids(decisions: list[dict[str, Any]]) -> list[str]:
        seen = set()
        duplicates = set()
        for decision in decisions:
            decision_id = str(decision.get("id", "")).strip()
            if not decision_id:
                continue
            if decision_id in seen:
                duplicates.add(decision_id)
            seen.add(decision_id)
        return sorted(duplicates)

    def build_context(self) -> dict[str, Any]:
        project_state = self._read_json("NINIA_OS/DT_RUNTIME/project_state.json", required=True)
        decision_registry = self._read_json("NINIA_OS/DT_RUNTIME/decision_registry.json", required=True)
        learning_profile = self._read_json("NINIA_OS/DT_RUNTIME/learning_profile.json", required=False)
        runtime_rules = self._read_json("NINIA_OS/DT_RUNTIME/runtime_rules.json", required=False)
        current_sprint = self._read_text("NINIA_OS/CURRENT_SPRINT.md")
        roadmap = self._read_text("NINIA_OS/ROADMAP.md")

        decisions = self._extract_decisions(decision_registry)
        active_decisions = self._active_decisions(decisions)
        duplicates = self._duplicate_ids(decisions)

        context = {
            "schema_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_of_truth": "NINIA_OS",
            "project_state": project_state,
            "active_decisions": active_decisions,
            "decision_count": len(decisions),
            "active_decision_count": len(active_decisions),
            "learning_profile": learning_profile,
            "runtime_rules": runtime_rules,
            "current_sprint": current_sprint,
            "roadmap": roadmap,
            "qa": {
                "duplicate_decision_ids": duplicates,
                "passed": not duplicates,
            },
            "sources": [
                "NINIA_OS/DT_RUNTIME/project_state.json",
                "NINIA_OS/DT_RUNTIME/decision_registry.json",
                "NINIA_OS/DT_RUNTIME/learning_profile.json",
                "NINIA_OS/DT_RUNTIME/runtime_rules.json",
                "NINIA_OS/CURRENT_SPRINT.md",
                "NINIA_OS/ROADMAP.md",
            ],
        }

        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text(
            json.dumps(context, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return context

    def load_context(self) -> dict[str, Any]:
        if not self.output_path.exists():
            return self.build_context()
        return json.loads(self.output_path.read_text(encoding="utf-8"))

    def summary(self) -> dict[str, Any]:
        context = self.load_context()
        return {
            "schema_version": context["schema_version"],
            "source_of_truth": context["source_of_truth"],
            "decision_count": context["decision_count"],
            "active_decision_count": context["active_decision_count"],
            "qa_passed": context["qa"]["passed"],
            "context_path": self.output_path.relative_to(self.root).as_posix(),
        }
