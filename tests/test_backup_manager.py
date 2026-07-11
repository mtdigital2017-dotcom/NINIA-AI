from pathlib import Path

from dt_runtime.backup_manager import BackupManager

ROOT = Path(__file__).resolve().parents[1]


def test_backup_creates_artifacts(tmp_path):
    manager = BackupManager(ROOT, tmp_path)
    artifact = manager.create_backup("qa")

    assert Path(artifact.backup_path).exists()
    assert Path(artifact.manifest_path).exists()
    assert Path(artifact.checksum_path).exists()
    assert artifact.file_count > 0
    assert len(artifact.sha256) == 64


def test_backup_is_verified(tmp_path):
    manager = BackupManager(ROOT, tmp_path)
    artifact = manager.create_backup("qa")

    result = manager.verify_backup(
        Path(artifact.backup_path),
        Path(artifact.manifest_path),
    )

    assert result["valid"] is True
    assert result["zip_integrity_ok"] is True


def test_backup_can_be_restored(tmp_path):
    manager = BackupManager(ROOT, tmp_path / "backups")
    artifact = manager.create_backup("qa")

    restored = manager.restore_backup(
        Path(artifact.backup_path),
        tmp_path / "restored",
    )

    assert (restored / "requirements.txt").exists()
    assert (restored / "dt_runtime").exists()
    assert (restored / "NINIA_OS").exists()


def test_rotation_keeps_requested_number(tmp_path):
    manager = BackupManager(ROOT, tmp_path)

    for index in range(4):
        manager.create_backup(f"qa{index}")

    manager.rotate(keep=2)

    assert len(list(tmp_path.glob("NINIA-AI_*.zip"))) == 2


def test_backup_excludes_forbidden_paths(tmp_path):
    manager = BackupManager(ROOT, tmp_path)
    artifact = manager.create_backup("qa")

    import zipfile

    with zipfile.ZipFile(artifact.backup_path) as archive:
        members = archive.namelist()

    forbidden_tokens = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
    }

    assert not any(
        token in Path(member).parts
        for member in members
        for token in forbidden_tokens
    )

    assert not any(
        Path(member).suffix.lower() == ".pyc"
        for member in members
    )


def test_manifest_matches_archive(tmp_path):
    manager = BackupManager(ROOT, tmp_path)
    artifact = manager.create_backup("qa")

    result = manager.verify_backup(
        Path(artifact.backup_path),
        Path(artifact.manifest_path),
    )

    assert result["manifest_matches_archive"] is True
