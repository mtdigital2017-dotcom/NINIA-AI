from pathlib import Path
import inspect

from engine.services.hash_service import HashService
from engine.services.metadata_extractor import (
    MetadataExtractor,
)
from engine.services.knowledge_adapter import (
    KnowledgeContractAdapter,
)
from engine.services.knowledge_graph import (
    KnowledgeGraphService,
)
from engine.services.evidence_layer import (
    EvidenceLayerService,
)
from engine.services.regulatory_ingestion_service import (
    RegulatoryIngestionService,
)


def project_root():
    return Path(__file__).resolve().parents[1]


def document_path():
    return (
        project_root()
        / "data"
        / "regulatory_ingestion"
        / "documento_regulatorio_prueba.txt"
    )


def test_real_knowledge_adapter_contract():
    method = KnowledgeContractAdapter().build
    signature = inspect.signature(method)

    assert "raw_object" in signature.parameters
    assert "source_path" in signature.parameters
    assert "source_bytes" in signature.parameters


def test_real_evidence_layer_contract():
    method = EvidenceLayerService().build
    signature = inspect.signature(method)

    required = {
        "text",
        "knowledge_id",
        "source_path",
    }

    assert required.issubset(
        signature.parameters
    )


def test_orchestrator_reads_source_bytes():
    source = (
        project_root()
        / "engine"
        / "services"
        / "regulatory_ingestion_service.py"
    ).read_text(
        encoding="utf-8"
    )

    assert "source_bytes = path.read_bytes()" in source
    assert '"source_bytes": source_bytes' in source
    assert '"raw_object": {' in source


def test_orchestrator_supplies_evidence_contract():
    source = (
        project_root()
        / "engine"
        / "services"
        / "regulatory_ingestion_service.py"
    ).read_text(
        encoding="utf-8"
    )

    assert '"knowledge_id": knowledge_id' in source
    assert '"text": document_text' in source
    assert '"language": metadata_dict.get' in source


def test_real_base_contracts_execute():
    document = document_path()

    source_bytes = document.read_bytes()
    text = source_bytes.decode(
        "utf-8",
        errors="replace",
    )

    source_hash = HashService().sha256_file(
        document
    )

    metadata = MetadataExtractor().extract(
        document,
        text,
    )

    raw_object = {
        "metadata": metadata,
        "source_hash": source_hash,
        "source_path": str(document),
        "filename": document.name,
        "text": text,
    }

    contract = KnowledgeContractAdapter().build(
        raw_object,
        source_path=document,
        source_bytes=source_bytes,
    )

    assert isinstance(source_hash, str)
    assert len(source_hash) == 64
    assert isinstance(metadata, dict)
    assert isinstance(contract, dict)


def test_real_orchestrator_can_be_constructed():
    root = project_root()

    service = RegulatoryIngestionService(
        hash_service=HashService(),
        metadata_extractor=MetadataExtractor(),
        knowledge_adapter=KnowledgeContractAdapter(),
        knowledge_graph=KnowledgeGraphService(
            root
            / "NINIA_OS"
            / "KNOWLEDGE_GRAPH"
        ),
        evidence_layer=EvidenceLayerService(),
        global_observatory=None,
    )

    assert service.hash_service is not None
    assert service.metadata_extractor is not None
    assert service.knowledge_adapter is not None
    assert service.knowledge_graph is not None
    assert service.evidence_layer is not None
