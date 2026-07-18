from pathlib import Path
import json

import pytest

from engine.services.regulatory_ingestion_service import (
    RegulatoryDocumentNotFoundError,
    RegulatoryIngestionService,
)


class FakeHashService:
    def sha256_file(self, path):
        assert Path(path).exists()
        return "abc123"


class FakeMetadataExtractor:
    def extract(self, path):
        return {
            "title": Path(path).stem,
            "language": "es",
            "year": 2026,
        }


class FakeKnowledgeAdapter:
    def build(
        self,
        metadata,
        source_hash,
        source_path,
    ):
        return {
            "contract_version": "1.0",
            "metadata": metadata,
            "source_hash": source_hash,
            "source_path": source_path,
        }


class FakeKnowledgeGraph:
    def __init__(self):
        self.persisted = False

    def build(self, knowledge_contract):
        return {
            "nodes": [
                knowledge_contract
            ],
            "edges": [],
        }

    def validate(self, graph):
        return {
            "valid": bool(graph["nodes"])
        }

    def persist(self, graph):
        self.persisted = True
        return {
            "persisted": True,
            "node_count": len(graph["nodes"]),
        }


class FakeEvidenceLayer:
    def build(
        self,
        source_hash,
        metadata,
        knowledge_graph,
    ):
        return {
            "source_hash": source_hash,
            "metadata": metadata,
            "graph_node_count": len(
                knowledge_graph["nodes"]
            ),
            "traceable": True,
        }


class FakeGlobalObservatory:
    def get_mission(self, mission_id):
        return {
            "mission_id": mission_id,
            "status": "active",
        }

    def status(self):
        return {
            "status": "ready"
        }


def build_service():
    return RegulatoryIngestionService(
        hash_service=FakeHashService(),
        metadata_extractor=FakeMetadataExtractor(),
        knowledge_adapter=FakeKnowledgeAdapter(),
        knowledge_graph=FakeKnowledgeGraph(),
        evidence_layer=FakeEvidenceLayer(),
        global_observatory=FakeGlobalObservatory(),
    )


def test_regulatory_ingestion_pipeline(tmp_path):
    document = tmp_path / "decreto.txt"
    document.write_text(
        "Documento regulatorio de prueba.",
        encoding="utf-8",
    )

    service = build_service()

    result = service.ingest(
        document,
        mission_id="MIS-001",
        source_context={
            "jurisdiction": "Colombia"
        },
    )

    assert result.status == "completed"
    assert result.source_hash == "abc123"
    assert result.mission_id == "MIS-001"
    assert result.metadata["language"] == "es"

    assert result.knowledge_contract[
        "source_hash"
    ] == "abc123"

    assert result.knowledge_graph["nodes"]

    assert result.evidence["traceable"] is True

    assert result.observatory[
        "mission_id"
    ] == "MIS-001"

    completed_stages = {
        item["stage"]
        for item in result.trace
        if item["status"] == "completed"
    }

    assert "hash" in completed_stages
    assert "metadata" in completed_stages
    assert "knowledge_adapter" in completed_stages
    assert "knowledge_graph_build" in completed_stages
    assert "knowledge_graph_validate" in completed_stages
    assert "knowledge_graph_persist" in completed_stages
    assert "evidence" in completed_stages
    assert (
        "global_observatory_get_mission"
        in completed_stages
    )


def test_regulatory_ingestion_json_output(tmp_path):
    document = tmp_path / "resolucion.txt"
    document.write_text(
        "Resolución regulatoria.",
        encoding="utf-8",
    )

    output = tmp_path / "result.json"

    service = build_service()

    destination = service.ingest_to_json(
        document,
        output,
        mission_id="MIS-002",
    )

    assert destination.exists()

    payload = json.loads(
        destination.read_text(
            encoding="utf-8"
        )
    )

    assert payload["status"] == "completed"
    assert payload["source_hash"] == "abc123"
    assert payload["mission_id"] == "MIS-002"
    assert payload["evidence"]["traceable"] is True


def test_missing_regulatory_document_is_rejected(
    tmp_path,
):
    service = build_service()

    missing = tmp_path / "missing.pdf"

    with pytest.raises(
        RegulatoryDocumentNotFoundError
    ):
        service.ingest(missing)


def test_graph_persistence_can_be_disabled(tmp_path):
    document = tmp_path / "ley.txt"
    document.write_text(
        "Ley regulatoria.",
        encoding="utf-8",
    )

    graph = FakeKnowledgeGraph()

    service = RegulatoryIngestionService(
        hash_service=FakeHashService(),
        metadata_extractor=FakeMetadataExtractor(),
        knowledge_adapter=FakeKnowledgeAdapter(),
        knowledge_graph=graph,
        evidence_layer=FakeEvidenceLayer(),
        global_observatory=None,
    )

    result = service.ingest(
        document,
        persist_graph=False,
    )

    assert result.status == "completed"
    assert graph.persisted is False

    stages = {
        item["stage"]
        for item in result.trace
    }

    assert "knowledge_graph_persist" not in stages
