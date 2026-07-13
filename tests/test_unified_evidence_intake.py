from pathlib import Path

from engine.evidence_admission import EvidenceAdmissionEngine


def payload(path: Path) -> dict:
    return {
        "uploaded_file_path": path,
        "original_filename": path.name,
        "title": "Protección digital infantil",
        "year": 2025,
        "author": "UNICEF",
        "source": "UNICEF",
        "document_type": "Informe institucional",
        "relation_to_ninia": "Protección digital de NNA.",
        "specialty": "proteccion_infantil_digital",
        "researcher_name": "NINIA CORE",
        "researcher_email": "core@ninia.org",
        "institution": "NINIA",
        "country": "Colombia",
        "source_url_or_doi": "https://www.unicef.org/",
        "declaration_accepted": True,
    }


def test_unified_intake_creates_quarantine_and_proposed_knowledge(
    tmp_path: Path,
):
    document = tmp_path / "unicef_2025.txt"
    document.write_text(
        "UNICEF analiza privacidad infantil y plataformas digitales.",
        encoding="utf-8",
    )

    engine = EvidenceAdmissionEngine(tmp_path)
    result = engine.admit_and_process(**payload(document))

    admission = result["admission_record"]
    knowledge = result["processing_result"][
        "normalized_knowledge_object"
    ]

    assert admission["status"] == "CUARENTENA"
    assert admission["processing_status"] == "PROCESADO"
    assert admission["knowledge_id"] == knowledge["knowledge_id"]
    assert admission["knowledge_status"] == "PROPUESTO"
    assert knowledge["evidence_status"] == "PROPUESTO"
    assert Path(admission["knowledge_object_path"]).exists()


def test_review_transition_synchronizes_knowledge_status(
    tmp_path: Path,
):
    document = tmp_path / "unicef_2025.txt"
    document.write_text(
        "UNICEF analiza privacidad infantil y plataformas digitales.",
        encoding="utf-8",
    )

    engine = EvidenceAdmissionEngine(tmp_path)
    result = engine.admit_and_process(**payload(document))
    request_id = result["admission_record"]["id"]

    validating = engine.update_status(
        request_id=request_id,
        new_status="EN_VALIDACION",
        reviewer_name="Revisora",
        reviewer_email="review@ninia.org",
        review_notes="Metadatos revisados.",
    )
    assert validating["knowledge_status"] == "EN_VALIDACION"
    assert Path(validating["knowledge_object_path"]).parent.name == "in_validation"

    approved = engine.update_status(
        request_id=request_id,
        new_status="APROBADO",
        reviewer_name="Revisora",
        reviewer_email="review@ninia.org",
        review_notes="Fuente y contenido verificados.",
        evidence_level="ALTO",
    )
    assert approved["knowledge_status"] == "APROBADO"
    assert Path(approved["knowledge_object_path"]).parent.name == "approved"
