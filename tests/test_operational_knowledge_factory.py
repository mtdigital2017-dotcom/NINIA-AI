
from __future__ import annotations

import json
from pathlib import Path

from engine.services.operational_knowledge_factory import (
    OperationalKnowledgeFactory,
)


class FakeAcquisition:
    def acquire(self, **kwargs):
        return {
            "documents_acquired": 1,
            "acquired": [{"request_id": "req-1"}],
            "rejected": [],
        }


class FakeValidation:
    def assess_request(self, request_id):
        return {"request_id": request_id, "recommendation": "READY"}


class FakeAudit:
    def __init__(self, ready=False):
        self.ready = ready

    def audit(self):
        return {
            "counts": {"proposed": 1, "approved": 0},
            "training_gate": {
                "ready_for_next_official_training": self.ready,
                "reasons": [] if self.ready else ["Corpus insuficiente."],
            },
        }


def test_factory_blocks_training_when_corpus_gate_is_closed(tmp_path: Path):
    service = OperationalKnowledgeFactory(
        tmp_path,
        acquisition_service=FakeAcquisition(),
        validation_service=FakeValidation(),
        corpus_audit_service=FakeAudit(ready=False),
    )

    result = service.run(train_if_ready=True)

    assert result["scientific_validation"]["successful"] == 1
    assert result["training"]["status"] == "BLOCKED_BY_CORPUS_GATE"
    assert result["governance"]["automatic_approval"] is False
    assert service.latest_path.exists()


def test_status_reports_real_counts_and_latest_run(tmp_path: Path):
    proposed = tmp_path / "knowledge" / "proposed"
    approved = tmp_path / "knowledge" / "approved"
    proposed.mkdir(parents=True)
    approved.mkdir(parents=True)
    (proposed / "p1.json").write_text("{}", encoding="utf-8")
    (approved / "a1.json").write_text("{}", encoding="utf-8")

    service = OperationalKnowledgeFactory(
        tmp_path,
        acquisition_service=FakeAcquisition(),
        validation_service=FakeValidation(),
        corpus_audit_service=FakeAudit(ready=False),
    )
    service.run(train_if_ready=False)
    status = service.status()

    assert status["knowledge"] == {"proposed": 1, "approved": 1}
    assert status["latest_run"]["status"] == "COMPLETED"


def test_factory_persists_auditable_manifest(tmp_path: Path):
    service = OperationalKnowledgeFactory(
        tmp_path,
        acquisition_service=FakeAcquisition(),
        validation_service=FakeValidation(),
        corpus_audit_service=FakeAudit(ready=False),
    )
    result = service.run(train_if_ready=False)

    path = Path(result["run_path"])
    saved = json.loads(path.read_text(encoding="utf-8"))

    assert saved["run_id"] == result["run_id"]
    assert saved["governance"]["human_review_required"] is True
    assert saved["training"]["status"] == "NOT_REQUESTED"
