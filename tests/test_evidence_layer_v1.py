from pathlib import Path

import pytest

from engine.ninia_engine import NiniaEngine
from engine.services.evidence_layer import EvidenceLayerService
from knowledge.contract import (
    KnowledgeContractError,
    normalize_knowledge_object,
    validate_knowledge_object,
)


def test_old_knowledge_object_remains_valid():
    normalized = normalize_knowledge_object(
        {
            "title": "Documento heredado",
            "content": "Contenido heredado válido.",
            "source": "Fuente",
            "status": "PROPUESTO",
        },
        source_path="legacy.txt",
        source_bytes=b"legacy",
    )

    assert normalized["schema_version"] == "1.0"
    assert normalized["evidence_fragments"] == []
    assert normalized["typed_relations"] == []
    validate_knowledge_object(normalized)


def test_evidence_layer_builds_traceable_fragments_and_relations():
    service = EvidenceLayerService(min_fragment_chars=20)
    layer = service.build(
        text=(
            "La privacidad infantil requiere protección reforzada. "
            "Las plataformas digitales deben reducir riesgos para niños."
        ),
        knowledge_id="knowledge-1",
        source_path="document.txt",
        language="es",
        topics=["privacidad"],
        digital_risks=["privacidad infantil"],
        relation_to_ninia="Protección digital de NNA",
    )

    assert layer["evidence_fragments"]
    assert layer["typed_relations"]
    fragment_ids = {
        item["fragment_id"]
        for item in layer["evidence_fragments"]
    }
    for relation in layer["typed_relations"]:
        assert set(relation["source_fragment_ids"]).issubset(fragment_ids)
        assert relation["validation_status"] == "PROPUESTO"


def test_contract_rejects_relation_to_unknown_fragment():
    with pytest.raises(KnowledgeContractError):
        normalize_knowledge_object(
            {
                "title": "Documento",
                "content": "Contenido.",
                "source": "Fuente",
                "status": "PROPUESTO",
                "typed_relations": [
                    {
                        "relation_id": "r1",
                        "relation_type": "HAS_TOPIC",
                        "target": {
                            "type": "TOPIC",
                            "value": "privacidad",
                        },
                        "source_fragment_ids": ["missing"],
                        "confidence": 1.0,
                        "validation_status": "PROPUESTO",
                    }
                ],
            },
            source_path="document.txt",
            source_bytes=b"document",
        )


def test_ninia_engine_persists_evidence_layer(tmp_path):
    source = tmp_path / "unicef_privacidad.txt"
    source.write_text(
        (
            "UNICEF analiza la privacidad infantil en plataformas digitales. "
            "La protección de datos personales de niñas y niños es prioritaria."
        ),
        encoding="utf-8",
    )

    result = NiniaEngine(base_dir=tmp_path).process_document(
        source,
        metadata={
            "source_entity": "UNICEF",
            "topics": ["privacidad infantil"],
            "relation_to_ninia": "Protección digital de NNA",
        },
    )
    knowledge = result["normalized_knowledge_object"]

    assert knowledge["evidence_fragments"]
    assert knowledge["typed_relations"]
    assert all(
        item["validation_status"] == "PROPUESTO"
        for item in knowledge["evidence_fragments"]
    )
    assert Path(result["saved_to"]).exists()
