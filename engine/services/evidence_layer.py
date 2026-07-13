from __future__ import annotations

import hashlib
import re
from typing import Any


class EvidenceLayerService:
    """Builds traceable evidence fragments and typed relations.

    This service is deterministic and additive. It does not approve evidence
    and does not replace the Knowledge Contract.
    """

    def __init__(
        self,
        *,
        max_fragments: int = 40,
        min_fragment_chars: int = 80,
        max_fragment_chars: int = 1200,
    ) -> None:
        self.max_fragments = max_fragments
        self.min_fragment_chars = min_fragment_chars
        self.max_fragment_chars = max_fragment_chars

    def build(
        self,
        *,
        text: str,
        knowledge_id: str,
        source_path: str,
        language: str | None = None,
        topics: list[str] | None = None,
        digital_risks: list[str] | None = None,
        relation_to_ninia: str | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        fragments = self._fragments(
            text=text,
            knowledge_id=knowledge_id,
            source_path=source_path,
            language=language,
        )
        relations = self._relations(
            fragments=fragments,
            topics=topics or [],
            digital_risks=digital_risks or [],
            relation_to_ninia=relation_to_ninia,
        )
        return {
            "evidence_fragments": fragments,
            "typed_relations": relations,
        }

    def _fragments(
        self,
        *,
        text: str,
        knowledge_id: str,
        source_path: str,
        language: str | None,
    ) -> list[dict[str, Any]]:
        raw_blocks = [
            re.sub(r"\s+", " ", block).strip()
            for block in re.split(
                r"\n\s*\n|(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ])",
                text,
            )
            if re.sub(r"\s+", " ", block).strip()
        ]

        blocks: list[str] = []
        buffer = ""
        for block in raw_blocks:
            candidate = f"{buffer} {block}".strip()
            if len(candidate) < self.min_fragment_chars:
                buffer = candidate
                continue
            blocks.append(candidate)
            buffer = ""

        if buffer:
            if blocks and len(buffer) < self.min_fragment_chars:
                blocks[-1] = f"{blocks[-1]} {buffer}".strip()
            elif len(buffer) >= self.min_fragment_chars:
                blocks.append(buffer)

        if not blocks and text.strip():
            blocks = [re.sub(r"\s+", " ", text).strip()]

        fragments: list[dict[str, Any]] = []
        for position, block in enumerate(blocks[: self.max_fragments], start=1):
            excerpt = block[: self.max_fragment_chars].strip()
            seed = f"{knowledge_id}|{position}|{excerpt}".encode("utf-8")
            fragment_id = hashlib.sha256(seed).hexdigest()[:20]
            fragments.append(
                {
                    "fragment_id": fragment_id,
                    "position": position,
                    "text": excerpt,
                    "language": language,
                    "evidence_type": "DOCUMENT_EXCERPT",
                    "source_locator": {
                        "source_path": source_path,
                        "page": None,
                        "section": None,
                    },
                    "confidence": 1.0,
                    "validation_status": "PROPUESTO",
                }
            )
        return fragments

    def _relations(
        self,
        *,
        fragments: list[dict[str, Any]],
        topics: list[str],
        digital_risks: list[str],
        relation_to_ninia: str | None,
    ) -> list[dict[str, Any]]:
        relations: list[dict[str, Any]] = []
        fragment_ids = [item["fragment_id"] for item in fragments[:5]]

        for topic in sorted({str(item).strip() for item in topics if str(item).strip()}):
            relations.append(
                self._relation(
                    relation_type="HAS_TOPIC",
                    target_type="TOPIC",
                    target_value=topic,
                    source_fragment_ids=fragment_ids,
                )
            )

        for risk in sorted({
            str(item).strip()
            for item in digital_risks
            if str(item).strip() and str(item).strip() != "NO_CLASIFICADO"
        }):
            relations.append(
                self._relation(
                    relation_type="MENTIONS_DIGITAL_RISK",
                    target_type="DIGITAL_RISK",
                    target_value=risk,
                    source_fragment_ids=fragment_ids,
                )
            )

        if relation_to_ninia:
            relations.append(
                self._relation(
                    relation_type="RELATES_TO_NINIA",
                    target_type="NINIA_SCOPE",
                    target_value=str(relation_to_ninia).strip(),
                    source_fragment_ids=fragment_ids,
                )
            )

        return relations

    @staticmethod
    def _relation(
        *,
        relation_type: str,
        target_type: str,
        target_value: str,
        source_fragment_ids: list[str],
    ) -> dict[str, Any]:
        seed = (
            f"{relation_type}|{target_type}|{target_value}|"
            f"{','.join(source_fragment_ids)}"
        ).encode("utf-8")
        return {
            "relation_id": hashlib.sha256(seed).hexdigest()[:20],
            "relation_type": relation_type,
            "target": {
                "type": target_type,
                "value": target_value,
            },
            "source_fragment_ids": source_fragment_ids,
            "confidence": 1.0,
            "validation_status": "PROPUESTO",
        }
