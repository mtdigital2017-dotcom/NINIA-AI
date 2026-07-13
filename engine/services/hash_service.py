from __future__ import annotations

import hashlib
from pathlib import Path


class HashService:
    """Genera huellas reproducibles para trazabilidad y duplicados."""

    def sha256_file(self, path: Path | str) -> str:
        source = Path(path)
        digest = hashlib.sha256()
        with source.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
