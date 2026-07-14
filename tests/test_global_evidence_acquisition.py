from __future__ import annotations

import json
from pathlib import Path

import httpx

from engine.services.global_evidence_acquisition import (
    GlobalEvidenceAcquisitionService,
)


class FakeAdmissionEngine:
    def admit_and_process(self, **kwargs):
        return {
            "admission_record": {
                "id": "request-1",
                "status": "CUARENTENA",
            },
            "processing_result": {
                "normalized_knowledge_object": {
                    "knowledge_id": "knowledge-1",
                    "evidence_status": "PROPUESTO",
                }
            },
        }


def _catalog(tmp_path: Path) -> Path:
    path = tmp_path / "official_sources.json"
    path.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "source_id": "example",
                        "organization": "Example Authority",
                        "jurisdiction": "TEST",
                        "domains": ["official.example"],
                        "discovery_urls": [
                            "https://official.example/publications"
                        ],
                        "topics": ["children"],
                        "enabled": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    return path


def test_discovery_and_acquisition_reuse_existing_intake(tmp_path):
    pdf_bytes = b"%PDF-1.4\n% NINIA test document\n"

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/publications":
            return httpx.Response(
                200,
                headers={"content-type": "text/html"},
                text=(
                    '<html><body><a href="/child-safety.pdf">'
                    "Children digital safety report</a></body></html>"
                ),
            )
        if request.url.path == "/child-safety.pdf":
            return httpx.Response(
                200,
                headers={"content-type": "application/pdf"},
                content=pdf_bytes,
            )
        return httpx.Response(404)

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        follow_redirects=True,
    )
    service = GlobalEvidenceAcquisitionService(
        base_dir=tmp_path,
        catalog_path=_catalog(tmp_path),
        admission_engine=FakeAdmissionEngine(),
        client=client,
        request_delay_seconds=0,
    )

    manifest = service.acquire(max_total_documents=1)

    assert manifest["documents_discovered"] == 1
    assert manifest["documents_acquired"] == 1
    assert manifest["acquired"][0]["request_status"] == "CUARENTENA"
    assert manifest["acquired"][0]["knowledge_status"] == "PROPUESTO"
    assert manifest["governance"]["automatic_approval"] is False
    assert Path(manifest["manifest_path"]).exists()


def test_unofficial_document_is_rejected(tmp_path):
    service = GlobalEvidenceAcquisitionService(
        base_dir=tmp_path,
        catalog_path=_catalog(tmp_path),
        admission_engine=FakeAdmissionEngine(),
        client=httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(404))),
    )
    source = service.load_catalog()[0]

    assert service._authorized(
        "https://official.example/report.pdf",
        source,
    )
    assert not service._authorized(
        "https://unofficial.example/report.pdf",
        source,
    )
