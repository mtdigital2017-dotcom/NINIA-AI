from __future__ import annotations

import inspect
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4


class RegulatoryIngestionError(RuntimeError):
    """Error controlado del flujo de ingestión regulatoria."""


class RegulatoryDocumentNotFoundError(
    RegulatoryIngestionError
):
    """El documento solicitado no existe."""


class RegulatoryIngestionStageError(
    RegulatoryIngestionError
):
    """Una etapa especializada del pipeline falló."""

    def __init__(
        self,
        stage: str,
        message: str,
    ) -> None:
        self.stage = stage
        super().__init__(
            f"Falló la etapa '{stage}': {message}"
        )


@dataclass(frozen=True)
class RegulatoryIngestionResult:
    """
    Resultado trazable de una ingestión regulatoria.

    El orquestador conserva referencias a las salidas de los
    servicios especializados, pero no reemplaza su lógica.
    """

    ingestion_id: str
    generated_at: str
    status: str
    source_path: str
    source_hash: str
    mission_id: str | None
    metadata: dict[str, Any]
    knowledge_contract: Any
    knowledge_graph: Any
    evidence: Any
    observatory: Any
    trace: list[dict[str, Any]] = field(
        default_factory=list
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RegulatoryIngestionService:
    """
    Orquesta la ingestión de documentos regulatorios reales.

    Responsabilidades:

    - Coordinar servicios existentes.
    - Mantener una traza de ejecución.
    - Validar precondiciones.
    - Propagar resultados entre etapas.
    - No duplicar hashing, metadatos, adaptación,
      grafo, evidencia ni observatorio.

    Las dependencias se reciben por inyección para respetar
    la arquitectura existente y facilitar pruebas.
    """

    def __init__(
        self,
        *,
        hash_service: Any,
        metadata_extractor: Any,
        knowledge_adapter: Any,
        knowledge_graph: Any,
        evidence_layer: Any,
        global_observatory: Any | None = None,
    ) -> None:
        self.hash_service = hash_service
        self.metadata_extractor = metadata_extractor
        self.knowledge_adapter = knowledge_adapter
        self.knowledge_graph = knowledge_graph
        self.evidence_layer = evidence_layer
        self.global_observatory = global_observatory

    def ingest(
        self,
        document_path: str | Path,
        *,
        mission_id: str | None = None,
        source_context: Mapping[str, Any] | None = None,
        persist_graph: bool = True,
    ) -> RegulatoryIngestionResult:
        """
        Ejecuta una ingestión regulatoria completa.

        Parameters
        ----------
        document_path:
            Ruta del documento regulatorio.
        mission_id:
            Misión del Global Observatory asociada.
        source_context:
            Información adicional de procedencia.
        persist_graph:
            Indica si debe invocarse la persistencia del grafo.
        """

        path = Path(document_path).resolve()

        if not path.exists():
            raise RegulatoryDocumentNotFoundError(
                f"No existe el documento: {path}"
            )

        if not path.is_file():
            raise RegulatoryIngestionError(
                f"La ruta no es un archivo: {path}"
            )

        ingestion_id = (
            "REG-"
            + uuid4().hex[:12].upper()
        )

        generated_at = datetime.now(
            timezone.utc
        ).isoformat()

        trace: list[dict[str, Any]] = []

        source_bytes = path.read_bytes()

        document_text = source_bytes.decode(
            "utf-8",
            errors="replace",
        )

        context: dict[str, Any] = {
            "ingestion_id": ingestion_id,
            "generated_at": generated_at,
            "document_path": str(path),
            "source_path": str(path),
            "filename": path.name,
            "mission_id": mission_id,
            "source_context": dict(
                source_context or {}
            ),
            "text": document_text,
            "content": document_text,
            "document_text": document_text,
            "raw_text": document_text,
            "source_bytes": source_bytes,
            "document_bytes": source_bytes,
            "raw_bytes": source_bytes,
        }

        source_hash = self._run_stage(
            stage="hash",
            trace=trace,
            callable_object=self.hash_service.sha256_file,
            available_values={
                **context,
                "path": path,
                "file_path": path,
                "document_path": path,
            },
        )

        if not isinstance(source_hash, str):
            raise RegulatoryIngestionStageError(
                "hash",
                "HashService no devolvió una cadena.",
            )

        context["source_hash"] = source_hash
        context["sha256"] = source_hash
        context["hash"] = source_hash

        metadata = self._run_stage(
            stage="metadata",
            trace=trace,
            callable_object=self.metadata_extractor.extract,
            available_values={
                **context,
                "path": path,
                "file_path": path,
                "document_path": path,
            },
        )

        if metadata is None:
            metadata = {}

        if not isinstance(metadata, Mapping):
            raise RegulatoryIngestionStageError(
                "metadata",
                "MetadataExtractor debe devolver un mapping.",
            )

        metadata_dict = dict(metadata)

        context["metadata"] = metadata_dict
        context["document_metadata"] = metadata_dict

        knowledge_contract = self._run_stage(
            stage="knowledge_adapter",
            trace=trace,
            callable_object=self.knowledge_adapter.build,
            available_values={
                **context,
                "raw_object": {
                    "metadata": metadata_dict,
                    "source_hash": source_hash,
                    "source_path": str(path),
                    "filename": path.name,
                    "text": document_text,
                    "source_context": dict(
                        source_context or {}
                    ),
                },
                "document": context,
                "record": context,
                "payload": context,
                "source": context,
                "input_data": context,
                "data": context,
                "source_path": str(path),
                "source_bytes": source_bytes,
            },
        )

        context["knowledge_contract"] = (
            knowledge_contract
        )
        context["contract"] = knowledge_contract
        context["knowledge"] = knowledge_contract

        knowledge_id = self._extract_knowledge_id(
            knowledge_contract,
            fallback=source_hash,
        )

        context["knowledge_id"] = knowledge_id

        graph_result = self._run_stage(
            stage="knowledge_graph_build",
            trace=trace,
            callable_object=self.knowledge_graph.build,
            available_values={
                **context,
                "document": knowledge_contract,
                "record": knowledge_contract,
                "payload": knowledge_contract,
                "contract": knowledge_contract,
                "knowledge_contract": knowledge_contract,
                "data": knowledge_contract,
            },
        )

        context["knowledge_graph"] = graph_result
        context["graph"] = graph_result

        validate_method = getattr(
            self.knowledge_graph,
            "validate",
            None,
        )

        if callable(validate_method):
            validation_result = self._run_stage(
                stage="knowledge_graph_validate",
                trace=trace,
                callable_object=validate_method,
                available_values={
                    **context,
                    "graph": graph_result,
                    "knowledge_graph": graph_result,
                    "data": graph_result,
                },
            )

            context["graph_validation"] = (
                validation_result
            )

        if persist_graph:
            persist_method = getattr(
                self.knowledge_graph,
                "persist",
                None,
            )

            if callable(persist_method):
                graph_persistence = self._run_stage(
                    stage="knowledge_graph_persist",
                    trace=trace,
                    callable_object=persist_method,
                    available_values={
                        **context,
                        "graph": graph_result,
                        "knowledge_graph": graph_result,
                        "data": graph_result,
                    },
                )

                context["graph_persistence"] = (
                    graph_persistence
                )

        evidence_result = self._run_stage(
            stage="evidence",
            trace=trace,
            callable_object=self.evidence_layer.build,
            available_values={
                **context,
                "text": document_text,
                "knowledge_id": knowledge_id,
                "source_path": str(path),
                "language": metadata_dict.get(
                    "language"
                ),
                "topics": metadata_dict.get(
                    "topics",
                    [],
                ),
                "digital_risks": metadata_dict.get(
                    "digital_risks",
                    [],
                ),
                "relation_to_ninia": metadata_dict.get(
                    "relation_to_ninia"
                ),
                "document": context,
                "record": context,
                "payload": context,
                "graph": graph_result,
                "knowledge_graph": graph_result,
                "metadata": metadata_dict,
                "data": context,
            },
        )

        context["evidence"] = evidence_result

        observatory_result = None

        if self.global_observatory is not None:
            observatory_result = (
                self._update_observatory(
                    mission_id=mission_id,
                    context=context,
                    trace=trace,
                )
            )

        return RegulatoryIngestionResult(
            ingestion_id=ingestion_id,
            generated_at=generated_at,
            status="completed",
            source_path=str(path),
            source_hash=source_hash,
            mission_id=mission_id,
            metadata=metadata_dict,
            knowledge_contract=knowledge_contract,
            knowledge_graph=graph_result,
            evidence=evidence_result,
            observatory=observatory_result,
            trace=trace,
        )

    def ingest_to_json(
        self,
        document_path: str | Path,
        output_path: str | Path,
        *,
        mission_id: str | None = None,
        source_context: Mapping[str, Any] | None = None,
        persist_graph: bool = True,
    ) -> Path:
        """
        Ejecuta la ingestión y guarda el resultado trazable
        como JSON.
        """

        result = self.ingest(
            document_path,
            mission_id=mission_id,
            source_context=source_context,
            persist_graph=persist_graph,
        )

        destination = Path(output_path).resolve()
        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination.write_text(
            json.dumps(
                result.to_dict(),
                indent=2,
                ensure_ascii=False,
                default=str,
            )
            + "\n",
            encoding="utf-8",
        )

        return destination

    @staticmethod
    def _extract_knowledge_id(
        knowledge_contract: Any,
        *,
        fallback: str,
    ) -> str:
        """
        Extrae el identificador de conocimiento del contrato
        sin imponer un esquema nuevo.
        """

        if isinstance(knowledge_contract, Mapping):
            candidate_keys = (
                "knowledge_id",
                "id",
                "contract_id",
                "document_id",
                "source_id",
                "uuid",
            )

            for key in candidate_keys:
                value = knowledge_contract.get(key)

                if value:
                    return str(value)

            nested_candidates = (
                knowledge_contract.get("knowledge"),
                knowledge_contract.get("identity"),
                knowledge_contract.get("metadata"),
            )

            for nested in nested_candidates:
                if not isinstance(nested, Mapping):
                    continue

                for key in candidate_keys:
                    value = nested.get(key)

                    if value:
                        return str(value)

        return str(fallback)

    def _update_observatory(
        self,
        *,
        mission_id: str | None,
        context: dict[str, Any],
        trace: list[dict[str, Any]],
    ) -> Any:
        """
        Actualiza el observatorio solo mediante métodos públicos
        ya existentes.
        """

        if mission_id:
            get_mission = getattr(
                self.global_observatory,
                "get_mission",
                None,
            )

            if callable(get_mission):
                return self._run_stage(
                    stage="global_observatory_get_mission",
                    trace=trace,
                    callable_object=get_mission,
                    available_values={
                        **context,
                        "mission_id": mission_id,
                        "id": mission_id,
                    },
                )

        status_method = getattr(
            self.global_observatory,
            "status",
            None,
        )

        if callable(status_method):
            return self._run_stage(
                stage="global_observatory_status",
                trace=trace,
                callable_object=status_method,
                available_values=context,
            )

        return None

    def _run_stage(
        self,
        *,
        stage: str,
        trace: list[dict[str, Any]],
        callable_object: Any,
        available_values: Mapping[str, Any],
    ) -> Any:
        started_at = datetime.now(
            timezone.utc
        ).isoformat()

        try:
            result = self._invoke_compatible(
                callable_object,
                available_values,
            )
        except RegulatoryIngestionError:
            raise
        except Exception as exc:
            trace.append(
                {
                    "stage": stage,
                    "status": "failed",
                    "started_at": started_at,
                    "finished_at": datetime.now(
                        timezone.utc
                    ).isoformat(),
                    "error": str(exc),
                }
            )

            raise RegulatoryIngestionStageError(
                stage,
                str(exc),
            ) from exc

        trace.append(
            {
                "stage": stage,
                "status": "completed",
                "started_at": started_at,
                "finished_at": datetime.now(
                    timezone.utc
                ).isoformat(),
                "result_type": type(result).__name__,
            }
        )

        return result

    @staticmethod
    def _invoke_compatible(
        callable_object: Any,
        available_values: Mapping[str, Any],
    ) -> Any:
        """
        Invoca un servicio existente respetando su firma.

        Solo entrega parámetros declarados por la función.
        Esto permite integrar contratos existentes sin modificar
        los servicios especializados.
        """

        signature = inspect.signature(
            callable_object
        )

        positional_arguments: list[Any] = []
        keyword_arguments: dict[str, Any] = {}

        missing_required: list[str] = []

        for parameter in signature.parameters.values():
            if parameter.name in {
                "self",
                "cls",
            }:
                continue

            if parameter.kind == (
                inspect.Parameter.VAR_POSITIONAL
            ):
                continue

            if parameter.kind == (
                inspect.Parameter.VAR_KEYWORD
            ):
                continue

            if parameter.name in available_values:
                value = available_values[
                    parameter.name
                ]

                if parameter.kind == (
                    inspect.Parameter.POSITIONAL_ONLY
                ):
                    positional_arguments.append(
                        value
                    )
                else:
                    keyword_arguments[
                        parameter.name
                    ] = value

                continue

            if parameter.default is (
                inspect.Parameter.empty
            ):
                missing_required.append(
                    parameter.name
                )

        if missing_required:
            raise RegulatoryIngestionError(
                "No fue posible satisfacer la firma de "
                f"{callable_object!r}. Parámetros requeridos: "
                + ", ".join(missing_required)
            )

        return callable_object(
            *positional_arguments,
            **keyword_arguments,
        )
