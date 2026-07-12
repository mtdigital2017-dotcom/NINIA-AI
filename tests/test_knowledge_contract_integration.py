from pathlib import Path

from engine.ninia_engine import NiniaEngine
from knowledge.contract import (
    normalize_knowledge_object,
    validate_knowledge_object,
)


def test_real_engine_output_normalizes_to_contract(tmp_path):
    source = tmp_path / "UNICEF_privacidad_infancia_2025.txt"
    source.write_text(
        (
            "UNICEF 2025. La privacidad infantil y la protección de datos "
            "personales son esenciales para niñas, niños y adolescentes "
            "en plataformas digitales y redes sociales."
        ),
        encoding="utf-8",
    )

    engine = NiniaEngine(base_dir=tmp_path)
    result = engine.process_document(
        source,
        metadata={
            "title": "Privacidad infantil en plataformas digitales",
            "source_url_or_doi": "https://example.org/unicef-2025",
            "evidence_level": "NO_CLASIFICADO",
            "status": "PROPUESTO",
        },
    )

    raw = result["knowledge_object"]
    normalized = normalize_knowledge_object(
        raw,
        source_path=result["saved_to"],
        source_bytes=source.read_bytes(),
    )

    validate_knowledge_object(normalized)

    assert raw["status"] == "PROPUESTO"
    assert normalized["evidence_status"] == "PROPUESTO"
    assert normalized["knowledge_id"] == raw["id"]
    assert normalized["title"] == raw["title"]
    assert normalized["publication_year"] == 2025
    assert normalized["provenance"]["source_path"] == result["saved_to"]
    assert len(normalized["provenance"]["sha256"]) == 64


def test_contract_never_auto_approves_engine_output(tmp_path):
    source = tmp_path / "evidencia.txt"
    source.write_text(
        "Documento científico sobre protección infantil digital.",
        encoding="utf-8",
    )

    raw = NiniaEngine(base_dir=tmp_path).process_document(source)[
        "knowledge_object"
    ]

    normalized = normalize_knowledge_object(
        raw,
        source_path="knowledge/proposed/evidencia.json",
        source_bytes=source.read_bytes(),
    )

    assert normalized["evidence_status"] == "PROPUESTO"
    assert normalized["evidence_status"] != "APROBADO"
