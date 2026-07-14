from __future__ import annotations

import hashlib
import json
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urljoin, urlparse

import httpx
from html.parser import HTMLParser



class _LinkExtractor(HTMLParser):
    """Minimal dependency-free HTML link extractor."""

    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text_parts: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        if tag.lower() != "a":
            return
        attributes = dict(attrs)
        href = attributes.get("href")
        if href:
            self._href = href
            self._text_parts = []

    def handle_data(self, data: str) -> None:
        if self._href:
            self._text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href:
            title = " ".join(
                part.strip()
                for part in self._text_parts
                if part.strip()
            )
            self.links.append((self._href, title))
            self._href = None
            self._text_parts = []

from engine.evidence_admission import (
    DuplicateEvidenceError,
    EvidenceAdmissionEngine,
)


@dataclass(frozen=True)
class OfficialSource:
    """Governed source used by the acquisition service."""

    source_id: str
    organization: str
    jurisdiction: str
    domains: tuple[str, ...]
    discovery_urls: tuple[str, ...]
    source_type: str = "MULTILATERAL"
    languages: tuple[str, ...] = ("en",)
    topics: tuple[str, ...] = ()
    enabled: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OfficialSource":
        return cls(
            source_id=str(data["source_id"]),
            organization=str(data["organization"]),
            jurisdiction=str(data.get("jurisdiction", "GLOBAL")),
            domains=tuple(data.get("domains") or ()),
            discovery_urls=tuple(data.get("discovery_urls") or ()),
            source_type=str(data.get("source_type", "MULTILATERAL")),
            languages=tuple(data.get("languages") or ("en",)),
            topics=tuple(data.get("topics") or ()),
            enabled=bool(data.get("enabled", True)),
        )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key in ("domains", "discovery_urls", "languages", "topics"):
            data[key] = list(data[key])
        return data


@dataclass(frozen=True)
class DiscoveredDocument:
    source_id: str
    organization: str
    jurisdiction: str
    url: str
    title: str
    document_type: str
    topics: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["topics"] = list(self.topics)
        return data


