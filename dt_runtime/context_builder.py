from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

class ContextBuilder:
    """Construye un contexto breve y verificable para la siguiente decisión."""

    def build(self, memory: dict[str, Any]) -> dict[str, Any]:
        state = memory["project_state.json"]
        decisions = memory["decision_registry.json"]["decisions"]
        modules = memory["module_registry.json"]["modules"]
        learning = memory["learning_profile.json"]
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "project": state["project"],
            "version": state["current_version"],
            "active_focus": state["active_focus"],
            "open_issues": state.get("open_issues", []),
            "approved_decisions": [d for d in decisions if d.get("status") == "APROBADA"],
            "existing_modules": [m["path"] for m in modules if m.get("status") == "EXISTS"],
            "user_level": learning["user_profile"]["level"],
            "interaction_rule": learning["user_profile"]["interaction_rule"],
        }
