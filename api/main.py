from pathlib import Path
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
from pydantic import BaseModel

from engine.ninia_engine import NiniaEngine
from engine.evidence_admission import (
    DuplicateEvidenceError,
    EvidenceAdmissionEngine,
    EvidenceAdmissionError,
    EvidenceNotFoundError,
)


BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "data" / "uploads"

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


class StatusUpdate(BaseModel):
    status: str
    reviewer_name: str
    reviewer_email: str
    review_notes: str
    evidence_level: str | None = None


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

        record = admission_engine.create_request(
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

        return {
            "ok": True,
            "message": (
                "Solicitud enviada a cuarentena."
            ),
            "request": record,
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
    status: str | None = None,
    specialty: str | None = None,
):
    items = admission_engine.list_requests(
        status=status,
        specialty=specialty,
    )

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
