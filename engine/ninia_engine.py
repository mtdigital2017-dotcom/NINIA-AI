from __future__ import annotations

from pathlib import Path
from datetime import datetime
import json
import uuid
import re


class NiniaEngine:
    """Motor principal de procesamiento documental de NINIA-AI v1.0."""

    STATUS_FOLDERS = {
        "PROPUESTO": "proposed",
        "EN_VALIDACION": "in_validation",
        "APROBADO": "approved",
        "RECHAZADO": "rejected",
    }

    RISK_KEYWORDS = {
        "desinformación": [
            "desinformación",
            "misinformation",
            "disinformation",
            "fake news",
        ],
        "privacidad infantil": [
            "privacidad",
            "privacy",
            "datos personales",
            "personal data",
        ],
        "publicidad dirigida": [
            "publicidad",
            "advertising",
            "targeted ads",
            "marketing",
        ],
        "plataformas digitales": [
            "plataforma",
            "platform",
            "redes sociales",
            "social media",
        ],
        "ia generativa": [
            "ia generativa",
            "generative ai",
            "deepfake",
            "chatbot",
        ],
        "ciberacoso": [
            "ciberacoso",
            "cyberbullying",
            "bullying",
        ],
    }

    def __init__(self, base_dir: Path | str | None = None):
        self.base_dir = (
            Path(base_dir)
            if base_dir
            else Path(__file__).resolve().parent.parent
        )
        self.knowledge_dir = self.base_dir / "knowledge"
        self.upload_dir = self.base_dir / "data" / "uploads"
        self.ensure_directories()

    def ensure_directories(self) -> None:
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        for folder in self.STATUS_FOLDERS.values():
            (self.knowledge_dir / folder).mkdir(parents=True, exist_ok=True)

    def read_document(self, file_path: Path | str) -> str:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"No existe el archivo: {path}")

        suffix = path.suffix.lower()

        if suffix == ".txt":
            return path.read_text(encoding="utf-8", errors="ignore")

        if suffix == ".pdf":
            import pdfplumber

            text_parts = []
            with pdfplumber.open(str(path)) as pdf:
                for page in pdf.pages:
                    text_parts.append(page.extract_text() or "")
            return "\n".join(text_parts)

        if suffix == ".docx":
            from docx import Document

            doc = Document(str(path))
            return "\n".join(p.text for p in doc.paragraphs)

        raise ValueError("Formato no soportado. Usa PDF, DOCX o TXT.")

    def detect_digital_risks(self, text: str) -> list[str]:
        text_lower = text.lower()
        risks = []

        for risk, keywords in self.RISK_KEYWORDS.items():
            if any(keyword.lower() in text_lower for keyword in keywords):
                risks.append(risk)

        return sorted(set(risks)) if risks else ["NO_CLASIFICADO"]

    def infer_source_entity(self, file_name: str, text: str) -> str:
        candidates = [
            "UNESCO",
            "UNICEF",
            "ITU",
            "OECD",
            "OCDE",
            "ONU",
            "CRC",
            "EU",
            "DSA",
            "AI ACT",
        ]
        combined = f"{file_name} {text[:2000]}".upper()

        for candidate in candidates:
            if candidate in combined:
                return candidate

        return "NO_IDENTIFICADO"

    def infer_year(self, file_name: str, text: str) -> int:
        combined = f"{file_name} {text[:2000]}"
        match = re.search(r"\b(20[0-9]{2})\b", combined)
        return int(match.group(1)) if match else datetime.utcnow().year

    def build_knowledge_object(
        self,
        file_path: Path | str,
        text: str,
        metadata: dict | None = None,
    ) -> dict:
        metadata = metadata or {}
        path = Path(file_path)

        return {
            "id": str(uuid.uuid4()),
            "title": (
                metadata.get("title")
                or path.stem.replace("_", " ").replace("-", " ")
            ),
            "source_entity": (
                metadata.get("source_entity")
                or self.infer_source_entity(path.name, text)
            ),
            "year": (
                metadata.get("year")
                or self.infer_year(path.name, text)
            ),
            "document_type": (
                metadata.get("document_type")
                or path.suffix.lower().replace(".", "").upper()
            ),
            "source_url_or_doi": metadata.get("source_url_or_doi", ""),
            "main_topic": (
                metadata.get("main_topic")
                or "Protección integral de niñas, niños y adolescentes en entornos digitales"
            ),
            "relation_to_ninia": (
                metadata.get("relation_to_ninia")
                or "Documento procesado por NINIA para análisis y construcción de conocimiento."
            ),
            "digital_risks": self.detect_digital_risks(text),
            "target_population": (
                metadata.get("target_population")
                or "Niñas, niños y adolescentes"
            ),
            "evidence_level": (
                metadata.get("evidence_level")
                or "NO_CLASIFICADO"
            ),
            "status": metadata.get("status") or "PROPUESTO",
            "summary": text[:1200].strip(),
            "word_count": len(text.split()),
            "source_file": str(path),
            "created_at": datetime.utcnow().isoformat(),
        }

    def save_knowledge_object(self, knowledge_object: dict) -> Path:
        status = knowledge_object.get("status", "PROPUESTO")
        folder = self.STATUS_FOLDERS.get(status)

        if not folder:
            raise ValueError(f"Estado no válido: {status}")

        target = self.knowledge_dir / folder
        target.mkdir(parents=True, exist_ok=True)
        output = target / f"{knowledge_object['id']}.json"
        output.write_text(
            json.dumps(
                knowledge_object,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return output

    def process_document(
        self,
        file_path: Path | str,
        metadata: dict | None = None,
    ) -> dict:
        text = self.read_document(file_path)

        if not text.strip():
            raise ValueError("El documento no contiene texto extraíble.")

        knowledge_object = self.build_knowledge_object(
            file_path,
            text,
            metadata,
        )
        saved_to = self.save_knowledge_object(knowledge_object)

        return {
            "ok": True,
            "message": "Documento procesado correctamente.",
            "knowledge_object": knowledge_object,
            "saved_to": str(saved_to),
        }

    def list_knowledge(
        self,
        status: str = "proposed",
    ) -> list[dict]:
        allowed = set(self.STATUS_FOLDERS.values())

        if status not in allowed:
            raise ValueError(f"Estado no válido: {status}")

        folder = self.knowledge_dir / status
        folder.mkdir(parents=True, exist_ok=True)
        items = []

        for path in folder.glob("*.json"):
            try:
                items.append(
                    json.loads(
                        path.read_text(encoding="utf-8")
                    )
                )
            except Exception:
                continue

        return items
