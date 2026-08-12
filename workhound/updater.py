from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import os
import re
import shutil
import tempfile
import zipfile

from .version import __version__


VERSION_RE = re.compile(r'__version__\s*=\s*["\']([^"\']+)["\']')


@dataclass
class UpdateResult:
    release_version: str
    backup_name: str
    staged_path: str
    files_updated: int


def _safe_extract(zf: zipfile.ZipFile, destination: Path) -> None:
    destination = destination.resolve()
    for member in zf.infolist():
        member_path = (destination / member.filename).resolve()
        if destination not in member_path.parents and member_path != destination:
            raise ValueError(f"Unsafe ZIP path: {member.filename}")
    zf.extractall(destination)


def _find_release_root(extract_root: Path) -> Path:
    candidates = []
    for root in [extract_root] + [p for p in extract_root.iterdir() if p.is_dir()]:
        if (root / "run.py").is_file() and (root / "workhound" / "version.py").is_file():
            candidates.append(root)
    if len(candidates) != 1:
        raise ValueError(
            "Release ZIP must contain exactly one WorkHound application root "
            "with run.py and workhound/version.py."
        )
    return candidates[0]


def _read_release_version(release_root: Path) -> str:
    text = (release_root / "workhound" / "version.py").read_text(encoding="utf-8")
    m = VERSION_RE.search(text)
    if not m:
        raise ValueError("Unable to determine release version from workhound/version.py.")
    return m.group(1).strip()


def _version_tuple(version: str):
    # WolfPack numeric releases and numeric hotfix suffixes:
    # 0.1.3, 0.1.3-hf1, etc.
    m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)(?:-hf(\d+))?", version)
    if not m:
        return None
    major, minor, patch, hf = m.groups()
    return (int(major), int(minor), int(patch), int(hf or 0))


def validate_release_zip(zip_path: Path) -> tuple[str, Path, Path]:
    if not zipfile.is_zipfile(zip_path):
        raise ValueError("Uploaded file is not a valid ZIP archive.")

    temp_root = Path(tempfile.mkdtemp(prefix="workhound-update-"))
    with zipfile.ZipFile(zip_path) as zf:
        _safe_extract(zf, temp_root)

    release_root = _find_release_root(temp_root)
    release_version = _read_release_version(release_root)

    current_t = _version_tuple(__version__)
    release_t = _version_tuple(release_version)
    if not release_t:
        shutil.rmtree(temp_root, ignore_errors=True)
        raise ValueError(
            f"Unsupported release version '{release_version}'. "
            "Use numeric WolfPack versioning such as 0.1.3 or 0.1.3-hf1."
        )
    if current_t and release_t <= current_t:
        shutil.rmtree(temp_root, ignore_errors=True)
        raise ValueError(
            f"Release v{release_version} is not newer than installed v{__version__}."
        )

    return release_version, release_root, temp_root


def _copy_tree_overlay(src: Path, dst: Path) -> int:
    updated = 0
    skip_names = {".venv", "instance", "__pycache__"}
    for path in src.rglob("*"):
        rel = path.relative_to(src)
        if any(part in skip_names for part in rel.parts):
            continue
        if path.is_dir():
            (dst / rel).mkdir(parents=True, exist_ok=True)
            continue
        if path.suffix == ".pyc":
            continue
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        updated += 1
    return updated


def _create_backup(app_root: Path, backup_dir: Path, current_version: str) -> str:
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_name = f"workhound-pre-{current_version}-{stamp}.zip"
    backup_path = backup_dir / backup_name

    skip_roots = {".venv", "__pycache__"}
    with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in app_root.rglob("*"):
            rel = path.relative_to(app_root)
            if any(part in skip_roots for part in rel.parts):
                continue
            if path.is_file() and path.suffix != ".pyc":
                zf.write(path, rel)
    return backup_name


def stage_update(zip_path: Path, app_root: Path, instance_path: Path) -> UpdateResult:
    release_version, release_root, temp_root = validate_release_zip(zip_path)
    try:
        backup_dir = instance_path / "update_backups"
        staged_dir = instance_path / "update_staging"
        staged_dir.mkdir(parents=True, exist_ok=True)

        backup_name = _create_backup(app_root, backup_dir, __version__)

        # Keep a copy of exactly what was uploaded for traceability.
        staged_zip = staged_dir / f"workhound-v{release_version}.zip"
        shutil.copy2(zip_path, staged_zip)

        files_updated = _copy_tree_overlay(release_root, app_root)

        marker = instance_path / "UPDATE_STAGED.txt"
        marker.write_text(
            "\n".join([
                "WorkHound update staged",
                f"From: v{__version__}",
                f"To: v{release_version}",
                f"Timestamp: {datetime.now():%Y-%m-%d %H:%M:%S}",
                f"Backup: {backup_name}",
                f"Uploaded release: {staged_zip.name}",
                "Restart required: yes",
            ]) + "\n",
            encoding="utf-8"
        )

        return UpdateResult(
            release_version=release_version,
            backup_name=backup_name,
            staged_path=str(staged_zip),
            files_updated=files_updated,
        )
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def list_update_backups(instance_path: Path, limit: int = 10):
    backup_dir = instance_path / "update_backups"
    if not backup_dir.exists():
        return []
    files = sorted(
        [p for p in backup_dir.glob("workhound-pre-*.zip") if p.is_file()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return [
        {
            "name": p.name,
            "size": p.stat().st_size,
            "mtime": datetime.fromtimestamp(p.stat().st_mtime),
        }
        for p in files[:limit]
    ]
