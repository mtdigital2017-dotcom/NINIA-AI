from pathlib import Path
import json


def project_root():
    return Path(__file__).resolve().parents[1]


def reports_dir():
    return (
        project_root()
        / "NINIA_OS"
        / "DT_RUNTIME"
        / "reports"
    )


def test_sprint_3_5_integration_is_completed():
    path = (
        project_root()
        / "data"
        / "regulatory_ingestion"
        / "outputs"
        / "regulatory_ingestion_result.json"
    )

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert payload["status"] == "completed"


def test_sprint_3_5_trace_is_complete():
    path = (
        project_root()
        / "data"
        / "regulatory_ingestion"
        / "outputs"
        / "regulatory_ingestion_result.json"
    )

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    required = {
        "hash",
        "metadata",
        "knowledge_adapter",
        "knowledge_graph_build",
        "knowledge_graph_validate",
        "evidence",
        "global_observatory_status",
    }

    completed = {
        item["stage"]
        for item in payload["trace"]
        if item["status"] == "completed"
    }

    assert required.issubset(completed)


def test_sprint_3_5_manifest_exists():
    path = (
        reports_dir()
        / "SPRINT_3_5_ARTIFACT_MANIFEST.json"
    )

    assert path.exists()

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert payload["sprint"] == "3.5"
    assert payload["status"] == "closed"
    assert payload["artifacts"]


def test_master_memory_contains_closure():
    candidates = [
        project_root() / "MASTER_MEMORY.md",
        project_root() / "MASTER_MEMORY.txt",
        project_root() / "PROJECT_MEMORY.md",
        project_root() / "PROJECT_MEMORY.txt",
        (
            project_root()
            / "NINIA_OS"
            / "MASTER_MEMORY.md"
        ),
        (
            project_root()
            / "NINIA_OS"
            / "MASTER_MEMORY.txt"
        ),
        (
            project_root()
            / "NINIA_OS"
            / "PROJECT_MEMORY.md"
        ),
        (
            project_root()
            / "NINIA_OS"
            / "PROJECT_MEMORY.txt"
        ),
    ]

    existing = [
        path
        for path in candidates
        if path.exists()
    ]

    assert existing

    text = existing[0].read_text(
        encoding="utf-8"
    )

    assert (
        "<!-- NINIA_SPRINT_3_5_CLOSURE -->"
        in text
    )

    assert (
        "Sprint 3.6"
        in text
    )


def test_global_observatory_catalog_exists():
    path = (
        project_root()
        / "NINIA_OS"
        / "GLOBAL_OBSERVATORY"
        / "data"
        / "source_catalog"
        / "official_sources.json"
    )

    assert path.exists()

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert isinstance(payload, list)
