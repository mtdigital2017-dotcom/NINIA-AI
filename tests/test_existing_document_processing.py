from pathlib import Path

from engine.ninia_engine import NiniaEngine


def test_existing_document_processing_is_preserved(
    tmp_path: Path,
):
    document = tmp_path / "unicef_2025.txt"
    document.write_text(
        "UNICEF analiza privacidad infantil "
        "y plataformas digitales.",
        encoding="utf-8",
    )

    engine = NiniaEngine(
        base_dir=tmp_path
    )
    result = engine.process_document(
        document,
        {
            "title": "Documento de prueba",
            "status": "PROPUESTO",
        },
    )

    assert result["ok"] is True
    assert (
        result["knowledge_object"]["status"]
        == "PROPUESTO"
    )
    assert Path(
        result["saved_to"]
    ).exists()
