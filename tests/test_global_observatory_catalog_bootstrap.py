from pathlib import Path
import json
import inspect

from engine.services.global_observatory import (
    GlobalObservatoryService,
)
from engine.services.global_evidence_acquisition import (
    GlobalEvidenceAcquisitionService,
)


def project_root():
    return Path(__file__).resolve().parents[1]


def observatory_dir():
    return (
        project_root()
        / "NINIA_OS"
        / "GLOBAL_OBSERVATORY"
    )


def catalog_path():
    return (
        observatory_dir()
        / "data"
        / "source_catalog"
        / "official_sources.json"
    )


def test_official_sources_catalog_exists():
    path = catalog_path()

    assert path.exists()
    assert path.is_file()


def test_official_sources_catalog_is_valid_json():
    payload = json.loads(
        catalog_path().read_text(
            encoding="utf-8"
        )
    )

    assert isinstance(
        payload,
        (list, dict),
    )


def test_acquisition_service_constructor_is_keyword_only():
    signature = inspect.signature(
        GlobalEvidenceAcquisitionService
    )

    base_dir_parameter = signature.parameters[
        "base_dir"
    ]

    assert (
        base_dir_parameter.kind
        == inspect.Parameter.KEYWORD_ONLY
    )


def test_acquisition_service_loads_catalog():
    service = GlobalEvidenceAcquisitionService(
        base_dir=observatory_dir()
    )

    result = service.load_catalog()

    assert result is not None
    assert isinstance(result, list)


def test_global_observatory_status_executes():
    service = GlobalObservatoryService(
        observatory_dir()
    )

    status = service.status()

    assert status is not None
    assert isinstance(status, dict)
    assert status["sources"]["configured"] >= 0
    assert status["ecosystems"][
        "global_observatory"
    ] == "ACTIVE"


def test_catalog_is_inside_ninia_os():
    root = project_root().resolve()
    path = catalog_path().resolve()

    assert root in path.parents
    assert "NINIA_OS" in path.parts
    assert "GLOBAL_OBSERVATORY" in path.parts
