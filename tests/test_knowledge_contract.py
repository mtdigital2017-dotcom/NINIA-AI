from pathlib import Path

import pytest

from knowledge.contract import (
    KnowledgeContractError,
    normalize_knowledge_object,
    validate_knowledge_object,
)


def test_normalizes_legacy_object():
    normalized = normalize_knowledge_object(
        {
            "id": "legacy-001",
            "name": "Documento histórico",
            "text": "Contenido",
            "source": "Drive",
            "status": "PROPUESTO",
        },
        source_path="legacy/document.json",
    )

    assert normalized["knowledge_id"] == "legacy-001"
    assert normalized["title"] == "Documento histórico"
    assert normalized["evidence_status"] == "PROPUESTO"
    assert len(normalized["provenance"]["sha256"]) == 64


def test_normalizes_current_object():
    normalized = normalize_knowledge_object(
        {
            "document_id": "current-001",
            "title": "Documento actual",
            "content": {"text": "Contenido"},
            "source": "upload",
            "evidence_status": "EN_VALIDACION",
            "created_at": "2026-01-01T00:00:00+00:00",
        },
        source_path="knowledge/proposed/current.json",
    )

    validate_knowledge_object(normalized)
    assert normalized["schema_version"] == "1.0"


def test_never_accepts_invalid_status():
    with pytest.raises(KnowledgeContractError):
        normalize_knowledge_object(
            {
                "title": "Documento",
                "content": "Contenido",
                "source": "upload",
                "status": "AUTO_APROBADO",
            },
            source_path="invalid.json",
        )
