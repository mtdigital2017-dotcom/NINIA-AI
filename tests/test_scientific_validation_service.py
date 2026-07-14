from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import app
from engine.evidence_admission import EvidenceAdmissionEngine
from engine.services.scientific_validation import (
    ScientificValidationError,
    ScientificValidationService,
)


def _create_processed_request(tmp_path: Path) -> tuple[
    EvidenceAdmissionEngine,
    dict,
]:
    document = tmp_path / "official.txt"
    document.write_text(
        (
            "UNICEF analiza privacidad infantil y plataformas digitales. "
            "La protección de datos de niñas y niños es prioritaria."
        ),
        encoding="utf-8",
    )
    engine = EvidenceAdmissionEngine(base_dir=tmp_path)
    result = engine.admit_and_process(
        uploaded_file_path=document,
        original_filename=document.name,
        title="Privacidad infantil en plataformas",
        year=2025,
        author="UNICEF",
        source="UNICEF",
        document_type="informe institucional",
        relation_to_ninia=(
            "Evidencia directamente relacionada con la protección "
            "de niñas, niños y adolescentes en entornos digitales."
        ),
        specialty="proteccion_infantil_digital",
        researcher_name="Investigadora NINIA",
        researcher_email="researcher@ninia.org",
        institution="NINIA",
        country="Colombia",
        source_url_or_doi="https://www.unicef.org/report",
        declaration_accepted=True,
    )
    return engine, result["admission_record"]


def test_scientific_validation_is_non_binding(tmp_path):
    engine, request = _create_processed_request(tmp_path)
    service = ScientificValidationService(
        base_dir=tmp_path,
        admission_engine=engine,
    )

    report = service.assess_request(request["id"])

    assert report["governance"]["automatic_approval"] is False
    assert report["governance"]["binding_decision"] is False
    assert report["governance"]["human_review_required"] is True
    assert report["current_request_status"] == "CUARENTENA"
    assert report["current_knowledge_status"] == "PROPUESTO"

    unchanged = engine.get_request(request["id"])
    assert unchanged["status"] == "CUARENTENA"


def test_scientific_validation_persists_and_lists(tmp_path):
    engine, request = _create_processed_request(tmp_path)
    service = ScientificValidationService(
        base_dir=tmp_path,
        admission_engine=engine,
    )

    generated = service.assess_request(request["id"])
    loaded = service.get_report(request["id"])
    listed = service.list_reports()

    assert Path(generated["saved_to"]).exists()
    assert loaded["request_id"] == request["id"]
    assert len(listed) == 1
    assert set(generated["dimensions"]) == {
        "source_traceability",
        "metadata_completeness",
        "evidence_layer_quality",
        "ninia_relevance",
        "document_currency",
    }


def test_scientific_validation_requires_knowledge_object(tmp_path):
    document = tmp_path / "pending.txt"
    document.write_text("Documento pendiente.", encoding="utf-8")
    engine = EvidenceAdmissionEngine(base_dir=tmp_path)
    request = engine.create_request(
        uploaded_file_path=document,
        original_filename=document.name,
        title="Documento pendiente",
        year=2025,
        author="Autor",
        source="Fuente",
        document_type="informe institucional",
        relation_to_ninia="Relación pendiente con NINIA.",
        specialty="proteccion_infantil_digital",
        researcher_name="Investigadora",
        researcher_email="researcher@ninia.org",
        institution="NINIA",
        country="Colombia",
        declaration_accepted=True,
    )
    service = ScientificValidationService(
        base_dir=tmp_path,
        admission_engine=engine,
    )

    with pytest.raises(ScientificValidationError):
        service.assess_request(request["id"])


def test_api_exposes_scientific_validation_routes():
    paths = app.openapi()["paths"]
    assert (
        "/evidence/requests/{request_id}/scientific-validation"
        in paths
    )
    assert "/scientific-validation/reports" in paths
