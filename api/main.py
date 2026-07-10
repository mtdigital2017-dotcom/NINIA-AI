from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil

from engine.ninia_engine import NiniaEngine

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "data" / "uploads"

app = FastAPI(
    title="NINIA-AI API",
    description="Motor inteligente de NINIA v1.0",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = NiniaEngine(base_dir=BASE_DIR)


@app.get("/")
def root():
    return {
        "status": "ok",
        "project": "NINIA-AI",
        "version": "1.0",
        "message": "NINIA-AI API activa",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/knowledge")
def list_knowledge(status: str = "proposed"):
    try:
        items = engine.list_knowledge(status=status)
        return {"status": status, "total": len(items), "items": items}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/documents/process")
async def process_document(
    file: UploadFile = File(...),
    title: str = Form(default=""),
    source_entity: str = Form(default=""),
    source_url_or_doi: str = Form(default=""),
):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".pdf", ".docx", ".txt"}:
        raise HTTPException(status_code=400, detail="Formato no soportado. Usa PDF, DOCX o TXT.")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = (file.filename or "documento").replace("/", "_").replace("\\", "_")
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
        metadata = {k: v for k, v in metadata.items() if v is not None}

        return engine.process_document(target, metadata)

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
