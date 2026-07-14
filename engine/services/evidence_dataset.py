
from __future__ import annotations

import hashlib
import json
import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class EvidenceDatasetError(ValueError):
    """Raised when the evidence dataset cannot be built or validated."""


class EvidenceDatasetService:
    """Build reproducible AI datasets from approved Knowledge Objects.

    This service is a derived view over ``knowledge/approved``. It never
    modifies Knowledge Objects, never changes evidence states, and never
    approves evidence automatically.
    """

    DATASET_SCHEMA_VERSION = "1.0"

    def __init__(
        self,
        base_dir: Path | str,
        *,
        dataset_version: str = "0.1.0",
        seed: int = 42,
        train_ratio: float = 0.8,
        validation_ratio: float = 0.1,
        test_ratio: float = 0.1,
        min_examples_for_training: int = 20,
        min_labels_for_training: int = 2,
    ) -> None:
        self.base_dir = Path(base_dir)
        self.approved_dir = self.base_dir / "knowledge" / "approved"
        self.output_dir = (
            self.base_dir
            / "knowledge"
            / "datasets"
            / f"v{dataset_version}"
        )
        self.dataset_version = str(dataset_version)
        self.seed = int(seed)
        self.train_ratio = float(train_ratio)
        self.validation_ratio = float(validation_ratio)
        self.test_ratio = float(test_ratio)
        self.min_examples_for_training = int(min_examples_for_training)
        self.min_labels_for_training = int(min_labels_for_training)

        ratio_sum = self.train_ratio + self.validation_ratio + self.test_ratio
        if abs(ratio_sum - 1.0) > 1e-9:
            raise EvidenceDatasetError(
                "Las proporciones train/validation/test deben sumar 1.0."
            )
        if min(
            self.train_ratio,
            self.validation_ratio,
            self.test_ratio,
        ) < 0:
            raise EvidenceDatasetError(
                "Las proporciones no pueden ser negativas."
            )

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise EvidenceDatasetError(
                f"No fue posible leer {path}: {exc}"
            ) from exc
        if not isinstance(data, dict):
            raise EvidenceDatasetError(
                f"El Knowledge Object debe ser un objeto JSON: {path}"
            )
        return data

    def _approved_objects(self) -> list[tuple[Path, dict[str, Any]]]:
        if not self.approved_dir.exists():
            return []

        result: list[tuple[Path, dict[str, Any]]] = []
        for path in sorted(self.approved_dir.glob("*.json")):
            item = self._load_json(path)
            if item.get("evidence_status") != "APROBADO":
                continue
            result.append((path, item))
        return result

    @staticmethod
    def _primary_label(knowledge: dict[str, Any]) -> str:
        for key in ("digital_risks", "topics"):
            value = knowledge.get(key)
            if isinstance(value, list):
                for item in value:
                    text = str(item).strip()
                    if text:
                        return text
            elif isinstance(value, str) and value.strip():
                return value.strip()

        specialty = str(knowledge.get("specialty") or "").strip()
        return specialty or "sin_clasificar"

    @staticmethod
    def _iter_fragments(
        knowledge: dict[str, Any],
    ) -> list[dict[str, Any]]:
        fragments = knowledge.get("evidence_fragments")
        if isinstance(fragments, list) and fragments:
            return [
                fragment
                for fragment in fragments
                if isinstance(fragment, dict)
                and str(fragment.get("text") or "").strip()
                and fragment.get("validation_status") == "APROBADO"
            ]

        content = str(knowledge.get("content") or "").strip()
        if not content:
            return []

        return [{
            "fragment_id": f"{knowledge.get('knowledge_id')}:content",
            "position": 1,
            "text": content,
            "language": knowledge.get("language"),
            "evidence_type": "KNOWLEDGE_CONTENT",
            "source_locator": {
                "source_path": (
                    (knowledge.get("provenance") or {}).get("source_path")
                ),
                "page": None,
                "section": None,
            },
            "confidence": 1.0,
            "validation_status": "APROBADO",
        }]

    def _records(self) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        seen: set[str] = set()

        for source_path, knowledge in self._approved_objects():
            knowledge_id = str(
                knowledge.get("knowledge_id") or ""
            ).strip()
            if not knowledge_id:
                raise EvidenceDatasetError(
                    f"Knowledge Object sin knowledge_id: {source_path}"
                )

            provenance = knowledge.get("provenance") or {}
            sha256 = str(provenance.get("sha256") or "").strip()
            label = self._primary_label(knowledge)

            for fragment in self._iter_fragments(knowledge):
                fragment_id = str(
                    fragment.get("fragment_id") or ""
                ).strip()
                text = str(fragment.get("text") or "").strip()
                if not fragment_id or not text:
                    continue

                record_id = hashlib.sha256(
                    f"{knowledge_id}|{fragment_id}|{text}".encode("utf-8")
                ).hexdigest()[:24]
                if record_id in seen:
                    continue
                seen.add(record_id)

                records.append({
                    "schema_version": self.DATASET_SCHEMA_VERSION,
                    "record_id": record_id,
                    "task": "risk_or_topic_classification",
                    "input": text,
                    "target": label,
                    "language": (
                        fragment.get("language")
                        or knowledge.get("language")
                    ),
                    "evidence_level": knowledge.get("evidence_level"),
                    "knowledge_id": knowledge_id,
                    "fragment_id": fragment_id,
                    "source": knowledge.get("source"),
                    "source_url_or_doi": (
                        knowledge.get("source_url_or_doi")
                    ),
                    "publication_year": (
                        knowledge.get("publication_year")
                    ),
                    "topics": knowledge.get("topics") or [],
                    "digital_risks": (
                        knowledge.get("digital_risks") or []
                    ),
                    "traceability": {
                        "knowledge_id": knowledge_id,
                        "fragment_id": fragment_id,
                        "sha256": sha256,
                        "source_path": provenance.get("source_path"),
                        "source_locator": (
                            fragment.get("source_locator") or {}
                        ),
                    },
                })

        return sorted(records, key=lambda item: item["record_id"])

    def _split(
        self,
        records: list[dict[str, Any]],
    ) -> dict[str, list[dict[str, Any]]]:
        shuffled = list(records)
        random.Random(self.seed).shuffle(shuffled)

        total = len(shuffled)
        train_end = int(total * self.train_ratio)
        validation_end = train_end + int(
            total * self.validation_ratio
        )

        return {
            "train": shuffled[:train_end],
            "validation": shuffled[train_end:validation_end],
            "test": shuffled[validation_end:],
        }

    @staticmethod
    def _jsonl_text(records: list[dict[str, Any]]) -> str:
        return "".join(
            json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n"
            for item in records
        )

    @staticmethod
    def _sha256_text(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def _write_jsonl(
        self,
        filename: str,
        records: list[dict[str, Any]],
    ) -> str:
        text = self._jsonl_text(records)
        path = self.output_dir / filename
        path.write_text(text, encoding="utf-8")
        return self._sha256_text(text)

    def _training_readiness(
        self,
        records: list[dict[str, Any]],
    ) -> dict[str, Any]:
        labels = Counter(item["target"] for item in records)
        reasons: list[str] = []
        if len(records) < self.min_examples_for_training:
            reasons.append(
                f"Se requieren al menos "
                f"{self.min_examples_for_training} ejemplos."
            )
        if len(labels) < self.min_labels_for_training:
            reasons.append(
                f"Se requieren al menos "
                f"{self.min_labels_for_training} etiquetas."
            )

        return {
            "ready": not reasons,
            "minimum_examples": self.min_examples_for_training,
            "minimum_labels": self.min_labels_for_training,
            "actual_examples": len(records),
            "actual_labels": len(labels),
            "reasons": reasons,
        }

    def validate(
        self,
        records: list[dict[str, Any]],
        splits: dict[str, list[dict[str, Any]]],
    ) -> dict[str, Any]:
        errors: list[str] = []
        ids = [item.get("record_id") for item in records]
        if len(ids) != len(set(ids)):
            errors.append("Existen record_id duplicados.")

        required = {
            "record_id",
            "input",
            "target",
            "knowledge_id",
            "fragment_id",
            "traceability",
        }
        for item in records:
            missing = sorted(required - set(item))
            if missing:
                errors.append(
                    f"Registro {item.get('record_id')} incompleto: "
                    + ", ".join(missing)
                )
            traceability = item.get("traceability")
            if not isinstance(traceability, dict):
                errors.append(
                    f"Registro {item.get('record_id')} sin trazabilidad."
                )
                continue
            if not traceability.get("knowledge_id"):
                errors.append(
                    f"Registro {item.get('record_id')} sin knowledge_id."
                )
            if len(str(traceability.get("sha256") or "")) != 64:
                errors.append(
                    f"Registro {item.get('record_id')} sin SHA-256 válido."
                )

        split_ids = [
            item["record_id"]
            for split in splits.values()
            for item in split
        ]
        if sorted(split_ids) != sorted(ids):
            errors.append(
                "Las particiones no contienen exactamente los registros."
            )

        return {
            "valid": not errors,
            "errors": errors,
        }

    def build(self) -> dict[str, Any]:
        records = self._records()
        splits = self._split(records)
        validation = self.validate(records, splits)
        if not validation["valid"]:
            raise EvidenceDatasetError(
                "Dataset inválido: " + "; ".join(validation["errors"])
            )

        self.output_dir.mkdir(parents=True, exist_ok=True)

        checksums = {
            "train.jsonl": self._write_jsonl(
                "train.jsonl", splits["train"]
            ),
            "validation.jsonl": self._write_jsonl(
                "validation.jsonl", splits["validation"]
            ),
            "test.jsonl": self._write_jsonl(
                "test.jsonl", splits["test"]
            ),
            "rag_chunks.jsonl": self._write_jsonl(
                "rag_chunks.jsonl", records
            ),
            "benchmark.jsonl": self._write_jsonl(
                "benchmark.jsonl", splits["test"]
            ),
        }

        labels = Counter(item["target"] for item in records)
        sources = Counter(
            str(item.get("source") or "SIN_FUENTE")
            for item in records
        )
        readiness = self._training_readiness(records)

        statistics = {
            "records": len(records),
            "splits": {
                key: len(value)
                for key, value in splits.items()
            },
            "labels": dict(sorted(labels.items())),
            "sources": dict(sorted(sources.items())),
            "training_readiness": readiness,
        }
        (self.output_dir / "statistics.json").write_text(
            json.dumps(
                statistics,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ) + "\n",
            encoding="utf-8",
        )

        source_signature = hashlib.sha256(
            "|".join(item["record_id"] for item in records).encode("utf-8")
        ).hexdigest()
        dataset_id = hashlib.sha256(
            (
                f"{self.DATASET_SCHEMA_VERSION}|"
                f"{self.dataset_version}|{self.seed}|"
                f"{source_signature}"
            ).encode("utf-8")
        ).hexdigest()[:24]

        manifest = {
            "dataset_schema_version": self.DATASET_SCHEMA_VERSION,
            "dataset_id": dataset_id,
            "dataset_version": self.dataset_version,
            "generated_at": self._now(),
            "source_policy": "APPROVED_KNOWLEDGE_ONLY",
            "seed": self.seed,
            "ratios": {
                "train": self.train_ratio,
                "validation": self.validation_ratio,
                "test": self.test_ratio,
            },
            "source_signature": source_signature,
            "statistics": statistics,
            "validation": validation,
            "checksums": checksums,
            "governance": {
                "automatic_approval": False,
                "knowledge_objects_modified": False,
                "traceability_required": True,
            },
        }
        (self.output_dir / "manifest.json").write_text(
            json.dumps(
                manifest,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ) + "\n",
            encoding="utf-8",
        )
        return manifest
