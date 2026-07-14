
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from engine.services.ai_trainer import AITrainerService, AITrainerError
from engine.services.corpus_audit import CorpusAuditService
from engine.services.evidence_dataset import (
    EvidenceDatasetError,
    EvidenceDatasetService,
)
from engine.services.global_evidence_acquisition import (
    GlobalEvidenceAcquisitionService,
)
from engine.services.scientific_validation import (
    ScientificValidationService,
)


class OperationalPipelineError(RuntimeError):
    """Raised when the operational knowledge factory cannot complete safely."""


class OperationalKnowledgeFactory:
    """Run the existing NINIA pipeline end to end without parallel logic.

    Flow:
    trusted sources -> acquisition -> scientific prevalidation -> corpus audit
    -> dataset -> training (only when the existing training gate is open).

    The service never approves evidence automatically. It persists a run
    manifest that can be consumed by the API and frontend.
    """

    SCHEMA_VERSION = "1.0"

    def __init__(
        self,
        base_dir: Path | str,
        *,
        acquisition_service: GlobalEvidenceAcquisitionService | None = None,
        validation_service: ScientificValidationService | None = None,
        corpus_audit_service: CorpusAuditService | None = None,
    ) -> None:
        self.base_dir = Path(base_dir)
        self.acquisition_service = acquisition_service or (
            GlobalEvidenceAcquisitionService(base_dir=self.base_dir)
        )
        self.validation_service = validation_service or (
            ScientificValidationService(base_dir=self.base_dir)
        )
        self.corpus_audit_service = corpus_audit_service or (
            CorpusAuditService(self.base_dir)
        )
        self.runs_dir = self.base_dir / "operations" / "runs"
        self.latest_path = self.base_dir / "operations" / "latest.json"
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.latest_path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _run_id() -> str:
        return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")

    @staticmethod
    def _safe_validation(
        service: ScientificValidationService,
        request_id: str,
    ) -> dict[str, Any]:
        try:
            report = service.assess_request(request_id)
            return {
                "request_id": request_id,
                "status": "OK",
                "report": report,
            }
        except Exception as exc:
            return {
                "request_id": request_id,
                "status": "ERROR",
                "error_type": type(exc).__name__,
                "detail": str(exc),
            }

    @staticmethod
    def _next_version(prefix: str, existing: Iterable[Path]) -> str:
        highest = 0
        pattern = prefix.lower().lstrip("v")
        for path in existing:
            name = path.name.lower().lstrip("v")
            if not name.startswith(pattern):
                continue
            suffix = name[len(pattern):].lstrip(".-")
            try:
                highest = max(highest, int(suffix))
            except ValueError:
                continue
        return f"{prefix}.{highest + 1}"

    def _dataset_version(self) -> str:
        root = self.base_dir / "knowledge" / "datasets"
        existing = list(root.glob("v*")) if root.exists() else []
        return self._next_version("0.2", existing)

    def _model_version(self) -> str:
        root = self.base_dir / "models" / "classifier"
        existing = list(root.glob("v*")) if root.exists() else []
        return self._next_version("0.2", existing)

    def run(
        self,
        *,
        source_ids: Iterable[str] | None = None,
        max_documents_per_source: int = 3,
        max_total_documents: int = 10,
        train_if_ready: bool = True,
    ) -> dict[str, Any]:
        run_id = self._run_id()
        started_at = self._now()

        acquisition = self.acquisition_service.acquire(
            source_ids=source_ids,
            max_documents_per_source=max_documents_per_source,
            max_total_documents=max_total_documents,
        )

        validations = [
            self._safe_validation(
                self.validation_service,
                str(item["request_id"]),
            )
            for item in acquisition.get("acquired", [])
            if item.get("request_id")
        ]

        corpus_audit = self.corpus_audit_service.audit()
        training_gate = corpus_audit.get("training_gate", {})
        ready_for_training = bool(
            training_gate.get("ready_for_next_official_training")
        )

        dataset_result: dict[str, Any] | None = None
        training_result: dict[str, Any] | None = None
        training_status = "NOT_REQUESTED"

        if train_if_ready:
            if ready_for_training:
                dataset_version = self._dataset_version()
                model_version = self._model_version()
                dataset_service = EvidenceDatasetService(
                    self.base_dir,
                    dataset_version=dataset_version,
                    seed=42,
                )
                try:
                    dataset_result = dataset_service.build()
                    trainer = AITrainerService(
                        self.base_dir,
                        dataset_version=dataset_version,
                        model_version=model_version,
                    )
                    training_result = trainer.train()
                    training_status = "COMPLETED"
                except (EvidenceDatasetError, AITrainerError) as exc:
                    training_status = "BLOCKED"
                    training_result = {
                        "error_type": type(exc).__name__,
                        "detail": str(exc),
                    }
            else:
                training_status = "BLOCKED_BY_CORPUS_GATE"
                training_result = {
                    "reasons": training_gate.get("reasons", []),
                }

        manifest = {
            "schema_version": self.SCHEMA_VERSION,
            "run_id": run_id,
            "started_at": started_at,
            "completed_at": self._now(),
            "status": "COMPLETED",
            "acquisition": acquisition,
            "scientific_validation": {
                "total": len(validations),
                "successful": sum(
                    1 for item in validations if item["status"] == "OK"
                ),
                "failed": sum(
                    1 for item in validations if item["status"] == "ERROR"
                ),
                "items": validations,
            },
            "corpus_audit": corpus_audit,
            "dataset": dataset_result,
            "training": {
                "status": training_status,
                "result": training_result,
            },
            "governance": {
                "automatic_approval": False,
                "human_review_required": True,
                "official_training_requires_corpus_gate": True,
                "source_documents_read_by_trainer": False,
                "knowledge_objects_read_by_trainer": False,
            },
        }

        run_path = self.runs_dir / f"{run_id}.json"
        run_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        self.latest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        manifest["run_path"] = str(run_path)
        return manifest

    def status(self) -> dict[str, Any]:
        if self.latest_path.exists():
            try:
                latest = json.loads(
                    self.latest_path.read_text(encoding="utf-8")
                )
            except json.JSONDecodeError as exc:
                raise OperationalPipelineError(
                    f"Estado operativo inválido: {exc}"
                ) from exc
        else:
            latest = None

        proposed = len(
            list((self.base_dir / "knowledge" / "proposed").glob("*.json"))
        )
        approved = len(
            list((self.base_dir / "knowledge" / "approved").glob("*.json"))
        )
        model_registry = self.base_dir / "models" / "registry.json"
        models = 0
        if model_registry.exists():
            try:
                data = json.loads(model_registry.read_text(encoding="utf-8"))
                models = len(data.get("models") or [])
            except Exception:
                models = 0

        return {
            "status": "ok",
            "knowledge": {
                "proposed": proposed,
                "approved": approved,
            },
            "models_registered": models,
            "latest_run": latest,
        }
