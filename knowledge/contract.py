from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ALLOWED_STATUSES = {
    "PROPUESTO",
    "EN_VALIDACION",
    "APROBADO",
    "RECHAZADO",
}


class KnowledgeContractError(ValueError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_status(value: Any) -> str:
    text = str(value or "PROPUESTO").strip().upper().replace(" ", "_")
    aliases = {
        "EN_VALIDACIÓN": "EN_VALIDACION",
        "PENDING": "PROPUESTO",
        "APPROVED": "APROBADO",
        "REJECTED": "RECHAZADO",
    }
    text = aliases.get(text, text)
    if text not in ALLOWED_STATUSES:
        raise KnowledgeContractError(f"Estado de evidencia inválido: {value}")
    return text


def normalize_knowledge_object(
    data: dict[str, Any],
    *,
    source_path: str,
    source_bytes: bytes | None = None,
) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise KnowledgeContractError("El objeto de conocimiento debe ser un diccionario.")

    result = deepcopy(data)

    content = (
        result.get("content")
        or result.get("text")
        or result.get("raw_text")
        or result.get("summary")
        or ""
    )

    title = (
        result.get("title")
        or result.get("name")
        or result.get("document_title")
        or Path(source_path).stem
    )

    knowledge_id = (
        result.get("knowledge_id")
        or result.get("document_id")
        or result.get("id")
    )

    if not knowledge_id:
        seed = f"{source_path}|{title}|{str(content)[:500]}".encode("utf-8")
        knowledge_id = hashlib.sha256(seed).hexdigest()[:16]

    sha256 = hashlib.sha256(
        source_bytes if source_bytes is not None else str(content).encode("utf-8")
    ).hexdigest()

    authors = result.get("authors")
    if authors is None:
        author = result.get("author")
        authors = [str(author)] if author else []
    elif isinstance(authors, str):
        authors = [authors]

    topics = result.get("topics") or result.get("keywords") or []
    if isinstance(topics, str):
        topics = [item.strip() for item in topics.split(",") if item.strip()]

    entities = result.get("entities") or []
    if not isinstance(entities, list):
        entities = []

    provenance = result.get("provenance")
    if not isinstance(provenance, dict):
        provenance = {}
    provenance.setdefault("source_path", source_path)
    provenance.setdefault("sha256", sha256)
    provenance.setdefault("ingestion_method", "normalized")

    normalized = {
        "schema_version": "1.0",
        "knowledge_id": str(knowledge_id),
        "title": str(title).strip(),
        "summary": result.get("summary"),
        "content": content,
        "document_type": result.get("document_type") or result.get("type"),
        "source": str(result.get("source") or source_path),
        "source_url_or_doi": result.get("source_url_or_doi") or result.get("url") or result.get("doi"),
        "authors": [str(item) for item in authors],
        "publication_year": result.get("publication_year") or result.get("year"),
        "language": result.get("language"),
        "topics": [str(item) for item in topics],
        "entities": entities,
        "evidence_level": result.get("evidence_level"),
        "evidence_status": _normalize_status(
            result.get("evidence_status") or result.get("status")
        ),
        "relation_to_ninia": result.get("relation_to_ninia") or result.get("relation"),
        "specialty": result.get("specialty"),
        "provenance": provenance,
        "created_at": str(result.get("created_at") or _now()),
        "updated_at": result.get("updated_at"),
    }

    validate_knowledge_object(normalized)
    return normalized


def validate_knowledge_object(data: dict[str, Any]) -> None:
    required = {
        "schema_version",
        "knowledge_id",
        "title",
        "content",
        "source",
        "evidence_status",
        "provenance",
        "created_at",
    }

    missing = sorted(required - set(data))
    if missing:
        raise KnowledgeContractError(
            "Faltan campos obligatorios: " + ", ".join(missing)
        )

    if data["schema_version"] != "1.0":
        raise KnowledgeContractError("schema_version debe ser 1.0.")

    if not str(data["knowledge_id"]).strip():
        raise KnowledgeContractError("knowledge_id no puede estar vacío.")

    if not str(data["title"]).strip():
        raise KnowledgeContractError("title no puede estar vacío.")

    if data["evidence_status"] not in ALLOWED_STATUSES:
        raise KnowledgeContractError("evidence_status inválido.")

    provenance = data["provenance"]
    if not isinstance(provenance, dict):
        raise KnowledgeContractError("provenance debe ser un objeto.")

    if not provenance.get("source_path"):
        raise KnowledgeContractError("provenance.source_path es obligatorio.")

    digest = str(provenance.get("sha256", ""))
    if len(digest) != 64:
        raise KnowledgeContractError("provenance.sha256 debe tener 64 caracteres.")


def load_and_normalize(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return normalize_knowledge_object(
        data,
        source_path=path.as_posix(),
        source_bytes=path.read_bytes(),
    )
