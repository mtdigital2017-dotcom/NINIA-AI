from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
import shutil
import uuid


class EvidenceAdmissionError(Exception):
    """Error controlado del proceso de admisión."""


class EvidenceNotFoundError(EvidenceAdmissionError):
    """Solicitud inexistente."""


class DuplicateEvidenceError(EvidenceAdmissionError):
    """Documento duplicado."""


class InvalidStatusTransitionError(EvidenceAdmissionError):
    """Transición de estado inválida."""


class EvidenceAdmissionEngine:
    """Gestiona cuarentena, trazabilidad y revisión humana."""

    ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
    MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024

    SPECIALTIES = [
        {"id": "proteccion_infantil_digital", "name": "Protección infantil digital"},
        {"id": "derecho_regulacion", "name": "Derecho y regulación"},
        {"id": "psicologia_salud_mental", "name": "Psicología y salud mental"},
        {"id": "educacion_ami", "name": "Educación y AMI"},
        {"id": "datos_ia", "name": "Ciencia de datos e IA"},
        {"id": "politicas_publicas", "name": "Políticas públicas"},
        {"id": "comunicacion_plataformas", "name": "Comunicación y plataformas"},
        {"id": "investigacion_general", "name": "Investigación académica general"},
    ]

    STATUS_TRANSITIONS = {
        "CUARENTENA": {"EN_VALIDACION", "RECHAZADO"},
        "EN_VALIDACION": {
            "APROBADO",
            "RECHAZADO",
            "CORRECCION_SOLICITADA",
        },
        "CORRECCION_SOLICITADA": {"CUARENTENA", "RECHAZADO"},
        "APROBADO": set(),
        "RECHAZADO": set(),
    }

    SOURCE_SCORES = {
        "UNESCO": 100,
        "UNICEF": 100,
        "ONU": 98,
        "ITU": 97,
        "OECD": 96,
        "OCDE": 96,
        "NATURE": 95,
        "IEEE": 94,
        "SPRINGER": 92,
        "UNIVERSIDAD": 88,
        "UNIVERSITY": 88,
        "MINISTERIO": 85,
        "GOBIERNO": 85,
        "ONG": 70,
    }

    def __init__(self, base_dir: Path | str | None = None):
        self.base_dir = (
            Path(base_dir)
            if base_dir
            else Path(__file__).resolve().parent.parent
        )
        self.files_dir = self.base_dir / "data" / "quarantine"
        self.quarantine_dir = self.base_dir / "knowledge" / "quarantine"
        self.approved_dir = self.base_dir / "knowledge" / "approved"
        self.rejected_dir = self.base_dir / "knowledge" / "rejected"

        for directory in [
            self.files_dir,
            self.quarantine_dir,
            self.approved_dir,
            self.rejected_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _safe_filename(filename: str) -> str:
        return re.sub(
            r"[^A-Za-z0-9._-]+",
            "_",
            Path(filename).name,
        )

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()

        with path.open("rb") as handle:
            for chunk in iter(
                lambda: handle.read(1024 * 1024),
                b"",
            ):
                digest.update(chunk)

        return digest.hexdigest()

    def _all_records(self):
        for directory in [
            self.quarantine_dir,
            self.approved_dir,
            self.rejected_dir,
        ]:
            for path in directory.glob("*.json"):
                try:
                    yield path, json.loads(
                        path.read_text(encoding="utf-8")
                    )
                except Exception:
                    continue

    def _load(self, request_id: str):
        for path, record in self._all_records():
            if record.get("id") == request_id:
                return path, record

        raise EvidenceNotFoundError(
            f"No existe la solicitud {request_id}."
        )

    @classmethod
    def calculate_confidence_index(
        cls,
        author: str,
        source: str,
        reference: str,
        document_type: str,
    ) -> int:
        score = 45
        combined = f"{author} {source}".upper()

        for marker, value in cls.SOURCE_SCORES.items():
            if marker in combined:
                score = max(score, value)

        ref = reference.strip().lower()

        if ref.startswith("10.") or "doi.org/" in ref:
            score = min(100, score + 8)
        elif ref.startswith("http"):
            score = min(100, score + 4)

        if document_type.lower() in {
            "artículo científico",
            "tesis",
            "normativa",
            "informe institucional",
        }:
            score = min(100, score + 3)

        return score

    def create_request(
        self,
        *,
        uploaded_file_path: Path | str,
        original_filename: str,
        title: str,
        year: int,
        author: str,
        source: str,
        document_type: str,
        relation_to_ninia: str,
        specialty: str,
        researcher_name: str,
        researcher_email: str,
        institution: str,
        country: str,
        source_url_or_doi: str = "",
        orcid: str = "",
        declaration_accepted: bool = False,
    ) -> dict:
        path = Path(uploaded_file_path)

        if not declaration_accepted:
            raise EvidenceAdmissionError(
                "Debe aceptar la declaración de autenticidad."
            )

        if not path.exists() or path.stat().st_size == 0:
            raise EvidenceAdmissionError(
                "El archivo no existe o está vacío."
            )

        if path.suffix.lower() not in self.ALLOWED_EXTENSIONS:
            raise EvidenceAdmissionError(
                "Formato no permitido. Use PDF, DOCX o TXT."
            )

        if path.stat().st_size > self.MAX_FILE_SIZE_BYTES:
            raise EvidenceAdmissionError(
                "El archivo supera el límite de 25 MB."
            )

        specialty_ids = {
            item["id"]
            for item in self.SPECIALTIES
        }

        if specialty not in specialty_ids:
            raise EvidenceAdmissionError(
                "La especialidad seleccionada no es válida."
            )

        current_year = datetime.now(timezone.utc).year

        if year < 1900 or year > current_year + 1:
            raise EvidenceAdmissionError(
                "El año del documento no es válido."
            )

        required = [
            title,
            author,
            source,
            document_type,
            relation_to_ninia,
            researcher_name,
            researcher_email,
            institution,
            country,
        ]

        if not all(str(value).strip() for value in required):
            raise EvidenceAdmissionError(
                "Faltan campos obligatorios."
            )

        sha256 = self._sha256(path)

        for _, item in self._all_records():
            if item.get("sha256") == sha256:
                raise DuplicateEvidenceError(
                    f"Documento duplicado: {item['id']}"
                )

        request_id = str(uuid.uuid4())
        stored_path = (
            self.files_dir
            / f"{request_id}_{self._safe_filename(original_filename)}"
        )
        shutil.copy2(path, stored_path)

        now = self._now()

        record = {
            "id": request_id,
            "status": "CUARENTENA",
            "title": title.strip(),
            "year": year,
            "author": author.strip(),
            "source": source.strip(),
            "document_type": document_type.strip(),
            "source_url_or_doi": source_url_or_doi.strip(),
            "relation_to_ninia": relation_to_ninia.strip(),
            "specialty": specialty,
            "researcher": {
                "name": researcher_name.strip(),
                "email": researcher_email.strip().lower(),
                "institution": institution.strip(),
                "country": country.strip(),
                "orcid": orcid.strip(),
            },
            "original_filename": original_filename,
            "stored_file": str(stored_path),
            "file_size": stored_path.stat().st_size,
            "sha256": sha256,
            "confidence_index": self.calculate_confidence_index(
                author,
                source,
                source_url_or_doi,
                document_type,
            ),
            "evidence_level": "NO_CLASIFICADO",
            "reviewer": None,
            "review_notes": "",
            "created_at": now,
            "updated_at": now,
            "history": [
                {
                    "timestamp": now,
                    "from_status": None,
                    "to_status": "CUARENTENA",
                    "actor": researcher_email.strip().lower(),
                    "notes": "Solicitud creada en cuarentena.",
                }
            ],
        }

        target = self.quarantine_dir / f"{request_id}.json"
        target.write_text(
            json.dumps(
                record,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        return record

    def list_requests(
        self,
        status: str | None = None,
        specialty: str | None = None,
    ) -> list[dict]:
        items = []

        for _, item in self._all_records():
            if status and item.get("status") != status:
                continue

            if specialty and item.get("specialty") != specialty:
                continue

            items.append(item)

        return sorted(
            items,
            key=lambda item: item.get("created_at", ""),
            reverse=True,
        )

    def get_request(self, request_id: str) -> dict:
        return self._load(request_id)[1]

    def update_status(
        self,
        *,
        request_id: str,
        new_status: str,
        reviewer_name: str,
        reviewer_email: str,
        review_notes: str,
        evidence_level: str | None = None,
    ) -> dict:
        old_path, record = self._load(request_id)
        current_status = record["status"]

        if new_status not in self.STATUS_TRANSITIONS.get(
            current_status,
            set(),
        ):
            raise InvalidStatusTransitionError(
                f"No se permite {current_status} → {new_status}."
            )

        if not all(
            [
                reviewer_name.strip(),
                reviewer_email.strip(),
                review_notes.strip(),
            ]
        ):
            raise EvidenceAdmissionError(
                "Revisor y observaciones son obligatorios."
            )

        if evidence_level and evidence_level not in {
            "ALTO",
            "MEDIO",
            "BAJO",
            "NO_CLASIFICADO",
        }:
            raise EvidenceAdmissionError(
                "Nivel de evidencia no válido."
            )

        now = self._now()
        record["status"] = new_status
        record["reviewer"] = {
            "name": reviewer_name.strip(),
            "email": reviewer_email.strip().lower(),
        }
        record["review_notes"] = review_notes.strip()
        record["updated_at"] = now

        if evidence_level:
            record["evidence_level"] = evidence_level

        record["history"].append(
            {
                "timestamp": now,
                "from_status": current_status,
                "to_status": new_status,
                "actor": reviewer_email.strip().lower(),
                "notes": review_notes.strip(),
            }
        )

        if new_status == "APROBADO":
            target_dir = self.approved_dir
        elif new_status == "RECHAZADO":
            target_dir = self.rejected_dir
        else:
            target_dir = self.quarantine_dir

        new_path = target_dir / old_path.name
        new_path.write_text(
            json.dumps(
                record,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        if new_path != old_path and old_path.exists():
            old_path.unlink()

        return record
