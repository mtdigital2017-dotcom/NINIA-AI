
from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.services.ai_trainer import AITrainerError, AITrainerService


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(
            json.dumps(item, ensure_ascii=False) + "\n"
            for item in records
        ),
        encoding="utf-8",
    )


def _dataset(base_dir: Path, *, ready: bool = True) -> None:
    dataset_dir = base_dir / "knowledge" / "datasets" / "v0.1.0"
    dataset_dir.mkdir(parents=True)

    train = []
    validation = []
    test = []
    for index in range(20):
        label = "privacidad infantil" if index % 2 == 0 else "violencia digital"
        record = {
            "record_id": f"record-{index:03d}",
            "input": (
                "protección de datos y privacidad infantil"
                if label == "privacidad infantil"
                else "prevención de violencia y acoso digital"
            ),
            "target": label,
            "traceability": {
                "knowledge_id": f"knowledge-{index:03d}",
                "fragment_id": f"fragment-{index:03d}",
                "sha256": f"{index:064x}"[-64:],
            },
        }
        if index < 14:
            train.append(record)
        elif index < 17:
            validation.append(record)
        else:
            test.append(record)

    _write_jsonl(dataset_dir / "train.jsonl", train)
    _write_jsonl(dataset_dir / "validation.jsonl", validation)
    _write_jsonl(dataset_dir / "test.jsonl", test)
    (dataset_dir / "manifest.json").write_text(
        json.dumps(
            {
                "dataset_id": "dataset-functional-001",
                "dataset_version": "0.1.0",
                "source_policy": "APPROVED_KNOWLEDGE_ONLY",
                "seed": 42,
                "statistics": {
                    "training_readiness": {
                        "ready": ready,
                        "reasons": [] if ready else ["Corpus insuficiente."],
                    }
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def test_trainer_is_reproducible_and_persists_artifacts(
    tmp_path: Path,
) -> None:
    _dataset(tmp_path)

    first = AITrainerService(tmp_path)
    first_manifest = first.train()
    first_model = (
        first.output_dir / "model.json"
    ).read_text(encoding="utf-8")

    second = AITrainerService(tmp_path)
    second_manifest = second.train()
    second_model = (
        second.output_dir / "model.json"
    ).read_text(encoding="utf-8")

    assert first_manifest["model_id"] == second_manifest["model_id"]
    assert first_model == second_model
    assert first_manifest["governance"]["source_documents_read"] is False
    assert first_manifest["governance"]["knowledge_objects_read"] is False
    assert (first.output_dir / "metrics.json").exists()
    assert (first.output_dir / "training_report.json").exists()
    assert (first.output_dir / "training_manifest.json").exists()
    assert (tmp_path / "models" / "registry.json").exists()


def test_trainer_refuses_dataset_not_ready(tmp_path: Path) -> None:
    _dataset(tmp_path, ready=False)

    with pytest.raises(AITrainerError, match="no apto"):
        AITrainerService(tmp_path).train()


def test_metrics_are_complete(tmp_path: Path) -> None:
    _dataset(tmp_path)
    service = AITrainerService(tmp_path)
    service.train()

    metrics = json.loads(
        (service.output_dir / "metrics.json").read_text(encoding="utf-8")
    )

    for split in ("validation", "test"):
        assert 0 <= metrics[split]["accuracy"] <= 1
        assert 0 <= metrics[split]["macro_precision"] <= 1
        assert 0 <= metrics[split]["macro_recall"] <= 1
        assert 0 <= metrics[split]["macro_f1"] <= 1
        assert metrics[split]["confusion_matrix"]
