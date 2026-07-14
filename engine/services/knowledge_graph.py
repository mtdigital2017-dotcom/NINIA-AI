from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class KnowledgeGraphError(ValueError):
    """Raised when the knowledge graph cannot be built or validated."""


class KnowledgeGraphService:
    """Builds a traceable graph from approved NINIA Knowledge Objects.

    The graph is a derived view. It never modifies Knowledge Objects and
    never promotes evidence states. Only objects stored in knowledge/approved
    are included by default.
    """

    GRAPH_VERSION = "1.0"

    def __init__(self, base_dir: Path | str) -> None:
        self.base_dir = Path(base_dir)
        self.knowledge_dir = self.base_dir / "knowledge"
        self.approved_dir = self.knowledge_dir / "approved"
        self.graph_dir = self.knowledge_dir / "graph"
        self.graph_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _stable_id(node_type: str, value: str) -> str:
        normalized = " ".join(str(value).strip().lower().split())
        digest = hashlib.sha256(
            f"{node_type}|{normalized}".encode("utf-8")
        ).hexdigest()[:20]
        return f"{node_type.lower()}:{digest}"

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise KnowledgeGraphError(
                f"No fue posible leer {path}: {exc}"
            ) from exc
        if not isinstance(data, dict):
            raise KnowledgeGraphError(
                f"El Knowledge Object debe ser un objeto JSON: {path}"
            )
        return data

    def _approved_objects(self) -> list[tuple[Path, dict[str, Any]]]:
        if not self.approved_dir.exists():
            return []
        objects: list[tuple[Path, dict[str, Any]]] = []
        for path in sorted(self.approved_dir.glob("*.json")):
            data = self._load_json(path)
            if data.get("evidence_status") != "APROBADO":
                continue
            objects.append((path, data))
        return objects

    def build(self) -> dict[str, Any]:
        nodes: dict[str, dict[str, Any]] = {}
        edges: dict[str, dict[str, Any]] = {}
        sources = self._approved_objects()

        for source_path, knowledge in sources:
            self._add_knowledge_object(
                knowledge=knowledge,
                source_path=source_path,
                nodes=nodes,
                edges=edges,
            )

        graph = {
            "graph_version": self.GRAPH_VERSION,
            "generated_at": self._now(),
            "source_policy": "APPROVED_KNOWLEDGE_ONLY",
            "statistics": {
                "knowledge_objects": len(sources),
                "nodes": len(nodes),
                "edges": len(edges),
            },
            "nodes": sorted(
                nodes.values(),
                key=lambda item: (item["node_type"], item["node_id"]),
            ),
            "edges": sorted(
                edges.values(),
                key=lambda item: (
                    item["relation_type"],
                    item["source_node_id"],
                    item["target_node_id"],
                ),
            ),
        }

        validation = self.validate(graph)
        graph["validation"] = validation
        self.persist(graph)
        return graph

    def _add_knowledge_object(
        self,
        *,
        knowledge: dict[str, Any],
        source_path: Path,
        nodes: dict[str, dict[str, Any]],
        edges: dict[str, dict[str, Any]],
    ) -> None:
        knowledge_id = str(knowledge.get("knowledge_id") or "").strip()
        if not knowledge_id:
            raise KnowledgeGraphError(
                f"Knowledge Object sin knowledge_id: {source_path}"
            )

        document_node_id = f"document:{knowledge_id}"
        self._add_node(
            nodes,
            node_id=document_node_id,
            node_type="DOCUMENT",
            label=str(knowledge.get("title") or knowledge_id),
            properties={
                "knowledge_id": knowledge_id,
                "document_type": knowledge.get("document_type"),
                "publication_year": knowledge.get("publication_year"),
                "language": knowledge.get("language"),
                "evidence_level": knowledge.get("evidence_level"),
                "evidence_status": knowledge.get("evidence_status"),
                "source_url_or_doi": knowledge.get("source_url_or_doi"),
                "source_path": str(source_path),
                "sha256": (
                    (knowledge.get("provenance") or {}).get("sha256")
                ),
            },
        )

        source = str(knowledge.get("source") or "").strip()
        if source:
            target = self._stable_id("ORGANIZATION", source)
            self._add_node(
                nodes,
                node_id=target,
                node_type="ORGANIZATION",
                label=source,
                properties={},
            )
            self._add_edge(
                edges,
                source_node_id=document_node_id,
                target_node_id=target,
                relation_type="ISSUED_BY",
                knowledge_id=knowledge_id,
            )

        for topic in self._string_values(knowledge.get("topics")):
            target = self._stable_id("TOPIC", topic)
            self._add_node(
                nodes,
                node_id=target,
                node_type="TOPIC",
                label=topic,
                properties={},
            )
            self._add_edge(
                edges,
                source_node_id=document_node_id,
                target_node_id=target,
                relation_type="HAS_TOPIC",
                knowledge_id=knowledge_id,
            )

        risks = knowledge.get("digital_risks") or []
        for risk in self._string_values(risks):
            if risk == "NO_CLASIFICADO":
                continue
            target = self._stable_id("DIGITAL_RISK", risk)
            self._add_node(
                nodes,
                node_id=target,
                node_type="DIGITAL_RISK",
                label=risk,
                properties={},
            )
            self._add_edge(
                edges,
                source_node_id=document_node_id,
                target_node_id=target,
                relation_type="IDENTIFIES_RISK",
                knowledge_id=knowledge_id,
            )

        for entity in knowledge.get("entities") or []:
            value, entity_type = self._entity_value(entity)
            if not value:
                continue
            node_type = entity_type or "ENTITY"
            target = self._stable_id(node_type, value)
            self._add_node(
                nodes,
                node_id=target,
                node_type=node_type,
                label=value,
                properties={},
            )
            self._add_edge(
                edges,
                source_node_id=document_node_id,
                target_node_id=target,
                relation_type="MENTIONS_ENTITY",
                knowledge_id=knowledge_id,
            )

        fragment_ids = set()
        for fragment in knowledge.get("evidence_fragments") or []:
            fragment_id = str(fragment.get("fragment_id") or "").strip()
            if not fragment_id:
                continue
            fragment_ids.add(fragment_id)
            node_id = f"fragment:{fragment_id}"
            self._add_node(
                nodes,
                node_id=node_id,
                node_type="EVIDENCE_FRAGMENT",
                label=str(fragment.get("text") or "")[:160],
                properties={
                    "fragment_id": fragment_id,
                    "position": fragment.get("position"),
                    "language": fragment.get("language"),
                    "evidence_type": fragment.get("evidence_type"),
                    "source_locator": fragment.get("source_locator"),
                    "confidence": fragment.get("confidence"),
                    "validation_status": fragment.get("validation_status"),
                    "knowledge_id": knowledge_id,
                },
            )
            self._add_edge(
                edges,
                source_node_id=document_node_id,
                target_node_id=node_id,
                relation_type="SUPPORTED_BY",
                knowledge_id=knowledge_id,
                source_fragment_ids=[fragment_id],
            )

        for relation in knowledge.get("typed_relations") or []:
            relation_type = str(
                relation.get("relation_type") or "RELATED_TO"
            ).strip()
            target_type = str(
                relation.get("target_type") or "ENTITY"
            ).strip().upper()
            target_value = str(
                relation.get("target_value") or ""
            ).strip()
            if not target_value:
                continue
            target = self._stable_id(target_type, target_value)
            self._add_node(
                nodes,
                node_id=target,
                node_type=target_type,
                label=target_value,
                properties={},
            )
            referenced_fragments = [
                item
                for item in relation.get("source_fragment_ids") or []
                if item in fragment_ids
            ]
            self._add_edge(
                edges,
                source_node_id=document_node_id,
                target_node_id=target,
                relation_type=relation_type,
                knowledge_id=knowledge_id,
                source_fragment_ids=referenced_fragments,
                confidence=relation.get("confidence"),
                validation_status=relation.get("validation_status"),
            )

    @staticmethod
    def _string_values(value: Any) -> list[str]:
        if isinstance(value, str):
            value = [value]
        if not isinstance(value, list):
            return []
        return sorted({
            str(item).strip()
            for item in value
            if str(item).strip()
        })

    @staticmethod
    def _entity_value(entity: Any) -> tuple[str, str]:
        if isinstance(entity, str):
            return entity.strip(), "ENTITY"
        if isinstance(entity, dict):
            value = str(
                entity.get("value")
                or entity.get("text")
                or entity.get("name")
                or ""
            ).strip()
            entity_type = str(
                entity.get("type")
                or entity.get("entity_type")
                or "ENTITY"
            ).strip().upper()
            return value, entity_type
        return "", "ENTITY"

    @staticmethod
    def _add_node(
        nodes: dict[str, dict[str, Any]],
        *,
        node_id: str,
        node_type: str,
        label: str,
        properties: dict[str, Any],
    ) -> None:
        existing = nodes.get(node_id)
        candidate = {
            "node_id": node_id,
            "node_type": node_type,
            "label": label,
            "properties": properties,
        }
        if existing is None:
            nodes[node_id] = candidate
            return
        if (
            existing["node_type"] != node_type
            or existing["label"] != label
        ):
            raise KnowledgeGraphError(
                f"Colisión de nodo detectada: {node_id}"
            )

    @staticmethod
    def _add_edge(
        edges: dict[str, dict[str, Any]],
        *,
        source_node_id: str,
        target_node_id: str,
        relation_type: str,
        knowledge_id: str,
        source_fragment_ids: list[str] | None = None,
        confidence: Any = None,
        validation_status: Any = None,
    ) -> None:
        edge_seed = (
            f"{source_node_id}|{relation_type}|{target_node_id}|"
            f"{knowledge_id}|{','.join(source_fragment_ids or [])}"
        )
        edge_id = "edge:" + hashlib.sha256(
            edge_seed.encode("utf-8")
        ).hexdigest()[:20]
        edges.setdefault(
            edge_id,
            {
                "edge_id": edge_id,
                "source_node_id": source_node_id,
                "target_node_id": target_node_id,
                "relation_type": relation_type,
                "knowledge_id": knowledge_id,
                "source_fragment_ids": source_fragment_ids or [],
                "confidence": confidence,
                "validation_status": validation_status,
            },
        )

    def validate(self, graph: dict[str, Any]) -> dict[str, Any]:
        node_ids = [item.get("node_id") for item in graph.get("nodes", [])]
        edge_ids = [item.get("edge_id") for item in graph.get("edges", [])]
        node_set = set(node_ids)

        errors: list[str] = []
        if None in node_set or "" in node_set:
            errors.append("Existen nodos sin identificador.")
        if len(node_ids) != len(node_set):
            errors.append("Existen node_id duplicados.")
        if len(edge_ids) != len(set(edge_ids)):
            errors.append("Existen edge_id duplicados.")

        for edge in graph.get("edges", []):
            if edge.get("source_node_id") not in node_set:
                errors.append(
                    f"Origen inexistente: {edge.get('edge_id')}"
                )
            if edge.get("target_node_id") not in node_set:
                errors.append(
                    f"Destino inexistente: {edge.get('edge_id')}"
                )
            if not edge.get("knowledge_id"):
                errors.append(
                    f"Arista sin trazabilidad: {edge.get('edge_id')}"
                )

        return {
            "valid": not errors,
            "errors": errors,
            "checked_at": self._now(),
        }

    def persist(self, graph: dict[str, Any]) -> dict[str, str]:
        if not graph.get("validation", {}).get("valid"):
            raise KnowledgeGraphError(
                "No se puede persistir un grafo inválido."
            )

        paths = {
            "graph": self.graph_dir / "knowledge_graph.json",
            "nodes": self.graph_dir / "graph_nodes.json",
            "edges": self.graph_dir / "graph_edges.json",
            "index": self.graph_dir / "graph_index.json",
        }

        paths["graph"].write_text(
            json.dumps(graph, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        paths["nodes"].write_text(
            json.dumps(graph["nodes"], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        paths["edges"].write_text(
            json.dumps(graph["edges"], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        paths["index"].write_text(
            json.dumps(
                {
                    "graph_version": graph["graph_version"],
                    "generated_at": graph["generated_at"],
                    "source_policy": graph["source_policy"],
                    "statistics": graph["statistics"],
                    "validation": graph["validation"],
                },
                ensure_ascii=False,
                indent=2,
            ) + "\n",
            encoding="utf-8",
        )

        return {name: str(path) for name, path in paths.items()}
