from __future__ import annotations

from pathlib import Path
from typing import Optional
import shutil
import tempfile

from fastapi import (
    FastAPI,
    HTTPException,
    UploadFile,
    File,
    Form,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from engine.ninia_engine import NiniaEngine
from dt_runtime.bootstrap import RuntimeBootstrap
from dt_runtime.executive_controller import ExecutiveController
from engine.services.scientific_validation import (
    ScientificValidationError,
    ScientificValidationService,
)
from engine.services.operational_knowledge_factory import (
    OperationalKnowledgeFactory,
)
from engine.evidence_admission import (
    DuplicateEvidenceError,
    EvidenceAdmissionEngine,
    EvidenceAdmissionError,
    EvidenceNotFoundError,
)


BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
runtime_bootstrap = RuntimeBootstrap(BASE_DIR)
executive_controller = ExecutiveController(BASE_DIR)

app = FastAPI(
    title="NINIA-AI API",
    description="Motor inteligente de NINIA v1.0",
    version="1.0.3",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = NiniaEngine(base_dir=BASE_DIR)
admission_engine = EvidenceAdmissionEngine(
    base_dir=BASE_DIR
)
scientific_validation_service = ScientificValidationService(
    base_dir=BASE_DIR,
    admission_engine=admission_engine,
)
operational_knowledge_factory = OperationalKnowledgeFactory(
    base_dir=BASE_DIR,
)



@app.on_event("startup")
def startup_runtime():
    """Carga memoria, manifiesto y QA antes de aceptar solicitudes."""
    app.state.runtime_status = runtime_bootstrap.run()


@app.middleware("http")
async def enforce_runtime_bootstrap(request, call_next):
    """Impide procesar solicitudes si el Runtime no está listo."""
    if request.url.path in {
        "/docs",
        "/openapi.json",
        "/redoc",
    }:
        return await call_next(request)

    try:
        app.state.runtime_status = runtime_bootstrap.run()
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={
                "status": "blocked",
                "reason": "DT Runtime no disponible",
                "detail": str(exc),
            },
        )

    return await call_next(request)



class DTRequest(BaseModel):
    request: str


class StatusUpdate(BaseModel):
    status: str
    reviewer_name: str
    reviewer_email: str
    review_notes: str
    evidence_level: Optional[str] = None


class OperationalRunRequest(BaseModel):
    source_ids: list[str] = []
    max_documents_per_source: int = 3
    max_total_documents: int = 10
    train_if_ready: bool = True



@app.get("/dt/health")
def dt_health():
    return {
        "runtime": runtime_bootstrap.run(),
        "executive": executive_controller.health(),
    }


@app.post("/dt/plan")
def dt_plan(payload: DTRequest):
    try:
        result = executive_controller.process(payload.request)
        return {
            "request_id": result.request_id,
            "memory_loaded": result.memory_loaded,
            "memory_qa_passed": result.memory_qa_passed,
            "decision_plan": result.decision_plan,
            "execution_plan": result.execution_plan,
            "trace_path": result.trace_path,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.get("/")
def root():
    return {
        "status": "ok",
        "project": "NINIA-AI",
        "version": "1.0.3",
        "message": "NINIA-AI API activa",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "1.0.3",
        "services": {
            "document_processing": "ready",
            "evidence_admission": "ready",
        },
    }


@app.get("/knowledge")
def list_knowledge(status: str = "proposed"):
    try:
        items = engine.list_knowledge(status=status)

        return {
            "status": status,
            "total": len(items),
            "items": items,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.post("/documents/process")
async def process_document(
    file: UploadFile = File(...),
    title: str = Form(default=""),
    source_entity: str = Form(default=""),
    source_url_or_doi: str = Form(default=""),
):
    suffix = Path(file.filename or "").suffix.lower()

    if suffix not in {".pdf", ".docx", ".txt"}:
        raise HTTPException(
            status_code=400,
            detail="Formato no soportado. Usa PDF, DOCX o TXT.",
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    safe_name = (
        (file.filename or "documento")
        .replace("/", "_")
        .replace("\\", "_")
    )
    target = UPLOAD_DIR / safe_name

    try:
        with target.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        metadata = {
            "title": title.strip() or None,
            "source_entity": source_entity.strip() or None,
            "source_url_or_doi": source_url_or_doi.strip(),
            "status": "PROPUESTO",
        }
        metadata = {
            key: value
            for key, value in metadata.items()
            if value is not None
        }

        return engine.process_document(
            target,
            metadata,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@app.get("/researcher/specialties")
def researcher_specialties():
    return {
        "total": len(
            admission_engine.SPECIALTIES
        ),
        "items": admission_engine.SPECIALTIES,
    }


@app.post(
    "/evidence/requests",
    status_code=201,
)
async def create_evidence_request(
    file: UploadFile = File(...),
    title: str = Form(...),
    year: int = Form(...),
    author: str = Form(...),
    source: str = Form(...),
    document_type: str = Form(...),
    relation_to_ninia: str = Form(...),
    specialty: str = Form(...),
    researcher_name: str = Form(...),
    researcher_email: str = Form(...),
    institution: str = Form(...),
    country: str = Form(...),
    source_url_or_doi: str = Form(default=""),
    orcid: str = Form(default=""),
    declaration_accepted: bool = Form(...),
):
    temp_path = None

    try:
        suffix = Path(
            file.filename or ""
        ).suffix.lower()

        with tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False,
        ) as temp:
            shutil.copyfileobj(
                file.file,
                temp,
            )
            temp_path = Path(temp.name)

        unified = admission_engine.admit_and_process(
            uploaded_file_path=temp_path,
            original_filename=(
                file.filename or "documento"
            ),
            title=title,
            year=year,
            author=author,
            source=source,
            document_type=document_type,
            relation_to_ninia=relation_to_ninia,
            specialty=specialty,
            researcher_name=researcher_name,
            researcher_email=researcher_email,
            institution=institution,
            country=country,
            source_url_or_doi=source_url_or_doi,
            orcid=orcid,
            declaration_accepted=declaration_accepted,
        )

        admission = unified["admission_record"]
        processing = unified["processing_result"]

        return {
            "ok": True,
            "message": (
                "Solicitud enviada a cuarentena y documento procesado."
            ),
            "request": admission,
            "knowledge": processing["normalized_knowledge_object"],
            "saved_to": processing["saved_to"],
        }

    except DuplicateEvidenceError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    except EvidenceAdmissionError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    finally:
        if (
            temp_path is not None
            and temp_path.exists()
        ):
            temp_path.unlink()


@app.get("/evidence/requests")
def list_evidence_requests(
    status: Optional[str] = None,
    specialty: Optional[str] = None,
    researcher_email: Optional[str] = None,
):
    items = admission_engine.list_requests(
        status=status,
        specialty=specialty,
    )

    if researcher_email:
        normalized_email = researcher_email.strip().lower()
        items = [
            item
            for item in items
            if str(item.get("researcher", {}).get("email", "")).lower()
            == normalized_email
        ]

    return {
        "total": len(items),
        "items": items,
    }


@app.get("/evidence/requests/{request_id}")
def get_evidence_request(
    request_id: str,
):
    try:
        return admission_engine.get_request(
            request_id
        )
    except EvidenceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@app.patch(
    "/evidence/requests/{request_id}/status"
)
def update_evidence_status(
    request_id: str,
    payload: StatusUpdate,
):
    try:
        record = admission_engine.update_status(
            request_id=request_id,
            new_status=payload.status,
            reviewer_name=payload.reviewer_name,
            reviewer_email=payload.reviewer_email,
            review_notes=payload.review_notes,
            evidence_level=payload.evidence_level,
        )

        return {
            "ok": True,
            "message": "Estado actualizado.",
            "request": record,
        }

    except EvidenceAdmissionError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.post("/evidence/requests/{request_id}/scientific-validation")
def run_scientific_validation(request_id: str):
    """Genera una preevaluación científica no vinculante."""
    try:
        return scientific_validation_service.assess_request(request_id)
    except EvidenceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ScientificValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/evidence/requests/{request_id}/scientific-validation")
def get_scientific_validation(request_id: str):
    """Consulta el informe científico asociado a una solicitud."""
    try:
        return scientific_validation_service.get_report(request_id)
    except ScientificValidationError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/scientific-validation/reports")
def list_scientific_validation_reports():
    items = scientific_validation_service.list_reports()
    return {"total": len(items), "items": items}

@app.get("/operations/status")
def operational_status():
    """Estado operativo consumible por frontend."""
    try:
        return operational_knowledge_factory.status()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/operations/run")
def run_operational_pipeline(payload: OperationalRunRequest):
    """Ejecuta el flujo completo usando únicamente servicios existentes."""
    if payload.max_documents_per_source < 1:
        raise HTTPException(
            status_code=400,
            detail="max_documents_per_source debe ser mayor que cero.",
        )
    if payload.max_total_documents < 1:
        raise HTTPException(
            status_code=400,
            detail="max_total_documents debe ser mayor que cero.",
        )
    if payload.max_total_documents > 100:
        raise HTTPException(
            status_code=400,
            detail="El PMV limita cada ejecución a 100 documentos.",
        )

    try:
        return operational_knowledge_factory.run(
            source_ids=payload.source_ids or None,
            max_documents_per_source=payload.max_documents_per_source,
            max_total_documents=payload.max_total_documents,
            train_if_ready=payload.train_if_ready,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

