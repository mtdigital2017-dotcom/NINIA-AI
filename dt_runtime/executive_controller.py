from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .decision_engine import DecisionEngine, DecisionPlan
from .memory_manager import MemoryManager
from cognitive.planner import Planner


class ExecutiveControllerError(RuntimeError):
    pass


@dataclass(frozen=True)
class ExecutiveResult:
    request_id: str
    request: str
    memory_loaded: bool
    memory_qa_passed: bool
    decision_plan: dict[str, Any]
    execution_plan: dict[str, Any]
    processed_at: str
    trace_path: str


class ExecutiveController:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.runtime_dir = self.root / "NINIA_OS" / "DT_RUNTIME"
        self.memory = MemoryManager(self.root)
        self.decisions = DecisionEngine(self.root)
        self.planner = Planner(self.root)
        self.trace_dir = self.runtime_dir / "executive_traces"
        self.trace_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _request_id(request: str) -> str:
        import hashlib
        timestamp = datetime.now(timezone.utc).isoformat()
        return hashlib.sha256(f"{timestamp}|{request}".encode()).hexdigest()[:16]

    def _bootstrap(self) -> dict[str, Any]:
        context = self.memory.build_context()
        if context.get("source_of_truth") != "NINIA_OS":
            raise ExecutiveControllerError("Fuente de verdad inválida.")
        if context.get("qa", {}).get("passed") is not True:
            raise ExecutiveControllerError("El contexto no superó QA.")
        return context

    def process(self, request: str) -> ExecutiveResult:
        if not request.strip():
            raise ValueError("La solicitud no puede estar vacía.")

        context = self._bootstrap()
        plan: DecisionPlan = self.decisions.plan(request)
        execution_plan = self.planner.build(asdict(plan))
        request_id = self._request_id(request)
        processed_at = datetime.now(timezone.utc).isoformat()
        trace_path = self.trace_dir / f"{request_id}.json"

        trace = {
            "schema_version": "1.0",
            "request_id": request_id,
            "request": request,
            "memory_loaded": True,
            "memory_qa_passed": True,
            "context_generated_at": context.get("generated_at"),
            "decision_plan": asdict(plan),
            "execution_plan": asdict(execution_plan),
            "processed_at": processed_at,
        }

        trace_path.write_text(
            json.dumps(trace, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        self.memory.build_context()

        return ExecutiveResult(
            request_id=request_id,
            request=request,
            memory_loaded=True,
            memory_qa_passed=True,
            decision_plan=asdict(plan),
            execution_plan=asdict(execution_plan),
            processed_at=processed_at,
            trace_path=trace_path.relative_to(self.root).as_posix(),
        )

    def health(self) -> dict[str, Any]:
        context = self._bootstrap()
        return {
            "status": "ok",
            "source_of_truth": context["source_of_truth"],
            "memory_qa_passed": context["qa"]["passed"],
        }
