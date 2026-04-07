"""Safe file I/O helpers for SPINE init."""

from __future__ import annotations

import json
from pathlib import Path


def write_file_safe(path: Path, content: str, *, force: bool = False) -> bool:
    """
    Write `content` to `path` only if the file does not already exist,
    unless `force=True`.

    Returns True if the file was written, False if it was skipped.
    """
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def ensure_dir(path: Path) -> None:
    """Create directory (and parents) if it does not exist."""
    path.mkdir(parents=True, exist_ok=True)


def touch_file(path: Path, *, force: bool = False) -> bool:
    """
    Create an empty file at `path` if it does not exist.
    Returns True if created, False if skipped.
    """
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
    return True


def update_artifact_manifest(
    manifest_path: Path,
    section: str,
    key: str | None,
    entry: dict,
) -> None:
    """
    Update a section of the artifact manifest at `manifest_path`.

    The manifest is a JSON file at .spine/artifact_manifest.json.
    It is always overwritten with the latest state (not append-only).

    Args:
        manifest_path: absolute path to artifact_manifest.json
        section: top-level key ("briefs" or "reviews")
        key: sub-key within the section (e.g. "claude"), or None if the section
             is flat (e.g. reviews uses a single entry)
        entry: dict of fields to merge into the section[key] slot
    """
    manifest: dict = {}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            manifest = {}

    manifest["contract_version"] = "1"

    if section not in manifest:
        manifest[section] = {}

    if key is not None:
        if key not in manifest[section]:
            manifest[section][key] = {}
        manifest[section][key].update(entry)
    else:
        manifest[section].update(entry)

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=True), encoding="utf-8")