class GlobalEvidenceAcquisitionService:
    """Discovers official documents and sends them to the existing intake.

    The service does not approve knowledge. Every accepted document remains
    in CUARENTENA and its Knowledge Object remains PROPUESTO.
    """

    ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
    CONTENT_TYPE_EXTENSIONS = {
        "application/pdf": ".pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "text/plain": ".txt",
    }

    def __init__(
        self,
        *,
        base_dir: Path | str,
        catalog_path: Path | str | None = None,
        admission_engine: EvidenceAdmissionEngine | None = None,
        client: httpx.Client | None = None,
        timeout_seconds: float = 35.0,
        request_delay_seconds: float = 0.25,
        max_file_bytes: int = 25 * 1024 * 1024,
    ) -> None:
        self.base_dir = Path(base_dir)
        self.catalog_path = (
            Path(catalog_path)
            if catalog_path
            else self.base_dir / "data" / "source_catalog" / "official_sources.json"
        )
        self.admission_engine = admission_engine or EvidenceAdmissionEngine(
            base_dir=self.base_dir
        )
        self.request_delay_seconds = request_delay_seconds
        self.max_file_bytes = max_file_bytes
        self.client = client or httpx.Client(
            follow_redirects=True,
            timeout=timeout_seconds,
            headers={
                "User-Agent": (
                    "NINIA-ResearchBot/0.2 "
                    "(official evidence acquisition; contact required)"
                )
            },
        )
        self.download_dir = self.base_dir / "data" / "acquisition" / "downloads"
        self.manifest_dir = self.base_dir / "data" / "acquisition" / "manifests"
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def close(self) -> None:
        self.client.close()

    def load_catalog(self) -> list[OfficialSource]:
        if not self.catalog_path.exists():
            raise FileNotFoundError(
                f"No existe el catálogo de fuentes: {self.catalog_path}"
            )
        raw = json.loads(self.catalog_path.read_text(encoding="utf-8"))
        items = raw.get("sources", raw) if isinstance(raw, dict) else raw
        return [
            OfficialSource.from_dict(item)
            for item in items
            if bool(item.get("enabled", True))
        ]

    @staticmethod
    def _authorized(url: str, source: OfficialSource) -> bool:
        host = (urlparse(url).hostname or "").lower()
        return any(
            host == domain.lower() or host.endswith("." + domain.lower())
            for domain in source.domains
        )

    @staticmethod
    def _safe_name(value: str) -> str:
        return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_")[:160]

    @staticmethod
    def _looks_relevant(text: str, topics: tuple[str, ...]) -> bool:
        if not topics:
            return True
        lowered = text.lower()
        return any(topic.lower() in lowered for topic in topics)

    def discover(
        self,
        source: OfficialSource,
        *,
        max_results: int = 25,
        max_pages: int = 8,
    ) -> list[DiscoveredDocument]:
        found: dict[str, DiscoveredDocument] = {}
        pending = list(source.discovery_urls)
        visited: set[str] = set()

        while pending and len(visited) < max_pages and len(found) < max_results:
            url = pending.pop(0)
            if url in visited or not self._authorized(url, source):
                continue
            visited.add(url)

            try:
                response = self.client.get(url)
                response.raise_for_status()
            except httpx.HTTPError:
                continue

            content_type = (
                response.headers.get("content-type", "")
                .split(";")[0]
                .strip()
                .lower()
            )

            if self._document_extension(url, content_type):
                title = Path(urlparse(url).path).name or source.organization
                found[url] = DiscoveredDocument(
                    source_id=source.source_id,
                    organization=source.organization,
                    jurisdiction=source.jurisdiction,
                    url=url,
                    title=title,
                    document_type=self._document_type(url, content_type),
                    topics=source.topics,
                )
                continue

            if "xml" in content_type or response.text.lstrip().startswith("<?xml"):
                for child in self._xml_locations(response.content):
                    if not self._authorized(child, source):
                        continue
                    child_ext = self._document_extension(child, "")
                    if child_ext:
                        title = Path(urlparse(child).path).name
                        if self._looks_relevant(
                            f"{title} {child}",
                            source.topics,
                        ):
                            found[child] = DiscoveredDocument(
                                source_id=source.source_id,
                                organization=source.organization,
                                jurisdiction=source.jurisdiction,
                                url=child,
                                title=title or source.organization,
                                document_type=self._document_type(child, ""),
                                topics=source.topics,
                            )
                    elif child not in visited and len(pending) < max_pages * 4:
                        pending.append(child)
                    if len(found) >= max_results:
                        break
                continue

            if "html" in content_type or "<html" in response.text[:500].lower():
                parser = _LinkExtractor()
                parser.feed(response.text)
                for href, label in parser.links:
                    child = urljoin(url, href)
                    if not self._authorized(child, source):
                        continue
                    if not self._looks_relevant(
                        f"{label} {child}",
                        source.topics,
                    ):
                        continue
                    ext = self._document_extension(child, "")
                    if not ext:
                        continue
                    title = label or Path(urlparse(child).path).name
                    found[child] = DiscoveredDocument(
                        source_id=source.source_id,
                        organization=source.organization,
                        jurisdiction=source.jurisdiction,
                        url=child,
                        title=title or source.organization,
                        document_type=self._document_type(child, ""),
                        topics=source.topics,
                    )
                    if len(found) >= max_results:
                        break

        return list(found.values())[:max_results]

    @staticmethod
    def _xml_locations(content: bytes) -> list[str]:
        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            return []
        return [
            (element.text or "").strip()
            for element in root.iter()
            if element.tag.lower().endswith("loc") and element.text
        ]

    def _document_extension(self, url: str, content_type: str) -> str | None:
        suffix = Path(urlparse(url).path).suffix.lower()
        if suffix in self.ALLOWED_EXTENSIONS:
            return suffix
        return self.CONTENT_TYPE_EXTENSIONS.get(content_type)

    def _document_type(self, url: str, content_type: str) -> str:
        extension = self._document_extension(url, content_type) or ""
        return {
            ".pdf": "INFORME_INSTITUCIONAL",
            ".docx": "DOCUMENTO_INSTITUCIONAL",
            ".txt": "DOCUMENTO_TEXTO",
        }.get(extension, "DOCUMENTO_INSTITUCIONAL")

    def download(
        self,
        source: OfficialSource,
        document: DiscoveredDocument,
    ) -> dict[str, Any]:
        if not self._authorized(document.url, source):
            raise PermissionError("El documento no pertenece a un dominio autorizado.")

        time.sleep(self.request_delay_seconds)
        with self.client.stream("GET", document.url) as response:
            response.raise_for_status()
            content_type = (
                response.headers.get("content-type", "")
                .split(";")[0]
                .strip()
                .lower()
            )
            extension = self._document_extension(document.url, content_type)
            if not extension:
                raise ValueError("Formato documental no permitido.")

            declared = int(response.headers.get("content-length") or 0)
            if declared and declared > self.max_file_bytes:
                raise ValueError("El documento supera el límite permitido.")

            digest = hashlib.sha256()
            total = 0
            temporary = self.download_dir / (
                self._safe_name(document.title or document.source_id) + ".part"
            )

            with temporary.open("wb") as handle:
                for chunk in response.iter_bytes():
                    total += len(chunk)
                    if total > self.max_file_bytes:
                        handle.close()
                        temporary.unlink(missing_ok=True)
                        raise ValueError("El documento supera el límite permitido.")
                    digest.update(chunk)
                    handle.write(chunk)

        sha256 = digest.hexdigest()
        final = self.download_dir / f"{sha256[:16]}{extension}"
        duplicate_download = final.exists()
        if duplicate_download:
            temporary.unlink(missing_ok=True)
        else:
            temporary.replace(final)

        return {
            "path": str(final),
            "sha256": sha256,
            "bytes": total,
            "duplicate_download": duplicate_download,
            "content_type": content_type,
        }

    def acquire(
        self,
        *,
        source_ids: Iterable[str] | None = None,
        max_documents_per_source: int = 5,
        max_total_documents: int = 20,
    ) -> dict[str, Any]:
        selected = set(source_ids or ())
        sources = [
            source
            for source in self.load_catalog()
            if not selected or source.source_id in selected
        ]

        acquired: list[dict[str, Any]] = []
        rejected: list[dict[str, Any]] = []
        discovered_count = 0

        for source in sources:
            if len(acquired) >= max_total_documents:
                break
            documents = self.discover(
                source,
                max_results=max_documents_per_source,
            )
            discovered_count += len(documents)

            for document in documents:
                if len(acquired) >= max_total_documents:
                    break
                try:
                    download = self.download(source, document)
                    year = datetime.now(timezone.utc).year
                    result = self.admission_engine.admit_and_process(
                        uploaded_file_path=download["path"],
                        original_filename=Path(download["path"]).name,
                        title=document.title,
                        year=year,
                        author=source.organization,
                        source=source.organization,
                        document_type=document.document_type,
                        relation_to_ninia=(
                            "Evidencia oficial sobre protección de niñas, "
                            "niños y adolescentes en entornos digitales."
                        ),
                        specialty="investigacion_general",
                        researcher_name="NINIA Global Evidence Acquisition",
                        researcher_email="acquisition@ninia.system",
                        institution="NINIA",
                        country=source.jurisdiction,
                        source_url_or_doi=document.url,
                        declaration_accepted=True,
                    )
                    acquired.append(
                        {
                            "source": source.to_dict(),
                            "document": document.to_dict(),
                            "download": download,
                            "request_id": result["admission_record"]["id"],
                            "request_status": result["admission_record"]["status"],
                            "knowledge_id": result["processing_result"][
                                "normalized_knowledge_object"
                            ]["knowledge_id"],
                            "knowledge_status": result["processing_result"][
                                "normalized_knowledge_object"
                            ]["evidence_status"],
                        }
                    )
                except DuplicateEvidenceError as exc:
                    rejected.append(
                        {
                            "source_id": source.source_id,
                            "url": document.url,
                            "reason": "DUPLICATE",
                            "detail": str(exc),
                        }
                    )
                except Exception as exc:
                    rejected.append(
                        {
                            "source_id": source.source_id,
                            "url": document.url,
                            "reason": type(exc).__name__,
                            "detail": str(exc),
                        }
                    )

        manifest = {
            "generated_at": self._now(),
            "sources_checked": len(sources),
            "documents_discovered": discovered_count,
            "documents_acquired": len(acquired),
            "documents_rejected": len(rejected),
            "acquired": acquired,
            "rejected": rejected,
            "governance": {
                "official_domains_only": True,
                "request_status": "CUARENTENA",
                "knowledge_status": "PROPUESTO",
                "automatic_approval": False,
            },
        }
        manifest_path = self.manifest_dir / (
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            + "_global_evidence_acquisition.json"
        )
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        manifest["manifest_path"] = str(manifest_path)
        return manifest
