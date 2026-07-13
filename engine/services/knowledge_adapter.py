from __future__ import annotations

from pathlib import Path
from typing import Any

from knowledge.contract import (
    normalize_knowledge_object,
    validate_knowledge_object,
)


class KnowledgeContractAdapter:
    """Adapta la salida heredada de NiniaEngine al contrato oficial v1."""

    def build(
        self,
        raw_object: dict[str, Any],
        *,
        source_path: Path | str,
        source_bytes: bytes,
    ) -> dict[str, Any]:
        normalized = normalize_knowledge_object(
            raw_object,
            source_path=str(source_path),
            source_bytes=source_bytes,
        )
        validate_knowledge_object(normalized)
        return normalized
