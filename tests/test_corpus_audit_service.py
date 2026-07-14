from __future__ import annotations

import json
from pathlib import Path

from engine.services.corpus_audit import CorpusAuditService


def _knowledge(
    knowledge_id: str,
    *,
    status: str,
    topic: str,
    source: str = "UNICEF",
    year: int = 2025,
    language: str = "es",
    score_ready: bool = True,
) -> dict:
    fragments = [
        {
            "fragment_id": f"fragment-{knowledge_id}",
            "position": 1,
            "text": "Evidencia oficial sobre protección infantil digital.",
            "language": language,
            "evidence_type": "DOCUMENT_EXCERPT",
            "source_locator": {
                "source_path": f"{knowledge_id}.pdf",
                "page": 1,
                "section": "1",
            },
            "confidence": 1.0,
            "validation_status": status,
        }
    ] if score_ready else []

    return {
        "schema_version": "1.0",
        "knowledge_id": knowledge_id,
        "title": f"Documento {knowledge_id}",
        "content": "Protección de niñas y niños en entornos digitales.",
        "document_type": "REPORT",
        "source": source,
        "source_url_or_doi": (
            f"https://www.unicef.org/{knowledge_id}"
            if score_ready else ""
        ),
        "authors": [source],
        "publication_year": year,
        "language": language,
        "topics": [topic],
        "entities": [],
        "digital_risks": [topic],
        "evidence_level": "ALTO",
        "evidence_status": status,
        "relation_to_ninia": (
            "Evidencia directamente relacionada con la protección "
            "integral de NNA en entornos digitales."
        ),
        "specialty": "proteccion_infantil_digital",
        "evidence_fragments": fragments,
        "typed_relations": [],
        "provenance": {
            "source_path": f"{knowledge_id}.pdf",
            "sha256": knowledge_id.zfill(64)[-64:],
            "ingestion_method": "normalized",
        },
        "created_at": "2025-01-01T00:00:00+00:00",
        "updated_at": None,
    }


def _write(root: Path, folder: str, payload: dict) -> None:
    directory = root / "knowledge" / folder
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{payload['knowledge_id']}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def test_corpus_audit_never_approves_automatically(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "proposed",
        _knowledge("1", status="PROPUESTO", topic="privacidad infantil"),
    )

    report = CorpusAuditService(tmp_path).audit()

    assert report["governance"]["automatic_approval"] is False
    assert report["governance"]["human_review_required"] is True
    assert report["counts"]["approved"] == 0
    assert report["counts"]["ready_for_batch_review"] == 1

    original = json.loads(
        (tmp_path / "knowledge" / "proposed" / "1.json")
        .read_text(encoding="utf-8")
    )
    assert original["evidence_status"] == "PROPUESTO"


def test_low_quality_object_remains_in_quarantine(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "proposed",
        _knowledge(
            "2",
            status="PROPUESTO",
            topic="violencia digital",
            score_ready=False,
        ),
    )

    report = CorpusAuditService(tmp_path).audit()

    assert report["counts"]["remain_in_quarantine"] == 1
    item = report["queues"]["remain_in_quarantine"][0]
    assert item["recommendation"] == "REMAIN_IN_QUARANTINE"
    assert item["human_review_required"] is True


def test_training_gate_is_strict_and_reproducible(tmp_path: Path) -> None:
    for index in range(20):
        topic = "privacidad infantil" if index < 10 else "violencia digital"
        _write(
            tmp_path,
            "approved",
            _knowledge(
                f"{index + 10}",
                status="APROBADO",
                topic=topic,
                source="UNICEF" if index % 2 == 0 else "OECD",
            ),
        )

    service = CorpusAuditService(tmp_path)
    first = service.audit()
    second = service.audit()

    assert first["training_gate"]["ready_for_next_official_training"] is False
    assert first["training_gate"]["approved_objects"] == 20
    assert first["corpus_score"]["value"] == second["corpus_score"]["value"]
    assert first["coverage"] == second["coverage"]
    assert first["corpus_score"]["interpretation"].startswith(
        "Indicador descriptivo"
    )


def test_duplicate_detection_uses_sha_url_and_title(tmp_path: Path) -> None:
    first = _knowledge(
        "31",
        status="APROBADO",
        topic="privacidad infantil",
    )
    second = _knowledge(
        "32",
        status="APROBADO",
        topic="privacidad infantil",
    )
    second["title"] = first["title"]
    second["source_url_or_doi"] = first["source_url_or_doi"]
    second["provenance"]["sha256"] = first["provenance"]["sha256"]

    _write(tmp_path, "approved", first)
    _write(tmp_path, "approved", second)

    report = CorpusAuditService(tmp_path).audit()

    assert report["duplicates"]["duplicate_object_count"] == 2
    assert set(report["duplicates"]["duplicate_knowledge_ids"]) == {"31", "32"}
    assert report["training_gate"]["ready_for_next_official_training"] is False


def test_audit_persists_governed_outputs(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "proposed",
        _knowledge("41", status="PROPUESTO", topic="salud mental"),
    )

    service = CorpusAuditService(tmp_path)
    service.audit()

    expected = [
        "corpus_audit_report.json",
        "batch_review_queue.json",
        "individual_review_queue.json",
        "corpus_gap_report.json",
    ]
    for name in expected:
        assert (service.output_dir / name).exists()
