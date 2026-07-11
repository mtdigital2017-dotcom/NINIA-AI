from pathlib import Path

import pytest

from engine.evidence_admission import (
    DuplicateEvidenceError,
    EvidenceAdmissionEngine,
    InvalidStatusTransitionError,
)


def payload(path: Path) -> dict:
    return {
        "uploaded_file_path": path,
        "original_filename": path.name,
        "title": "Privacidad infantil",
        "year": 2025,
        "author": "UNICEF",
        "source": "UNICEF",
        "document_type": "Informe institucional",
        "relation_to_ninia": (
            "Protección digital de NNA."
        ),
        "specialty": (
            "proteccion_infantil_digital"
        ),
        "researcher_name": "Investigadora",
        "researcher_email": "i@example.org",
        "institution": "Universidad",
        "country": "Colombia",
        "source_url_or_doi": (
            "https://www.unicef.org/"
        ),
        "declaration_accepted": True,
    }


def test_create_and_approve(
    tmp_path: Path,
):
    document = tmp_path / "evidence.txt"
    document.write_text(
        "contenido",
        encoding="utf-8",
    )

    engine = EvidenceAdmissionEngine(
        tmp_path
    )
    record = engine.create_request(
        **payload(document)
    )

    assert record["status"] == "CUARENTENA"
    assert record["confidence_index"] >= 90

    record = engine.update_status(
        request_id=record["id"],
        new_status="EN_VALIDACION",
        reviewer_name="Revisora",
        reviewer_email="r@example.org",
        review_notes="Metadatos verificados.",
    )

    record = engine.update_status(
        request_id=record["id"],
        new_status="APROBADO",
        reviewer_name="Revisora",
        reviewer_email="r@example.org",
        review_notes="Fuente verificada.",
        evidence_level="ALTO",
    )

    assert record["status"] == "APROBADO"


def test_duplicate(
    tmp_path: Path,
):
    document = tmp_path / "evidence.txt"
    document.write_text(
        "contenido",
        encoding="utf-8",
    )

    engine = EvidenceAdmissionEngine(
        tmp_path
    )
    engine.create_request(
        **payload(document)
    )

    with pytest.raises(
        DuplicateEvidenceError
    ):
        engine.create_request(
            **payload(document)
        )


def test_cannot_approve_directly(
    tmp_path: Path,
):
    document = tmp_path / "evidence.txt"
    document.write_text(
        "contenido",
        encoding="utf-8",
    )

    engine = EvidenceAdmissionEngine(
        tmp_path
    )
    record = engine.create_request(
        **payload(document)
    )

    with pytest.raises(
        InvalidStatusTransitionError
    ):
        engine.update_status(
            request_id=record["id"],
            new_status="APROBADO",
            reviewer_name="Revisora",
            reviewer_email="r@example.org",
            review_notes="Intento inválido.",
        )
