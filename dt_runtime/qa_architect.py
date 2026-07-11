from __future__ import annotations
from pathlib import Path
from typing import Any

class QAArchitect:
    """Valida que la memoria sea completa y coherente antes de usarla."""

    REQUIRED_CONTEXT = ("project", "version", "active_focus", "approved_decisions",
                        "existing_modules", "user_level", "interaction_rule")

    def validate(self, root: Path, context: dict[str, Any]) -> dict[str, Any]:
        errors = [f"Falta campo: {key}" for key in self.REQUIRED_CONTEXT if key not in context]
        missing_modules = [
            rel for rel in context.get("existing_modules", [])
            if not (root / rel).exists()
        ]
        errors.extend(f"Módulo registrado pero ausente: {rel}" for rel in missing_modules)
        ids = [d.get("id") for d in context.get("approved_decisions", [])]
        duplicates = sorted({x for x in ids if ids.count(x) > 1})
        errors.extend(f"Decisión duplicada: {x}" for x in duplicates)
        return {"valid": not errors, "errors": errors}
