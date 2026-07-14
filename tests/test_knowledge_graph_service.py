from __future__ import annotations

import json
from pathlib import Path

from engine.services.knowledge_graph import KnowledgeGraphService


def _write_approved_knowledge(base_dir: Path) -> Path:
    approved = base_dir / "knowledge" / "approved"
    approved.mkdir(parents=True, exist_ok=True)
    path = approved / "knowledge-001.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "knowledge_id": "knowledge-001",
                "title": "Protección infantil digital",
                "content": "Contenido aprobado.",
                "source": "UNICEF",
                "source_url_or_doi": "https://www.unicef.org/report",
                "authors": ["UNICEF"],
                "publication_year": 2025,
                "language": "es",
                "topics": ["privacidad infantil"],
                "entities": [
                    {"type": "ORGANIZATION", "value": "UNICEF"}
                ],
                "digital_risks": ["privacidad infantil"],
                "evidence_level": "ALTO",
                "evidence_status": "APROBADO",
                "relation_to_ninia": "Protección de NNA",
                "specialty": "proteccion_infantil_digital",
                "evidence_fragments": [
                    {
                        "fragment_id": "fragment-001",
                        "position": 1,
                        "text": "La privacidad infantil debe protegerse.",
                        "language": "es",
                        "evidence_type": "DOCUMENT_EXCERPT",
                        "source_locator": {
                            "source_path": "report.pdf",
                            "page": 1,
                            "section": None,
                        },
                        "confidence": 1.0,
                        "validation_status": "APROBADO",
                    }
                ],
                "typed_relations": [
                    {
                        "relation_id": "relation-001",
                        "relation_type": "HAS_TOPIC",
                        "target_type": "TOPIC",
                        "target_value": "privacidad infantil",
                        "source_fragment_ids": ["fragment-001"],
                        "confidence": 1.0,
                        "validation_status": "APROBADO",
                    }
                ],
                "provenance": {
                    "source_path": "report.pdf",
                    "sha256": "a" * 64,
                    "ingestion_method": "normalized",
                },
                "created_at": "2025-01-01T00:00:00+00:00",
                "updated_at": None,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return path


def test_builds_traceable_graph_from_approved_knowledge(tmp_path: Path) -> None:
    _write_approved_knowledge(tmp_path)
    service = KnowledgeGraphService(tmp_path)

    graph = service.build()

    assert graph["source_policy"] == "APPROVED_KNOWLEDGE_ONLY"
    assert graph["statistics"]["knowledge_objects"] == 1
    assert graph["statistics"]["nodes"] >= 4
    assert graph["statistics"]["edges"] >= 4
    assert graph["validation"]["valid"] is True
    assert (
        tmp_path / "knowledge" / "graph" / "knowledge_graph.json"
    ).exists()

    document = next(
        node for node in graph["nodes"]
        if node["node_type"] == "DOCUMENT"
    )
    assert document["properties"]["knowledge_id"] == "knowledge-001"

    assert all(edge["knowledge_id"] for edge in graph["edges"])
    assert any(
        edge["relation_type"] == "SUPPORTED_BY"
        for edge in graph["edges"]
    )


def test_ignores_non_approved_knowledge(tmp_path: Path) -> None:
    proposed = tmp_path / "knowledge" / "approved"
    proposed.mkdir(parents=True)
    (proposed / "proposed.json").write_text(
        json.dumps(
            {
                "knowledge_id": "proposed-001",
                "title": "No aprobado",
                "evidence_status": "PROPUESTO",
            }
        ),
        encoding="utf-8",
    )

    graph = KnowledgeGraphService(tmp_path).build()

    assert graph["statistics"] == {
        "knowledge_objects": 0,
        "nodes": 0,
        "edges": 0,
    }
    assert graph["validation"]["valid"] is True
