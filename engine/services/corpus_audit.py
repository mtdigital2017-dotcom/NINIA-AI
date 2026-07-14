from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from engine.services.scientific_validation import ScientificValidationService


class CorpusAuditError(ValueError):
    """Raised when the scientific corpus cannot be audited safely."""


class CorpusAuditService:
    """Audit the NINIA corpus without approving evidence automatically.

    The service is a derived view over ``knowledge/proposed`` and
    ``knowledge/approved``. It never changes evidence status. It produces:

    - a strict object-level prevalidation queue;
    - a batch-review queue for high-scoring objects;
    - corpus balance and coverage statistics;
    - duplicate warnings;
    - a transparent Corpus Score;
    - a training gate recommendation.

    Human confirmation remains mandatory before any object moves to APROBADO.
    """

    CORPUS_AUDIT_SCHEMA_VERSION = "1.0"
    READY_THRESHOLD = 90.0
    INDIVIDUAL_REVIEW_THRESHOLD = 70.0
    MIN_TRACEABILITY_FOR_BATCH = 80
    MIN_APPROVED_PER_LABEL = 10
    MIN_APPROVED_OBJECTS = 80

    CORPUS_SCORE_WEIGHTS = {
        "metadata_completeness": 0.20,
        "traceability": 0.25,
        "source_diversity": 0.15,
        "category_balance": 0.20,
        "temporal_coverage": 0.10,
        "language_diversity": 0.05,
        "duplicate_control": 0.05,
    }

    def __init__(self, base_dir: Path | str) -> None:
        self.base_dir = Path(base_dir)
        self.proposed_dir = self.base_dir / "knowledge" / "proposed"
        self.approved_dir = self.base_dir / "knowledge" / "approved"
        self.output_dir = self.base_dir / "knowledge" / "corpus_audit"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CorpusAuditError(f"No fue posible leer {path}: {exc}") from exc
        if not isinstance(value, dict):
            raise CorpusAuditError(f"Se esperaba un objeto JSON en {path}.")
        return value

    def _objects(self, directory: Path) -> list[tuple[Path, dict[str, Any]]]:
        if not directory.exists():
            return []
        result: list[tuple[Path, dict[str, Any]]] = []
        for path in sorted(directory.glob("*.json")):
            result.append((path, self._load_json(path)))
        return result

    @staticmethod
    def _request_view(knowledge: dict[str, Any]) -> dict[str, Any]:
        return {
            "title": knowledge.get("title"),
            "year": knowledge.get("publication_year"),
            "author": knowledge.get("authors"),
            "document_type": knowledge.get("document_type"),
            "source": knowledge.get("source"),
            "relation_to_ninia": knowledge.get("relation_to_ninia"),
            "source_url_or_doi": knowledge.get("source_url_or_doi"),
        }

    @classmethod
    def score_object(cls, knowledge: dict[str, Any]) -> dict[str, Any]:
        request = cls._request_view(knowledge)
        dimensions = {}
        notes: list[str] = []

        scorers = {
            "source_traceability": ScientificValidationService._score_traceability,
            "metadata_completeness": ScientificValidationService._score_metadata,
            "evidence_layer_quality": ScientificValidationService._score_evidence_layer,
            "ninia_relevance": ScientificValidationService._score_relevance,
            "document_currency": ScientificValidationService._score_currency,
        }

        for name, scorer in scorers.items():
            if name == "evidence_layer_quality":
                score, score_notes = scorer(knowledge)
            else:
                score, score_notes = scorer(request, knowledge)
            dimensions[name] = int(score)
            notes.extend(score_notes)

        overall = round(
            sum(
                dimensions[name] * weight
                for name, weight in ScientificValidationService.DIMENSION_WEIGHTS.items()
            ),
            2,
        )

        conflicts = []
        provenance = knowledge.get("provenance") or {}
        if len(str(provenance.get("sha256") or "")) != 64:
            conflicts.append("INVALID_OR_MISSING_SHA256")
        if not str(knowledge.get("source_url_or_doi") or "").strip():
            conflicts.append("MISSING_SOURCE_URL_OR_DOI")
        if not (knowledge.get("evidence_fragments") or []):
            conflicts.append("MISSING_EVIDENCE_FRAGMENTS")
        if str(knowledge.get("evidence_status") or "").upper() == "APROBADO":
            conflicts.append("ALREADY_APPROVED")

        if (
            overall >= cls.READY_THRESHOLD
            and dimensions["source_traceability"] >= cls.MIN_TRACEABILITY_FOR_BATCH
            and not conflicts
        ):
            recommendation = "READY_FOR_BATCH_REVIEW"
        elif overall >= cls.INDIVIDUAL_REVIEW_THRESHOLD:
            recommendation = "INDIVIDUAL_HUMAN_REVIEW"
        else:
            recommendation = "REMAIN_IN_QUARANTINE"

        return {
            "knowledge_id": knowledge.get("knowledge_id"),
            "title": knowledge.get("title"),
            "source": knowledge.get("source"),
            "publication_year": knowledge.get("publication_year"),
            "language": knowledge.get("language"),
            "topics": list(knowledge.get("topics") or []),
            "overall_score": overall,
            "dimensions": dimensions,
            "recommendation": recommendation,
            "conflicts": conflicts,
            "limitations": sorted(set(notes)),
            "automatic_approval": False,
            "human_review_required": True,
        }

    @staticmethod
    def _primary_label(knowledge: dict[str, Any]) -> str:
        risks = knowledge.get("digital_risks") or []
        topics = knowledge.get("topics") or []
        specialty = knowledge.get("specialty")
        if isinstance(risks, str):
            risks = [risks]
        if isinstance(topics, str):
            topics = [topics]
        if risks:
            return str(risks[0]).strip().lower()
        if topics:
            return str(topics[0]).strip().lower()
        if specialty:
            return str(specialty).strip().lower()
        return "sin_clasificar"

    @staticmethod
    def _normalized_source(value: Any) -> str:
        return str(value or "DESCONOCIDA").strip().upper()

    @staticmethod
    def _balance_score(counts: Counter[str]) -> float:
        if not counts:
            return 0.0
        values = list(counts.values())
        maximum = max(values)
        minimum = min(values)
        if maximum == 0:
            return 0.0
        return round(100.0 * minimum / maximum, 2)

    @staticmethod
    def _diversity_score(unique_count: int, target: int) -> float:
        if target <= 0:
            return 0.0
        return round(min(100.0, unique_count / target * 100.0), 2)

    @staticmethod
    def _average(values: list[float]) -> float:
        return round(sum(values) / len(values), 2) if values else 0.0

    def _duplicate_report(
        self,
        objects: list[tuple[Path, dict[str, Any]]],
    ) -> dict[str, Any]:
        groups: dict[str, dict[str, list[str]]] = {
            "sha256": defaultdict(list),
            "source_url_or_doi": defaultdict(list),
            "title": defaultdict(list),
        }

        for _, item in objects:
            knowledge_id = str(item.get("knowledge_id") or "")
            provenance = item.get("provenance") or {}
            sha = str(provenance.get("sha256") or "").strip().lower()
            url = str(item.get("source_url_or_doi") or "").strip().lower()
            title = " ".join(str(item.get("title") or "").lower().split())
            if sha:
                groups["sha256"][sha].append(knowledge_id)
            if url:
                groups["source_url_or_doi"][url].append(knowledge_id)
            if title:
                groups["title"][title].append(knowledge_id)

        duplicates = {}
        duplicate_ids: set[str] = set()
        for key, mapping in groups.items():
            normalized = {
                value: sorted(set(ids))
                for value, ids in mapping.items()
            }
            duplicates[key] = {
                value: ids
                for value, ids in normalized.items()
                if len(ids) > 1
            }
            for ids in duplicates[key].values():
                duplicate_ids.update(ids)

        return {
            "duplicate_groups": duplicates,
            "duplicate_knowledge_ids": sorted(duplicate_ids),
            "duplicate_object_count": len(duplicate_ids),
        }

    def audit(self) -> dict[str, Any]:
        proposed = self._objects(self.proposed_dir)
        approved = self._objects(self.approved_dir)
        all_objects = proposed + approved

        proposed_scores = [
            {
                **self.score_object(item),
                "source_path": str(path),
            }
            for path, item in proposed
        ]

        approved_scores = [
            self.score_object(item)
            for _, item in approved
        ]

        ready_queue = [
            item for item in proposed_scores
            if item["recommendation"] == "READY_FOR_BATCH_REVIEW"
        ]
        individual_queue = [
            item for item in proposed_scores
            if item["recommendation"] == "INDIVIDUAL_HUMAN_REVIEW"
        ]
        quarantine_queue = [
            item for item in proposed_scores
            if item["recommendation"] == "REMAIN_IN_QUARANTINE"
        ]

        approved_labels = Counter(
            self._primary_label(item)
            for _, item in approved
        )
        approved_sources = Counter(
            self._normalized_source(item.get("source"))
            for _, item in approved
        )
        approved_languages = Counter(
            str(item.get("language") or "unknown").lower()
            for _, item in approved
        )
        approved_years = Counter(
            str(item.get("publication_year") or "unknown")
            for _, item in approved
        )

        duplicate_report = self._duplicate_report(all_objects)

        metadata_values = [
            score["dimensions"]["metadata_completeness"]
            for score in approved_scores
        ]
        traceability_values = [
            score["dimensions"]["source_traceability"]
            for score in approved_scores
        ]

        components = {
            "metadata_completeness": self._average(metadata_values),
            "traceability": self._average(traceability_values),
            "source_diversity": self._diversity_score(
                len(approved_sources), target=10
            ),
            "category_balance": self._balance_score(approved_labels),
            "temporal_coverage": self._diversity_score(
                len([year for year in approved_years if year != "unknown"]),
                target=5,
            ),
            "language_diversity": self._diversity_score(
                len([lang for lang in approved_languages if lang != "unknown"]),
                target=3,
            ),
            "duplicate_control": round(
                max(
                    0.0,
                    100.0
                    - (
                        duplicate_report["duplicate_object_count"]
                        / max(1, len(all_objects))
                        * 100.0
                    ),
                ),
                2,
            ),
        }

        corpus_score = round(
            sum(
                components[name] * weight
                for name, weight in self.CORPUS_SCORE_WEIGHTS.items()
            ),
            2,
        )

        underrepresented = {
            label: count
            for label, count in sorted(approved_labels.items())
            if count < self.MIN_APPROVED_PER_LABEL
        }

        training_gate_reasons = []
        if len(approved) < self.MIN_APPROVED_OBJECTS:
            training_gate_reasons.append(
                f"Se requieren al menos {self.MIN_APPROVED_OBJECTS} "
                f"Knowledge Objects aprobados; existen {len(approved)}."
            )
        if underrepresented:
            training_gate_reasons.append(
                "Existen categorías con menos de "
                f"{self.MIN_APPROVED_PER_LABEL} objetos aprobados."
            )
        if duplicate_report["duplicate_object_count"] > 0:
            training_gate_reasons.append(
                "Existen posibles duplicados que deben resolverse."
            )

        training_gate = {
            "ready_for_next_official_training": not training_gate_reasons,
            "reasons": training_gate_reasons,
            "approved_objects": len(approved),
            "minimum_approved_objects": self.MIN_APPROVED_OBJECTS,
            "minimum_per_label": self.MIN_APPROVED_PER_LABEL,
            "underrepresented_labels": underrepresented,
        }

        report = {
            "schema_version": self.CORPUS_AUDIT_SCHEMA_VERSION,
            "generated_at": self._now(),
            "governance": {
                "automatic_approval": False,
                "human_review_required": True,
                "batch_review_allowed": True,
                "batch_threshold": self.READY_THRESHOLD,
                "individual_review_threshold": self.INDIVIDUAL_REVIEW_THRESHOLD,
            },
            "counts": {
                "proposed": len(proposed),
                "approved": len(approved),
                "total": len(all_objects),
                "ready_for_batch_review": len(ready_queue),
                "individual_human_review": len(individual_queue),
                "remain_in_quarantine": len(quarantine_queue),
            },
            "queues": {
                "ready_for_batch_review": ready_queue,
                "individual_human_review": individual_queue,
                "remain_in_quarantine": quarantine_queue,
            },
            "coverage": {
                "labels": dict(sorted(approved_labels.items())),
                "sources": dict(sorted(approved_sources.items())),
                "languages": dict(sorted(approved_languages.items())),
                "years": dict(sorted(approved_years.items())),
            },
            "duplicates": duplicate_report,
            "corpus_score": {
                "value": corpus_score,
                "scale": "0-100",
                "components": components,
                "weights": self.CORPUS_SCORE_WEIGHTS,
                "interpretation": (
                    "Indicador descriptivo y reproducible del corpus; "
                    "no representa accuracy del modelo."
                ),
            },
            "training_gate": training_gate,
        }

        self._write_outputs(report)
        return report

    def _write_outputs(self, report: dict[str, Any]) -> None:
        (self.output_dir / "corpus_audit_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (self.output_dir / "batch_review_queue.json").write_text(
            json.dumps(
                report["queues"]["ready_for_batch_review"],
                ensure_ascii=False,
                indent=2,
            ) + "\n",
            encoding="utf-8",
        )
        (self.output_dir / "individual_review_queue.json").write_text(
            json.dumps(
                report["queues"]["individual_human_review"],
                ensure_ascii=False,
                indent=2,
            ) + "\n",
            encoding="utf-8",
        )
        (self.output_dir / "corpus_gap_report.json").write_text(
            json.dumps(
                {
                    "generated_at": report["generated_at"],
                    "training_gate": report["training_gate"],
                    "coverage": report["coverage"],
                    "duplicates": report["duplicates"],
                },
                ensure_ascii=False,
                indent=2,
            ) + "\n",
            encoding="utf-8",
        )
