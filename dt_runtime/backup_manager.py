from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class BackupArtifact:
    backup_path: str
    manifest_path: str
    checksum_path: str
    sha256: str
    created_at: str
    file_count: int


class BackupValidationError(RuntimeError):
    """Señala que un respaldo contiene archivos prohibidos o inconsistentes."""


class BackupManager:
    """Crea, verifica, rota y restaura backups de NINIA.

    La versión 1.1 valida explícitamente que el ZIP no incluya:
    `.git`, `.venv`, cachés, archivos `.pyc`, `.DS_Store`,
    credenciales o secretos conocidos.
    """

    EXCLUDED_NAMES = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".DS_Store",
    }

    EXCLUDED_SUFFIXES = {
        ".pyc",
        ".pyo",
        ".log",
    }

    EXCLUDED_BASENAMES = {
        ".env",
        "credentials.json",
        "token.json",
        "client_secret.json",
    }

    FORBIDDEN_ARCHIVE_PARTS = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
    }

    def __init__(self, repo_root: Path, backup_root: Path):
        self.repo_root = repo_root.resolve()
        self.backup_root = backup_root.resolve()
        self.backup_root.mkdir(parents=True, exist_ok=True)

    def _is_excluded(self, path: Path) -> bool:
        relative = path.relative_to(self.repo_root)

        if any(part in self.EXCLUDED_NAMES for part in relative.parts):
            return True

        if path.name in self.EXCLUDED_BASENAMES:
            return True

        if path.suffix.lower() in self.EXCLUDED_SUFFIXES:
            return True

        return False

    def _iter_files(self):
        for path in sorted(self.repo_root.rglob("*")):
            if not path.is_file():
                continue
            if self._is_excluded(path):
                continue
            yield path

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @classmethod
    def _validate_archive_members(cls, members: list[str]) -> None:
        forbidden: list[str] = []

        for member in members:
            parts = Path(member).parts

            if any(part in cls.FORBIDDEN_ARCHIVE_PARTS for part in parts):
                forbidden.append(member)
                continue

            name = Path(member).name

            if name in cls.EXCLUDED_BASENAMES:
                forbidden.append(member)
                continue

            if Path(member).suffix.lower() in cls.EXCLUDED_SUFFIXES:
                forbidden.append(member)

        if forbidden:
            preview = ", ".join(forbidden[:10])
            raise BackupValidationError(
                f"El respaldo contiene archivos prohibidos: {preview}"
            )

    def create_backup(self, label: str = "manual") -> BackupArtifact:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base_name = f"NINIA-AI_{label}_{timestamp}"

        backup_path = self.backup_root / f"{base_name}.zip"
        manifest_path = self.backup_root / f"{base_name}.manifest.json"
        checksum_path = self.backup_root / f"{base_name}.sha256"

        files = list(self._iter_files())

        with zipfile.ZipFile(
            backup_path,
            "w",
            compression=zipfile.ZIP_DEFLATED,
        ) as archive:
            for path in files:
                archive.write(
                    path,
                    path.relative_to(self.repo_root).as_posix(),
                )

        with zipfile.ZipFile(backup_path) as archive:
            members = archive.namelist()
            self._validate_archive_members(members)

        checksum = self._sha256(backup_path)

        manifest: dict[str, Any] = {
            "schema_version": "1.1",
            "project": "NINIA-AI",
            "label": label,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "backup_file": backup_path.name,
            "sha256": checksum,
            "file_count": len(files),
            "files": [
                path.relative_to(self.repo_root).as_posix()
                for path in files
            ],
            "excluded_policy": {
                "names": sorted(self.EXCLUDED_NAMES),
                "suffixes": sorted(self.EXCLUDED_SUFFIXES),
                "basenames": sorted(self.EXCLUDED_BASENAMES),
            },
        }

        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        checksum_path.write_text(
            f"{checksum}  {backup_path.name}\n",
            encoding="utf-8",
        )

        return BackupArtifact(
            backup_path=str(backup_path),
            manifest_path=str(manifest_path),
            checksum_path=str(checksum_path),
            sha256=checksum,
            created_at=manifest["created_at"],
            file_count=len(files),
        )

    def verify_backup(
        self,
        backup_path: Path,
        manifest_path: Path,
    ) -> dict[str, Any]:
        manifest = json.loads(
            manifest_path.read_text(encoding="utf-8")
        )

        actual = self._sha256(backup_path)
        expected = manifest["sha256"]

        with zipfile.ZipFile(backup_path) as archive:
            bad_file = archive.testzip()
            members = archive.namelist()
            self._validate_archive_members(members)

        manifest_files = set(manifest.get("files", []))
        archive_files = set(members)
        manifest_matches_archive = manifest_files == archive_files

        return {
            "valid": (
                actual == expected
                and bad_file is None
                and manifest_matches_archive
            ),
            "expected_sha256": expected,
            "actual_sha256": actual,
            "zip_integrity_ok": bad_file is None,
            "manifest_matches_archive": manifest_matches_archive,
            "bad_file": bad_file,
        }

    def restore_backup(
        self,
        backup_path: Path,
        destination: Path,
    ) -> Path:
        if destination.exists():
            shutil.rmtree(destination)

        destination.mkdir(parents=True)

        with zipfile.ZipFile(backup_path) as archive:
            members = archive.namelist()
            self._validate_archive_members(members)
            archive.extractall(destination)

        return destination

    def rotate(self, keep: int = 5) -> list[str]:
        if keep < 1:
            raise ValueError("keep debe ser mayor o igual a 1.")

        backups = sorted(
            self.backup_root.glob("NINIA-AI_*.zip"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )

        removed: list[str] = []

        for backup in backups[keep:]:
            stem = backup.with_suffix("")
            manifest = stem.with_suffix(".manifest.json")
            checksum = stem.with_suffix(".sha256")

            for path in (backup, manifest, checksum):
                if path.exists():
                    path.unlink()
                    removed.append(path.name)

        return removed
