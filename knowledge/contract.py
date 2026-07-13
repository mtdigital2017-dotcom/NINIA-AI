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

    evidence_fragments = result.get("evidence_fragments") or []
    if not isinstance(evidence_fragments, list):
        evidence_fragments = []

    typed_relations = result.get("typed_relations") or []
    if not isinstance(typed_relations, list):
        typed_relations = []

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
        "evidence_fragments": evidence_fragments,
        "typed_relations": typed_relations,
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

    _validate_evidence_layer(data)


def _validate_evidence_layer(data: dict[str, Any]) -> None:
    fragments = data.get("evidence_fragments", [])
    relations = data.get("typed_relations", [])

    if not isinstance(fragments, list):
        raise KnowledgeContractError("evidence_fragments debe ser una lista.")

    fragment_ids: set[str] = set()
    for item in fragments:
        if not isinstance(item, dict):
            raise KnowledgeContractError(
                "Cada evidence_fragment debe ser un objeto."
            )
        required = {
            "fragment_id",
            "text",
            "evidence_type",
            "source_locator",
            "confidence",
            "validation_status",
        }
        missing = required - set(item)
        if missing:
            raise KnowledgeContractError(
                "Evidence fragment incompleto: " + ", ".join(sorted(missing))
            )
        fragment_id = str(item["fragment_id"]).strip()
        if not fragment_id or fragment_id in fragment_ids:
            raise KnowledgeContractError(
                "fragment_id vacío o duplicado."
            )
        fragment_ids.add(fragment_id)
        if not str(item["text"]).strip():
            raise KnowledgeContractError(
                "El texto del fragmento no puede estar vacío."
            )
        confidence = float(item["confidence"])
        if not 0.0 <= confidence <= 1.0:
            raise KnowledgeContractError(
                "La confianza del fragmento debe estar entre 0 y 1."
            )
        if item["validation_status"] not in ALLOWED_STATUSES:
            raise KnowledgeContractError(
                "validation_status inválido en evidence_fragment."
            )
        if not isinstance(item["source_locator"], dict):
            raise KnowledgeContractError(
                "source_locator debe ser un objeto."
            )

    if not isinstance(relations, list):
        raise KnowledgeContractError("typed_relations debe ser una lista.")

    relation_ids: set[str] = set()
    for item in relations:
        if not isinstance(item, dict):
            raise KnowledgeContractError(
                "Cada typed_relation debe ser un objeto."
            )
        required = {
            "relation_id",
            "relation_type",
            "target",
            "source_fragment_ids",
            "confidence",
            "validation_status",
        }
        missing = required - set(item)
        if missing:
            raise KnowledgeContractError(
                "Typed relation incompleta: " + ", ".join(sorted(missing))
            )
        relation_id = str(item["relation_id"]).strip()
        if not relation_id or relation_id in relation_ids:
            raise KnowledgeContractError(
                "relation_id vacío o duplicado."
            )
        relation_ids.add(relation_id)
        if not isinstance(item["target"], dict):
            raise KnowledgeContractError("target debe ser un objeto.")
        unknown = set(item["source_fragment_ids"]) - fragment_ids
        if unknown:
            raise KnowledgeContractError(
                "La relación referencia fragmentos inexistentes: "
                + ", ".join(sorted(unknown))
            )
        confidence = float(item["confidence"])
        if not 0.0 <= confidence <= 1.0:
            raise KnowledgeContractError(
                "La confianza de la relación debe estar entre 0 y 1."
            )
        if item["validation_status"] not in ALLOWED_STATUSES:
            raise KnowledgeContractError(
                "validation_status inválido en typed_relation."
            )


def load_and_normalize(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return normalize_knowledge_object(
        data,
        source_path=path.as_posix(),
        source_bytes=path.read_bytes(),
    )
