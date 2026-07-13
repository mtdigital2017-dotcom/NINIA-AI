from __future__ import annotations

import re


class DOIExtractor:
    """Extrae un DOI candidato sin consultar servicios externos."""

    DOI_PATTERN = re.compile(
        r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b",
        re.IGNORECASE,
    )

    def extract(self, text: str) -> str:
        match = self.DOI_PATTERN.search(text or "")
        return match.group(0).rstrip(".,;:)") if match else ""
