from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from engine.evidence_admission import (
    EvidenceAdmissionEngine,
    EvidenceNotFoundError,
)


class ScientificValidationError(ValueError):
    """Raised when a scientific validation report cannot be generated."""


class ScientificValidationService:
    """Creates auditable, non-binding scientific validation reports.

    The service never approves or rejects evidence. It only prepares a
    structured assessment for a human reviewer.
    """

    DIMENSION_WEIGHTS = {
        "source_traceability": 0.25,
        "metadata_completeness": 0.20,
        "evidence_layer_quality": 0.25,
        "ninia_relevance": 0.20,
        "document_currency": 0.10,
    }

    def __init__(
        self,
        base_dir: Path | str,
        admission_engine: EvidenceAdmissionEngine | None = None,
    ) -> None:
        self.base_dir = Path(base_dir)
        self.admission_engine = admission_engine or EvidenceAdmissionEngine(
            base_dir=self.base_dir
        )
        self.reports_dir = (
            self.base_dir / "knowledge" / "validation_reports"
        )
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _score_traceability(
        request: dict[str, Any],
        knowledge: dict[str, Any],
    ) -> tuple[int, list[str]]:
        notes: list[str] = []
        score = 0

        source_url = str(
            request.get("source_url_or_doi")
            or knowledge.get("source_url_or_doi")
            or ""
        ).strip()
        if source_url:
            score += 40
        else:
            notes.append("Falta URL o DOI verificable.")

        source = str(request.get("source") or knowledge.get("source") or "")
        if source.strip():
            score += 25
        else:
            notes.append("Falta entidad o fuente emisora.")

        provenance = knowledge.get("provenance") or {}
        if len(str(provenance.get("sha256") or "")) == 64:
            score += 25
        else:
            notes.append("SHA-256 ausente o inválido.")

        if provenance.get("source_path"):
            score += 10
        else:
            notes.append("Falta ruta de procedencia.")

        return min(score, 100), notes

    @staticmethod
    def _score_metadata(
        request: dict[str, Any],
        knowledge: dict[str, Any],
    ) -> tuple[int, list[str]]:
        fields = {
            "title": request.get("title") or knowledge.get("title"),
            "year": request.get("year") or knowledge.get("publication_year"),
            "author": request.get("author") or knowledge.get("authors"),
            "document_type": (
                request.get("document_type")
                or knowledge.get("document_type")
            ),
            "source": request.get("source") or knowledge.get("source"),
            "relation_to_ninia": (
                request.get("relation_to_ninia")
                or knowledge.get("relation_to_ninia")
            ),
            "language": knowledge.get("language"),
            "topics": knowledge.get("topics"),
        }
        missing = [
            name for name, value in fields.items()
            if value in (None, "", [], {})
        ]
        score = round(100 * (len(fields) - len(missing)) / len(fields))
        notes = (
            ["Metadatos incompletos: " + ", ".join(missing)]
            if missing else []
        )
        return score, notes

    @staticmethod
    def _score_evidence_layer(
        knowledge: dict[str, Any],
    ) -> tuple[int, list[str]]:
        fragments = knowledge.get("evidence_fragments") or []
        relations = knowledge.get("typed_relations") or []
        notes: list[str] = []

        if not fragments:
            return 0, ["No existen fragmentos de evidencia."]

        fragment_scores = []
        for fragment in fragments:
            try:
                confidence = float(fragment.get("confidence", 0))
            except (TypeError, ValueError):
                confidence = 0
            has_text = bool(str(fragment.get("text") or "").strip())
            has_locator = bool(fragment.get("source_locator"))
            fragment_scores.append(
                max(0.0, min(1.0, confidence))
                * (1.0 if has_text else 0.0)
                * (1.0 if has_locator else 0.7)
            )

        base = sum(fragment_scores) / len(fragment_scores)
        relation_bonus = min(len(relations) * 0.04, 0.20)
        score = round(min(1.0, base + relation_bonus) * 100)

        if not relations:
            notes.append("No existen relaciones tipadas.")
        if any(
            item.get("validation_status") != "PROPUESTO"
            for item in fragments
        ):
            notes.append(
                "Hay fragmentos con estado distinto de PROPUESTO."
            )

        return score, notes

    @staticmethod
    def _score_relevance(
        request: dict[str, Any],
        knowledge: dict[str, Any],
    ) -> tuple[int, list[str]]:
        relation = str(
            request.get("relation_to_ninia")
            or knowledge.get("relation_to_ninia")
            or ""
        ).strip()
        topics = knowledge.get("topics") or []
        risks = knowledge.get("digital_risks") or []

        score = 0
        notes: list[str] = []
        if len(relation) >= 30:
            score += 55
        elif relation:
            score += 30
            notes.append("La relación con NINIA requiere mayor detalle.")
        else:
            notes.append("No se documentó la relación con NINIA.")

        if topics:
            score += 25
        else:
            notes.append("No se identificaron temas.")

        if risks:
            score += 20
        else:
            notes.append("No se identificaron riesgos digitales.")

        return min(score, 100), notes

    @staticmethod
    def _score_currency(
        request: dict[str, Any],
        knowledge: dict[str, Any],
    ) -> tuple[int, list[str]]:
        year = request.get("year") or knowledge.get("publication_year")
        try:
            year_int = int(year)
        except (TypeError, ValueError):
            return 20, ["Año de publicación ausente o inválido."]

        current_year = datetime.now(timezone.utc).year
        age = max(0, current_year - year_int)
        if age <= 2:
            return 100, []
        if age <= 5:
            return 85, []
        if age <= 10:
            return 65, ["Documento con más de cinco años."]
        return 40, ["Documento histórico; verificar vigencia."]

    def assess_request(
        self,
        request_id: str,
        *,
        evaluator_name: str = "NINIA Scientific Validation",
        evaluator_version: str = "1.0",
    ) -> dict[str, Any]:
        request = self.admission_engine.get_request(request_id)
        knowledge_path_value = request.get("knowledge_object_path")
        if not knowledge_path_value:
            raise ScientificValidationError(
                "La solicitud no tiene Knowledge Object asociado."
            )

        knowledge_path = Path(knowledge_path_value)
        if not knowledge_path.exists():
            raise ScientificValidationError(
                "No se encontró el Knowledge Object asociado."
            )

        knowledge = json.loads(
            knowledge_path.read_text(encoding="utf-8")
        )

        scorers = {
            "source_traceability": self._score_traceability,
            "metadata_completeness": self._score_metadata,
            "evidence_layer_quality": (
                lambda req, obj: self._score_evidence_layer(obj)
            ),
            "ninia_relevance": self._score_relevance,
            "document_currency": self._score_currency,
        }

        dimensions: dict[str, Any] = {}
        total = 0.0
        all_notes: list[str] = []

        for name, weight in self.DIMENSION_WEIGHTS.items():
            score, notes = scorers[name](request, knowledge)
            dimensions[name] = {
                "score": score,
                "weight": weight,
                "notes": notes,
            }
            total += score * weight
            all_notes.extend(notes)

        overall_score = round(total, 2)

        if overall_score >= 80 and dimensions[
            "source_traceability"
        ]["score"] >= 70:
            recommendation = "READY_FOR_HUMAN_REVIEW"
        elif overall_score >= 60:
            recommendation = "REQUIRES_COMPLETION"
        else:
            recommendation = "INSUFFICIENT_FOR_REVIEW"

        report = {
            "report_version": "1.0",
            "request_id": request_id,
            "knowledge_id": knowledge.get("knowledge_id"),
            "generated_at": self._now(),
            "evaluator": {
                "name": evaluator_name,
                "version": evaluator_version,
                "type": "AUTOMATED_PRE_ASSESSMENT",
            },
            "current_request_status": request.get("status"),
            "current_knowledge_status": knowledge.get("evidence_status"),
            "overall_score": overall_score,
            "dimensions": dimensions,
            "recommendation": recommendation,
            "limitations": sorted(set(all_notes)),
            "governance": {
                "binding_decision": False,
                "automatic_approval": False,
                "human_review_required": True,
                "allowed_human_decisions": [
                    "EN_VALIDACION",
                    "APROBADO",
                    "RECHAZADO",
                    "CORRECCION_SOLICITADA",
                ],
            },
        }

        target = self.reports_dir / f"{request_id}.json"
        target.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        report["saved_to"] = str(target)
        return report

    def get_report(self, request_id: str) -> dict[str, Any]:
        target = self.reports_dir / f"{request_id}.json"
        if not target.exists():
            raise ScientificValidationError(
                "No existe informe de validación científica."
            )
        report = json.loads(target.read_text(encoding="utf-8"))
        report["saved_to"] = str(target)
        return report

    def list_reports(self) -> list[dict[str, Any]]:
        reports = []
        for path in self.reports_dir.glob("*.json"):
            try:
                report = json.loads(path.read_text(encoding="utf-8"))
                report["saved_to"] = str(path)
                reports.append(report)
            except Exception:
                continue
        return sorted(
            reports,
            key=lambda item: item.get("generated_at", ""),
            reverse=True,
        )
