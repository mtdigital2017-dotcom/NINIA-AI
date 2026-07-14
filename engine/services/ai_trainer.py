
from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class AITrainerError(ValueError):
    """Raised when an AI training run cannot be completed safely."""


class AITrainerService:
    """Train a reproducible text classifier from EvidenceDatasetService output.

    The trainer consumes only dataset artifacts. It never reads source
    documents, Knowledge Objects, or the Knowledge Graph directly.
    """

    MODEL_SCHEMA_VERSION = "1.0"
    TOKEN_PATTERN = re.compile(r"\b[\wáéíóúüñ]+\b", re.IGNORECASE)

    def __init__(
        self,
        base_dir: Path | str,
        *,
        dataset_version: str = "0.1.0",
        model_version: str = "0.1.0",
        alpha: float = 1.0,
        min_token_length: int = 2,
    ) -> None:
        self.base_dir = Path(base_dir)
        self.dataset_dir = (
            self.base_dir / "knowledge" / "datasets" / f"v{dataset_version}"
        )
        self.output_dir = (
            self.base_dir / "models" / "classifier" / f"v{model_version}"
        )
        self.registry_path = self.base_dir / "models" / "registry.json"
        self.dataset_version = str(dataset_version)
        self.model_version = str(model_version)
        self.alpha = float(alpha)
        self.min_token_length = int(min_token_length)

        if self.alpha <= 0:
            raise AITrainerError("alpha debe ser mayor que cero.")
        if self.min_token_length < 1:
            raise AITrainerError(
                "min_token_length debe ser mayor o igual a uno."
            )

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise AITrainerError(
                f"No fue posible leer {path}: {exc}"
            ) from exc
        if not isinstance(value, dict):
            raise AITrainerError(f"Se esperaba un objeto JSON en {path}.")
        return value

    @staticmethod
    def _load_jsonl(path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            raise AITrainerError(f"No existe el dataset requerido: {path}")
        records: list[dict[str, Any]] = []
        for line_number, raw in enumerate(
            path.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if not raw.strip():
                continue
            try:
                value = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise AITrainerError(
                    f"JSONL inválido en {path}:{line_number}: {exc}"
                ) from exc
            if not isinstance(value, dict):
                raise AITrainerError(
                    f"Registro inválido en {path}:{line_number}."
                )
            records.append(value)
        return records

    def _tokens(self, text: str) -> list[str]:
        return [
            token.lower()
            for token in self.TOKEN_PATTERN.findall(str(text))
            if len(token) >= self.min_token_length
        ]

    def _validate_dataset(
        self,
        manifest: dict[str, Any],
        train: list[dict[str, Any]],
        validation: list[dict[str, Any]],
        test: list[dict[str, Any]],
    ) -> None:
        if manifest.get("source_policy") != "APPROVED_KNOWLEDGE_ONLY":
            raise AITrainerError(
                "El entrenador solo admite conocimiento APROBADO."
            )
        readiness = (
            manifest.get("statistics", {})
            .get("training_readiness", {})
        )
        if readiness.get("ready") is not True:
            reasons = readiness.get("reasons") or []
            raise AITrainerError(
                "Dataset no apto para entrenamiento: "
                + "; ".join(str(item) for item in reasons)
            )
        if not train:
            raise AITrainerError("La partición train está vacía.")
        if not validation:
            raise AITrainerError("La partición validation está vacía.")
        if not test:
            raise AITrainerError("La partición test está vacía.")

        required = {"record_id", "input", "target", "traceability"}
        for split_name, records in (
            ("train", train),
            ("validation", validation),
            ("test", test),
        ):
            for record in records:
                missing = required - set(record)
                if missing:
                    raise AITrainerError(
                        f"Registro incompleto en {split_name}: "
                        + ", ".join(sorted(missing))
                    )

    def _fit(
        self,
        train: list[dict[str, Any]],
    ) -> dict[str, Any]:
        label_counts: Counter[str] = Counter()
        token_counts: dict[str, Counter[str]] = defaultdict(Counter)
        vocabulary: set[str] = set()

        for record in train:
            label = str(record["target"])
            tokens = self._tokens(str(record["input"]))
            label_counts[label] += 1
            token_counts[label].update(tokens)
            vocabulary.update(tokens)

        if len(label_counts) < 2:
            raise AITrainerError(
                "El entrenamiento requiere al menos dos etiquetas."
            )
        if not vocabulary:
            raise AITrainerError("El vocabulario del entrenamiento está vacío.")

        total_documents = sum(label_counts.values())
        labels = sorted(label_counts)
        priors = {
            label: label_counts[label] / total_documents
            for label in labels
        }
        token_totals = {
            label: sum(token_counts[label].values())
            for label in labels
        }

        return {
            "model_schema_version": self.MODEL_SCHEMA_VERSION,
            "model_type": "multinomial_naive_bayes",
            "model_version": self.model_version,
            "dataset_version": self.dataset_version,
            "alpha": self.alpha,
            "min_token_length": self.min_token_length,
            "labels": labels,
            "label_counts": dict(label_counts),
            "priors": priors,
            "token_counts": {
                label: dict(sorted(token_counts[label].items()))
                for label in labels
            },
            "token_totals": token_totals,
            "vocabulary": sorted(vocabulary),
        }

    def _predict_one(
        self,
        model: dict[str, Any],
        text: str,
    ) -> str:
        tokens = self._tokens(text)
        vocabulary_size = max(len(model["vocabulary"]), 1)
        best_label = ""
        best_score = -math.inf

        for label in model["labels"]:
            prior = max(float(model["priors"][label]), 1e-15)
            score = math.log(prior)
            counts = model["token_counts"][label]
            total = int(model["token_totals"][label])
            denominator = total + self.alpha * vocabulary_size

            for token in tokens:
                numerator = int(counts.get(token, 0)) + self.alpha
                score += math.log(numerator / denominator)

            if score > best_score or (
                score == best_score and label < best_label
            ):
                best_label = label
                best_score = score

        return best_label

    def _evaluate(
        self,
        model: dict[str, Any],
        records: list[dict[str, Any]],
    ) -> dict[str, Any]:
        labels = sorted(
            set(model["labels"])
            | {str(record["target"]) for record in records}
        )
        matrix = {
            actual: {predicted: 0 for predicted in labels}
            for actual in labels
        }

        correct = 0
        predictions: list[dict[str, str]] = []
        for record in records:
            actual = str(record["target"])
            predicted = self._predict_one(
                model,
                str(record["input"]),
            )
            matrix[actual][predicted] += 1
            correct += int(actual == predicted)
            predictions.append({
                "record_id": str(record["record_id"]),
                "actual": actual,
                "predicted": predicted,
            })

        per_label: dict[str, dict[str, float]] = {}
        for label in labels:
            tp = matrix[label][label]
            fp = sum(
                matrix[actual][label]
                for actual in labels
                if actual != label
            )
            fn = sum(
                matrix[label][predicted]
                for predicted in labels
                if predicted != label
            )
            precision = tp / (tp + fp) if tp + fp else 0.0
            recall = tp / (tp + fn) if tp + fn else 0.0
            f1 = (
                2 * precision * recall / (precision + recall)
                if precision + recall
                else 0.0
            )
            per_label[label] = {
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "support": sum(matrix[label].values()),
            }

        count = len(records)
        macro_precision = (
            sum(item["precision"] for item in per_label.values())
            / len(per_label)
            if per_label
            else 0.0
        )
        macro_recall = (
            sum(item["recall"] for item in per_label.values())
            / len(per_label)
            if per_label
            else 0.0
        )
        macro_f1 = (
            sum(item["f1"] for item in per_label.values())
            / len(per_label)
            if per_label
            else 0.0
        )

        return {
            "examples": count,
            "accuracy": correct / count if count else 0.0,
            "macro_precision": macro_precision,
            "macro_recall": macro_recall,
            "macro_f1": macro_f1,
            "per_label": per_label,
            "confusion_matrix": matrix,
            "predictions": predictions,
        }

    @staticmethod
    def _stable_model_id(
        model: dict[str, Any],
        dataset_id: str,
    ) -> str:
        canonical = json.dumps(
            {
                "dataset_id": dataset_id,
                "model_type": model["model_type"],
                "model_version": model["model_version"],
                "alpha": model["alpha"],
                "min_token_length": model["min_token_length"],
                "labels": model["labels"],
                "label_counts": model["label_counts"],
                "token_counts": model["token_counts"],
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24]

    def _update_registry(
        self,
        entry: dict[str, Any],
    ) -> None:
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        if self.registry_path.exists():
            data = self._load_json(self.registry_path)
        else:
            data = {"registry_schema_version": "1.0", "models": []}

        models = data.get("models")
        if not isinstance(models, list):
            models = []

        models = [
            item
            for item in models
            if item.get("model_id") != entry["model_id"]
        ]
        models.append(entry)
        models.sort(key=lambda item: str(item.get("model_id") or ""))
        data["models"] = models

        self.registry_path.write_text(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ) + "\n",
            encoding="utf-8",
        )

    def train(self) -> dict[str, Any]:
        manifest_path = self.dataset_dir / "manifest.json"
        manifest = self._load_json(manifest_path)
        train = self._load_jsonl(self.dataset_dir / "train.jsonl")
        validation = self._load_jsonl(
            self.dataset_dir / "validation.jsonl"
        )
        test = self._load_jsonl(self.dataset_dir / "test.jsonl")

        self._validate_dataset(manifest, train, validation, test)
        model = self._fit(train)
        dataset_id = str(manifest.get("dataset_id") or "")
        model_id = self._stable_model_id(model, dataset_id)
        model["model_id"] = model_id
        model["dataset_id"] = dataset_id

        validation_metrics = self._evaluate(model, validation)
        test_metrics = self._evaluate(model, test)

        self.output_dir.mkdir(parents=True, exist_ok=True)
        model_path = self.output_dir / "model.json"
        metrics_path = self.output_dir / "metrics.json"
        report_path = self.output_dir / "training_report.json"
        training_manifest_path = (
            self.output_dir / "training_manifest.json"
        )

        model_path.write_text(
            json.dumps(
                model,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ) + "\n",
            encoding="utf-8",
        )
        metrics = {
            "validation": validation_metrics,
            "test": test_metrics,
        }
        metrics_path.write_text(
            json.dumps(
                metrics,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ) + "\n",
            encoding="utf-8",
        )

        training_manifest = {
            "training_schema_version": "1.0",
            "training_id": hashlib.sha256(
                f"{dataset_id}|{model_id}".encode("utf-8")
            ).hexdigest()[:24],
            "model_id": model_id,
            "model_version": self.model_version,
            "model_type": model["model_type"],
            "dataset_id": dataset_id,
            "dataset_version": self.dataset_version,
            "dataset_source_policy": manifest.get("source_policy"),
            "dataset_seed": manifest.get("seed"),
            "configuration": {
                "alpha": self.alpha,
                "min_token_length": self.min_token_length,
            },
            "metrics": {
                "validation_accuracy": validation_metrics["accuracy"],
                "validation_macro_f1": validation_metrics["macro_f1"],
                "test_accuracy": test_metrics["accuracy"],
                "test_macro_f1": test_metrics["macro_f1"],
            },
            "generated_at": self._now(),
            "governance": {
                "source_documents_read": False,
                "knowledge_objects_read": False,
                "approved_dataset_only": True,
                "automatic_approval": False,
            },
        }
        training_manifest_path.write_text(
            json.dumps(
                training_manifest,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ) + "\n",
            encoding="utf-8",
        )
        report_path.write_text(
            json.dumps(
                {
                    "status": "TRAINED",
                    "model_id": model_id,
                    "dataset_id": dataset_id,
                    "validation": validation_metrics,
                    "test": test_metrics,
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ) + "\n",
            encoding="utf-8",
        )

        self._update_registry({
            "model_id": model_id,
            "model_version": self.model_version,
            "model_type": model["model_type"],
            "dataset_id": dataset_id,
            "dataset_version": self.dataset_version,
            "metrics": training_manifest["metrics"],
            "artifact_path": str(model_path),
            "registered_at": self._now(),
        })

        return training_manifest
