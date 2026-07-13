from pathlib import Path

from engine.ninia_engine import NiniaEngine
from engine.services.doi_extractor import DOIExtractor
from engine.services.language_detector import LanguageDetector


def test_language_detector_handles_spanish_and_english():
    detector = LanguageDetector()
    assert detector.detect(
        "La protección de los derechos de niñas y niños para entornos digitales."
    ) == "es"
    assert detector.detect(
        "The protection of children and their digital rights."
    ) == "en"


def test_doi_extractor():
    assert DOIExtractor().extract(
        "Disponible en https://doi.org/10.1234/ABC.2025.10."
    ) == "10.1234/ABC.2025.10"


def test_engine_saves_normalized_contract(tmp_path):
    source = tmp_path / "UNICEF_proteccion_2025.txt"
    source.write_text(
        (
            "Protección de la niñez en entornos digitales\n"
            "Autores: Ana Pérez; Luis Gómez\n"
            "UNICEF 2025. DOI 10.1234/ninia.2025.1\n"
            "La protección de los derechos de niñas y niños "
            "es prioritaria para las plataformas digitales."
        ),
        encoding="utf-8",
    )

    result = NiniaEngine(base_dir=tmp_path).process_document(source)
    raw = result["knowledge_object"]
    normalized = result["normalized_knowledge_object"]

    assert raw["language"] == "es"
    assert raw["authors"] == ["Ana Pérez", "Luis Gómez"]
    assert raw["source_url_or_doi"] == "10.1234/ninia.2025.1"
    assert len(raw["file_sha256"]) == 64

    assert normalized["schema_version"] == "1.0"
    assert normalized["evidence_status"] == "PROPUESTO"
    assert normalized["language"] == "es"
    assert len(normalized["provenance"]["sha256"]) == 64

    saved = Path(result["saved_to"])
    assert saved.exists()
    assert saved.parent.name == "proposed"
