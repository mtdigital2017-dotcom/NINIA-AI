
from __future__ import annotations

import json
from pathlib import Path

from engine.services.evidence_dataset import EvidenceDatasetService


def _knowledge(index: int, *, status: str = "APROBADO") -> dict:
    label = "privacidad infantil" if index % 2 == 0 else "violencia digital"
    return {
        "schema_version": "1.0",
        "knowledge_id": f"knowledge-{index:03d}",
        "title": f"Documento {index}",
        "content": "Conocimiento aprobado.",
        "source": "UNICEF",
        "source_url_or_doi": f"https://www.unicef.org/report-{index}",
        "authors": ["UNICEF"],
        "publication_year": 2025,
        "language": "es",
        "topics": [label],
        "entities": [],
        "digital_risks": [label],
        "evidence_level": "ALTO",
        "evidence_status": status,
        "relation_to_ninia": "Protección de NNA",
        "specialty": "proteccion_infantil_digital",
        "evidence_fragments": [{
            "fragment_id": f"fragment-{index:03d}",
            "position": 1,
            "text": f"Fragmento {index} sobre {label}.",
            "language": "es",
            "evidence_type": "DOCUMENT_EXCERPT",
            "source_locator": {
                "source_path": f"report-{index}.pdf",
                "page": index + 1,
                "section": None,
            },
            "confidence": 1.0,
            "validation_status": "APROBADO",
        }],
        "typed_relations": [],
        "provenance": {
            "source_path": f"report-{index}.pdf",
            "sha256": f"{index:064x}"[-64:],
            "ingestion_method": "normalized",
        },
        "created_at": "2025-01-01T00:00:00+00:00",
        "updated_at": None,
    }


def test_build_is_reproducible_and_approved_only(tmp_path: Path) -> None:
    approved = tmp_path / "knowledge" / "approved"
    approved.mkdir(parents=True)

    for index in range(30):
        (approved / f"{index:03d}.json").write_text(
            json.dumps(_knowledge(index), ensure_ascii=False),
            encoding="utf-8",
        )

    (approved / "rejected.json").write_text(
        json.dumps(_knowledge(999, status="RECHAZADO")),
        encoding="utf-8",
    )

    first = EvidenceDatasetService(
        tmp_path,
        dataset_version="0.1.0",
        seed=42,
    )
    first_manifest = first.build()
    first_train = (first.output_dir / "train.jsonl").read_text(
        encoding="utf-8"
    )

    second = EvidenceDatasetService(
        tmp_path,
        dataset_version="0.1.0",
        seed=42,
    )
    second_manifest = second.build()
    second_train = (second.output_dir / "train.jsonl").read_text(
        encoding="utf-8"
    )

    assert first_manifest["dataset_id"] == second_manifest["dataset_id"]
    assert first_train == second_train
    assert first_manifest["statistics"]["records"] == 30
    assert first_manifest["source_policy"] == "APPROVED_KNOWLEDGE_ONLY"
    assert first_manifest["statistics"]["training_readiness"]["ready"] is True
    assert first_manifest["validation"]["valid"] is True


def test_build_reports_not_ready_for_small_corpus(tmp_path: Path) -> None:
    approved = tmp_path / "knowledge" / "approved"
    approved.mkdir(parents=True)

    (approved / "one.json").write_text(
        json.dumps(_knowledge(1), ensure_ascii=False),
        encoding="utf-8",
    )

    service = EvidenceDatasetService(tmp_path)
    manifest = service.build()

    readiness = manifest["statistics"]["training_readiness"]
    assert readiness["ready"] is False
    assert readiness["actual_examples"] == 1
    assert (service.output_dir / "manifest.json").exists()
    assert (service.output_dir / "rag_chunks.jsonl").exists()
