from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from engine.services.corpus_audit import CorpusAuditService
from engine.services.global_evidence_acquisition import (
    GlobalEvidenceAcquisitionService,
)


class GlobalObservatoryError(RuntimeError):
    """Raised when the global observatory cannot complete safely."""


@dataclass
class KnowledgeMission:
    """Mission-centric unit that organizes NINIA operational work."""

    mission_id: str
    slug: str
    title: str
    objective: str
    domains: list[str]
    regions: list[str]
    source_ids: list[str]
    status: str = "PLANNED"
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    evidence_count: int = 0
    knowledge_objects: int = 0
    media_products: int = 0
    ami_resources: int = 0
    action_products: int = 0
    lessons_learned: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class GlobalObservatoryService:
    """Mission-centric facade over existing NINIA services.

    It does not duplicate document processing, validation, dataset building,
    or training. It organizes existing capabilities around governed missions
    and exposes a stable status contract for the frontend.
    """

    SCHEMA_VERSION = "1.0"

    def __init__(
        self,
        base_dir: Path | str,
        *,
        acquisition_service: GlobalEvidenceAcquisitionService | None = None,
        corpus_audit_service: CorpusAuditService | None = None,
    ) -> None:
        self.base_dir = Path(base_dir)
        self.acquisition_service = acquisition_service or (
            GlobalEvidenceAcquisitionService(base_dir=self.base_dir)
        )
        self.corpus_audit_service = corpus_audit_service or (
            CorpusAuditService(self.base_dir)
        )
        self.missions_dir = self.base_dir / "operations" / "missions"
        self.latest_path = (
            self.base_dir / "operations" / "observatory_latest.json"
        )
        self.missions_dir.mkdir(parents=True, exist_ok=True)
        self.latest_path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _slug(value: str) -> str:
        normalized = "".join(
            character.lower() if character.isalnum() else "-"
            for character in value.strip()
        )
        return "-".join(
            part for part in normalized.split("-") if part
        )[:80]

    def _mission_path(self, mission_id: str) -> Path:
        safe_id = "".join(
            character
            for character in mission_id
            if character.isalnum() or character in {"-", "_"}
        )
        if not safe_id:
            raise GlobalObservatoryError("mission_id inválido.")
        return self.missions_dir / f"{safe_id}.json"

    def list_sources(self) -> list[dict[str, Any]]:
        """Return the governed source catalog already used by acquisition."""
        sources = self.acquisition_service.load_catalog()
        return [
            {
                **source.to_dict(),
                "trust_level": (
                    "OFFICIAL"
                    if source.source_type
                    in {"MULTILATERAL", "REGULATOR", "GOVERNMENT"}
                    else "SPECIALIZED"
                ),
                "health": "CONFIGURED",
            }
            for source in sources
        ]

    def create_mission(
        self,
        *,
        title: str,
        objective: str,
        domains: Iterable[str],
        regions: Iterable[str] | None = None,
        source_ids: Iterable[str] | None = None,
    ) -> dict[str, Any]:
        """Create a governed mission without launching acquisition."""
        title = title.strip()
        objective = objective.strip()
        if not title:
            raise GlobalObservatoryError("La misión requiere título.")
        if not objective:
            raise GlobalObservatoryError("La misión requiere objetivo.")

        available_sources = {
            source["source_id"] for source in self.list_sources()
        }
        requested_sources = list(dict.fromkeys(source_ids or []))
        unknown = [
            source_id
            for source_id in requested_sources
            if source_id not in available_sources
        ]
        if unknown:
            raise GlobalObservatoryError(
                "Fuentes no registradas: "
                + ", ".join(sorted(unknown))
            )

        mission = KnowledgeMission(
            mission_id=f"MIS-{uuid.uuid4().hex[:12].upper()}",
            slug=self._slug(title),
            title=title,
            objective=objective,
            domains=list(
                dict.fromkeys(
                    str(item).strip()
                    for item in domains
                    if str(item).strip()
                )
            ),
            regions=list(
                dict.fromkeys(
                    str(item).strip()
                    for item in (regions or ["GLOBAL"])
                    if str(item).strip()
                )
            ),
            source_ids=requested_sources,
        )
        if not mission.domains:
            raise GlobalObservatoryError(
                "La misión requiere al menos un dominio."
            )

        path = self._mission_path(mission.mission_id)
        path.write_text(
            json.dumps(
                mission.to_dict(),
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return mission.to_dict()

    def get_mission(self, mission_id: str) -> dict[str, Any]:
        path = self._mission_path(mission_id)
        if not path.exists():
            raise GlobalObservatoryError("Misión no encontrada.")
        return json.loads(path.read_text(encoding="utf-8"))

    def list_missions(self) -> list[dict[str, Any]]:
        missions: list[dict[str, Any]] = []
        for path in sorted(self.missions_dir.glob("*.json")):
            try:
                missions.append(
                    json.loads(path.read_text(encoding="utf-8"))
                )
            except (OSError, json.JSONDecodeError):
                continue
        return sorted(
            missions,
            key=lambda item: item.get("created_at", ""),
            reverse=True,
        )

    def ensure_regulatory_pilot(self) -> dict[str, Any]:
        """Create the Cullen regulatory pilot once, without ingesting PDFs."""
        for mission in self.list_missions():
            if mission.get("slug") == "regulatory-intelligence-cullen":
                return mission

        catalog_ids = [
            source["source_id"] for source in self.list_sources()
        ]
        preferred = [
            source_id
            for source_id in catalog_ids
            if source_id.upper()
            in {
                "EUROPEAN_COMMISSION",
                "COUNCIL_OF_EUROPE",
                "OECD",
                "UNICEF",
                "UNESCO",
            }
        ]
        return self.create_mission(
            title="Regulatory Intelligence Cullen",
            objective=(
                "Organizar evidencia comparada sobre regulación, "
                "corregulación, autorregulación, publicidad y protección "
                "de NNA en servicios audiovisuales y plataformas digitales."
            ),
            domains=[
                "Regulatory Intelligence",
                "Protection of Minors",
                "Advertising",
                "Platform Governance",
            ],
            regions=[
                "GLOBAL",
                "EUROPE",
                "LATIN_AMERICA",
            ],
            source_ids=preferred,
        )

    def status(self) -> dict[str, Any]:
        """Return a stable contract for API and frontend."""
        sources = self.list_sources()
        missions = self.list_missions()
        audit = self.corpus_audit_service.audit()
        counts = audit.get("counts", {})

        by_region: dict[str, int] = {}
        by_domain: dict[str, int] = {}
        for mission in missions:
            for region in mission.get("regions") or []:
                by_region[region] = by_region.get(region, 0) + 1
            for domain in mission.get("domains") or []:
                by_domain[domain] = by_domain.get(domain, 0) + 1

        payload = {
            "schema_version": self.SCHEMA_VERSION,
            "generated_at": self._now(),
            "identity": (
                "Plataforma Mundial de Inteligencia Científica para la "
                "Protección Integral de NNA en Entornos Digitales"
            ),
            "sources": {
                "configured": len(sources),
                "active": sum(
                    1
                    for source in sources
                    if source.get("enabled", True)
                ),
                "items": sources,
            },
            "missions": {
                "total": len(missions),
                "active": sum(
                    1
                    for mission in missions
                    if mission.get("status")
                    in {"PLANNED", "ACTIVE", "RUNNING"}
                ),
                "items": missions,
            },
            "knowledge": {
                "proposed": int(counts.get("proposed", 0)),
                "approved": int(counts.get("approved", 0)),
                "corpus_score": audit.get(
                    "corpus_score",
                    {},
                ).get("value", 0),
                "training_ready": audit.get(
                    "training_gate",
                    {},
                ).get(
                    "ready_for_next_official_training",
                    False,
                ),
            },
            "coverage": {
                "regions": by_region,
                "domains": by_domain,
                "note": (
                    "La cobertura describe el corpus de NINIA; "
                    "no clasifica países o regiones."
                ),
            },
            "ecosystems": {
                "global_observatory": "ACTIVE",
                "knowledge_engine": "ACTIVE",
                "media_center": "CONNECTED",
                "ami_center": "CONNECTED",
                "action_lab": "FOUNDATION",
                "organizational_learning": "FOUNDATION",
            },
        }
        self.latest_path.write_text(
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return payload
