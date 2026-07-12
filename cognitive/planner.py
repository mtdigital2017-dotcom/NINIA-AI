from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class PlannerError(RuntimeError):
    """Error de planificación cuando el objetivo no puede procesarse."""


@dataclass(frozen=True)
class PlanTask:
    id: str
    title: str
    description: str
    specialist: str
    depends_on: list[str]
    acceptance_criteria: list[str]
    status: str = "pending"


@dataclass(frozen=True)
class Plan:
    plan_id: str
    objective: str
    source_request: str
    lead_specialist: str
    support_specialists: list[str]
    tasks: list[PlanTask]
    completion_criteria: list[str]
    blocked: bool
    reason: str
    generated_at: str
    sources: list[str]


class Planner:
    """Convierte una decisión aprobada en un plan ejecutable y trazable."""

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.plans_dir = self.root / "NINIA_OS" / "PLANS"
        self.plans_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _slug(value: str) -> str:
        normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
        return normalized[:48] or "plan"

    @staticmethod
    def _plan_id(objective: str) -> str:
        import hashlib

        stamp = datetime.now(timezone.utc).isoformat()
        payload = f"{stamp}|{objective}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()[:12]

    @staticmethod
    def _validate_decision_plan(decision_plan: dict[str, Any]) -> None:
        required = {
            "request",
            "lead_specialist",
            "support_specialists",
            "blocked",
            "reason",
        }
        missing = sorted(required - set(decision_plan))
        if missing:
            raise PlannerError(
                "El Decision Engine no entregó campos obligatorios: "
                + ", ".join(missing)
            )

    def build(self, decision_plan: dict[str, Any]) -> Plan:
        self._validate_decision_plan(decision_plan)

        request = str(decision_plan["request"]).strip()
        if not request:
            raise PlannerError("La solicitud no puede estar vacía.")

        blocked = bool(decision_plan.get("blocked"))
        reason = str(decision_plan.get("reason", ""))

        if blocked:
            tasks = [
                PlanTask(
                    id="T1",
                    title="Detener ejecución automática",
                    description=(
                        "Conservar el elemento en estado EN VALIDACIÓN "
                        "hasta decisión humana."
                    ),
                    specialist="Evidence",
                    depends_on=[],
                    acceptance_criteria=[
                        "No se modifica conocimiento aprobado.",
                        "La revisión humana queda registrada.",
                    ],
                    status="blocked",
                )
            ]
            completion = [
                "Existe una decisión humana registrada.",
                "El estado final está trazado.",
            ]
        else:
            lead = str(decision_plan["lead_specialist"])
            supports = list(decision_plan.get("support_specialists", []))[:2]

            tasks = [
                PlanTask(
                    id="T1",
                    title="Verificar contexto y no duplicidad",
                    description=(
                        "Consultar memoria, manifiesto, decisiones y "
                        "componentes existentes."
                    ),
                    specialist="Architect",
                    depends_on=[],
                    acceptance_criteria=[
                        "Se identifican componentes relacionados.",
                        "Se confirma que no existe una solución equivalente.",
                    ],
                ),
                PlanTask(
                    id="T2",
                    title="Definir contrato del entregable",
                    description=(
                        "Especificar objetivo, entradas, salidas, "
                        "dependencias y prueba mínima."
                    ),
                    specialist=lead,
                    depends_on=["T1"],
                    acceptance_criteria=[
                        "El archivo de destino está definido.",
                        "Entradas y salidas están documentadas.",
                        "Existe un criterio verificable de aceptación.",
                    ],
                ),
                PlanTask(
                    id="T3",
                    title="Construir entregable",
                    description="Implementar únicamente el alcance aprobado.",
                    specialist=lead,
                    depends_on=["T2"],
                    acceptance_criteria=[
                        "El entregable funciona en entorno aislado.",
                        "No altera módulos cerrados sin autorización.",
                    ],
                ),
                PlanTask(
                    id="T4",
                    title="Validar calidad",
                    description=(
                        "Ejecutar pruebas, revisar riesgos y verificar "
                        "trazabilidad."
                    ),
                    specialist="QA",
                    depends_on=["T3"],
                    acceptance_criteria=[
                        "Todas las pruebas obligatorias pasan.",
                        "No existen errores críticos abiertos.",
                    ],
                ),
                PlanTask(
                    id="T5",
                    title="Documentar y preparar integración",
                    description=(
                        "Actualizar decisión, documentación, manifiesto "
                        "y paquete limpio."
                    ),
                    specialist=supports[0] if supports else lead,
                    depends_on=["T4"],
                    acceptance_criteria=[
                        "La decisión queda registrada.",
                        "El paquete excluye .git, .venv y cachés.",
                        "El cambio está listo para revisión antes del commit.",
                    ],
                ),
            ]

            completion = [
                "Todas las tareas están completadas.",
                "QA está aprobado.",
                "La documentación y el manifiesto están actualizados.",
                "La integración fue revisada antes del commit.",
            ]

        plan_id = self._plan_id(request)
        plan = Plan(
            plan_id=plan_id,
            objective=request.rstrip("."),
            source_request=request,
            lead_specialist=str(decision_plan["lead_specialist"]),
            support_specialists=list(
                decision_plan.get("support_specialists", [])
            )[:2],
            tasks=tasks,
            completion_criteria=completion,
            blocked=blocked,
            reason=reason,
            generated_at=datetime.now(timezone.utc).isoformat(),
            sources=[
                "NINIA_OS/DT_RUNTIME/current_context.json",
                "NINIA_OS/DT_RUNTIME/decision_registry.json",
                "NINIA_OS/PROJECT_MANIFEST.json",
            ],
        )

        output = self.plans_dir / f"{plan_id}_{self._slug(request)}.json"
        output.write_text(
            json.dumps(asdict(plan), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return plan
