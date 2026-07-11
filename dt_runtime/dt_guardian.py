from __future__ import annotations
from typing import Any

class DTGuardian:
    """Evita propuestas repetidas, contradicciones y trabajo sin valor nuevo."""

    def review_proposal(self, proposal: str, context: dict[str, Any]) -> dict[str, Any]:
        normalized = " ".join(proposal.lower().split())
        matches = []
        for item in context.get("approved_decisions", []):
            decision = " ".join(item.get("decision", "").lower().split())
            if normalized and (normalized in decision or decision in normalized):
                matches.append(item["id"])
        conflicts = [
            issue["id"] for issue in context.get("open_issues", [])
            if issue.get("status") == "REQUIERE_DECISION"
            and any(token in normalized for token in ("drive", "oauth", "cuenta de servicio", "backup"))
        ]
        return {
            "allowed": not matches and not conflicts,
            "duplicate_decisions": matches,
            "blocking_conflicts": conflicts,
            "message": (
                "Propuesta nueva permitida."
                if not matches and not conflicts
                else "Detener: revisar duplicidad o conflicto antes de implementar."
            ),
        }
