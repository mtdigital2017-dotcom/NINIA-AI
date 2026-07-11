from __future__ import annotations
from typing import Any

class LearningAdvisor:
    """Adapta las instrucciones al nivel registrado sin repetir teoría innecesaria."""

    def guidance(self, context: dict[str, Any], requires_manual_action: bool) -> dict[str, Any]:
        if not requires_manual_action:
            return {"format": "resultado_directo", "max_actions": 0}
        return {
            "format": "objetivo_accion_validacion",
            "max_actions": 1 if context.get("user_level") == "principiante" else 3,
            "interaction_rule": context.get("interaction_rule"),
        }
