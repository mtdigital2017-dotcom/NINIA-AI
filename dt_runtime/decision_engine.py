from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DecisionPlan:
    request: str
    objective: str
    lead_specialist: str
    support_specialists: list[str]
    actions: list[str]
    warnings: list[str]
    blocked: bool
    reason: str
    sources: list[str]
    generated_at: str


class DecisionEngine:
    SPECIALIST_RULES = {
        "Architect": {"arquitectura", "módulo", "modulo", "roadmap", "estructura", "dependencia", "integración", "integracion"},
        "Developer": {"código", "codigo", "python", "api", "fastapi", "colab", "github", "prueba", "test", "instalar", "implementar"},
        "Evidence": {"evidencia", "doi", "cita", "referencia", "paper", "fuente", "validación humana", "validacion humana"},
        "Research": {"investigación", "investigacion", "estado del arte", "metodología", "metodologia", "benchmark"},
        "Policy": {"ley", "regulación", "regulacion", "política pública", "politica publica", "crc", "dsa", "ai act"},
        "AMI": {"ami", "alfabetización mediática", "alfabetizacion mediatica", "ciudadanía digital", "ciudadania digital", "desinformación", "desinformacion"},
        "Funding": {"financiación", "financiacion", "grant", "convocatoria", "cooperación", "cooperacion"},
        "Dashboard": {"dashboard", "visualización", "visualizacion", "indicador", "métrica", "metrica"},
        "QA": {"qa", "auditoría", "auditoria", "riesgo", "calidad", "verificar", "validar"},
    }

    EVIDENCE_APPROVAL_TERMS = {
        "aprobar evidencia",
        "aprobar documento",
        "incorporar como aprobado",
        "validar automáticamente",
        "validar automaticamente",
    }

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.runtime_dir = self.root / "NINIA_OS" / "DT_RUNTIME"
        self.context_path = self.runtime_dir / "current_context.json"
        self.registry_path = self.runtime_dir / "decision_registry.json"
        self.output_path = self.runtime_dir / "last_decision_plan.json"

    @staticmethod
    def _normalize(value: str) -> str:
        return re.sub(r"\s+", " ", value.strip().lower())

    def _load_json(self, path: Path, required: bool = True) -> Any:
        if not path.exists():
            if required:
                raise FileNotFoundError(f"Falta archivo requerido: {path}")
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def _active_decisions(self) -> list[dict[str, Any]]:
        registry = self._load_json(self.registry_path, required=True)
        if isinstance(registry, list):
            decisions = registry
        elif isinstance(registry, dict):
            decisions = registry.get("decisions") or registry.get("items") or registry.get("records") or []
        else:
            decisions = []
        active_statuses = {"approved", "active", "aprobado", "vigente"}
        return [
            d for d in decisions
            if isinstance(d, dict)
            and str(d.get("status", "")).strip().lower() in active_statuses
        ]

    def _rank_specialists(self, request: str) -> list[tuple[str, int]]:
        normalized = self._normalize(request)
        ranked = []
        for specialist, terms in self.SPECIALIST_RULES.items():
            score = sum(1 for term in terms if term in normalized)
            ranked.append((specialist, score))
        ranked.sort(key=lambda item: (-item[1], item[0]))
        return ranked

    def plan(self, request: str) -> DecisionPlan:
        if not request.strip():
            raise ValueError("La solicitud no puede estar vacía.")

        self._load_json(self.context_path, required=True)
        normalized = self._normalize(request)

        warnings = []
        blocked = False
        reason = "Plan generado correctamente."

        if any(term in normalized for term in self.EVIDENCE_APPROVAL_TERMS):
            blocked = True
            reason = "La evidencia requiere validación humana antes de aprobarse."
            warnings.append(reason)

        ranked = [item for item in self._rank_specialists(request) if item[1] > 0]
        lead = ranked[0][0] if ranked else "Architect"
        supports = [item[0] for item in ranked[1:3]] if ranked else ["QA"]

        actions = [
            "Leer current_context.json.",
            "Revisar decisiones activas.",
            "Confirmar que no exista un módulo equivalente.",
            "Definir prueba mínima.",
            "Registrar decisión y documentación.",
        ]

        if blocked:
            actions = [
                "Detener aprobación automática.",
                "Enviar a validación humana.",
                "Registrar estado EN VALIDACIÓN.",
            ]

        plan = DecisionPlan(
            request=request,
            objective=request.strip().rstrip("."),
            lead_specialist=lead,
            support_specialists=supports[:2],
            actions=actions,
            warnings=warnings,
            blocked=blocked,
            reason=reason,
            sources=[
                "NINIA_OS/DT_RUNTIME/current_context.json",
                "NINIA_OS/DT_RUNTIME/decision_registry.json",
            ],
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

        self.output_path.write_text(
            json.dumps(asdict(plan), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return plan
