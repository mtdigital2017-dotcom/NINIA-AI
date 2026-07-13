from __future__ import annotations

import re
from pathlib import Path

from engine.services.doi_extractor import DOIExtractor
from engine.services.language_detector import LanguageDetector


class MetadataExtractor:
    """Extrae metadatos básicos verificables y conserva incertidumbre."""

    YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")

    def __init__(self) -> None:
        self.language_detector = LanguageDetector()
        self.doi_extractor = DOIExtractor()

    def extract(self, file_path: Path | str, text: str) -> dict:
        path = Path(file_path)
        clean_lines = [
            line.strip()
            for line in (text or "").splitlines()
            if line.strip()
        ]
        first_lines = clean_lines[:12]
        combined = " ".join(first_lines)

        year_match = self.YEAR_PATTERN.search(
            f"{path.name} {combined}"
        )

        return {
            "language": self.language_detector.detect(text),
            "doi": self.doi_extractor.extract(text[:10000]),
            "publication_year": (
                int(year_match.group(0)) if year_match else None
            ),
            "authors": self._extract_authors(first_lines),
        }

    def _extract_authors(self, lines: list[str]) -> list[str]:
        for line in lines[1:8]:
            lowered = line.lower()
            if lowered.startswith(("author:", "authors:", "autor:", "autores:")):
                _, value = line.split(":", 1)
                return [
                    item.strip()
                    for item in re.split(r"[;,]", value)
                    if item.strip()
                ]
        return []
