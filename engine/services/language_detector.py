from __future__ import annotations

import re


class LanguageDetector:
    """Detector ligero y determinista para el PMV de NINIA."""

    LANGUAGE_MARKERS = {
        "es": {"el", "la", "los", "las", "para", "niñas", "niños", "protección", "derechos"},
        "en": {"the", "and", "for", "children", "protection", "rights", "digital"},
        "fr": {"le", "la", "les", "pour", "enfants", "protection", "droits"},
        "pt": {"o", "a", "os", "as", "para", "crianças", "proteção", "direitos"},
    }

    def detect(self, text: str) -> str:
        tokens = re.findall(r"[A-Za-zÀ-ÿ]+", (text or "").lower())
        if len(tokens) < 5:
            return "und"

        scores = {
            language: sum(token in markers for token in tokens[:1000])
            for language, markers in self.LANGUAGE_MARKERS.items()
        }
        best_language, best_score = max(scores.items(), key=lambda item: item[1])
        return best_language if best_score > 0 else "und"
