from pathlib import Path
from engine.ninia_engine import NiniaEngine


def test_engine_process_txt(tmp_path):
    test_file = tmp_path / "unicef_2024_privacidad.txt"
    test_file.write_text(
        "UNICEF 2024 privacidad infantil desinformación plataformas digitales.",
        encoding="utf-8",
    )

    engine = NiniaEngine(base_dir=tmp_path)
    result = engine.process_document(test_file, metadata={"title": "Prueba NINIA"})

    assert result["ok"] is True
    assert result["knowledge_object"]["status"] == "PROPUESTO"
    assert Path(result["saved_to"]).exists()
