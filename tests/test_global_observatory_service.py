from __future__ import annotations

from pathlib import Path

import pytest

from engine.services.global_observatory import (
    GlobalObservatoryError,
    GlobalObservatoryService,
)


class FakeAcquisition:
    def load_catalog(self):
        from engine.services.global_evidence_acquisition import (
            OfficialSource,
        )

        return [
            OfficialSource(
                source_id="UNICEF",
                organization="UNICEF",
                jurisdiction="GLOBAL",
                domains=("unicef.org",),
                discovery_urls=(
                    "https://www.unicef.org/reports",
                ),
                source_type="MULTILATERAL",
                languages=("en", "es"),
                topics=("child online protection",),
            )
        ]


class FakeAudit:
    def audit(self):
        return {
            "counts": {
                "proposed": 4,
                "approved": 3,
            },
            "corpus_score": {
                "value": 71.5,
            },
            "training_gate": {
                "ready_for_next_official_training": False,
            },
        }


def service(tmp_path: Path) -> GlobalObservatoryService:
    return GlobalObservatoryService(
        tmp_path,
        acquisition_service=FakeAcquisition(),
        corpus_audit_service=FakeAudit(),
    )


def test_create_and_list_mission(tmp_path):
    observatory = service(tmp_path)
    mission = observatory.create_mission(
        title="Regulatory Intelligence",
        objective="Cerrar brechas regulatorias.",
        domains=["Regulatory Intelligence"],
        regions=["GLOBAL"],
        source_ids=["UNICEF"],
    )

    assert mission["mission_id"].startswith("MIS-")
    assert (
        observatory.get_mission(
            mission["mission_id"]
        )["title"]
        == "Regulatory Intelligence"
    )
    assert len(observatory.list_missions()) == 1


def test_unknown_source_is_rejected(tmp_path):
    observatory = service(tmp_path)

    with pytest.raises(GlobalObservatoryError):
        observatory.create_mission(
            title="Misión",
            objective="Objetivo",
            domains=["AMI"],
            source_ids=["UNKNOWN"],
        )


def test_status_contract(tmp_path):
    observatory = service(tmp_path)
    observatory.create_mission(
        title="AMI Global",
        objective="Fortalecer alfabetización mediática.",
        domains=["AMI"],
        regions=["GLOBAL"],
        source_ids=["UNICEF"],
    )

    status = observatory.status()

    assert status["sources"]["configured"] == 1
    assert status["missions"]["total"] == 1
    assert status["knowledge"]["approved"] == 3
    assert status["knowledge"]["corpus_score"] == 71.5
    assert status["coverage"]["regions"]["GLOBAL"] == 1
    assert status["ecosystems"]["ami_center"] == "CONNECTED"
