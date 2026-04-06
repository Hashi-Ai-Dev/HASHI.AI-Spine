"""JSONL file utilities — creation, append, and streaming read."""

from __future__ import annotations

import json
from pathlib import Path


def ensure_jsonl(path: Path, *, force: bool = False) -> bool:
    """
    Create an empty JSONL file at `path` if it does not exist.
    Returns True if created, False if skipped.
    """
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")
    return True


def append_jsonl(path: Path, record: dict) -> None:
    """
    Append a JSON record to a JSONL file.
    Creates the file (and directory) if it does not exist.
    Each line is a separate JSON object followed by a newline.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def read_jsonl(path: Path) -> list[dict]:
    """
    Read all records from a JSONL file.
    Returns an empty list if the file does not exist.
    """
    if not path.exists():
        return []
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def parse_jsonl_lines(content: str) -> list[dict]:
    """Parse a string as JSONL. Returns list of parsed dicts, skipping blank lines."""
    records = []
    for line in content.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        records.append(json.loads(line))
    return records
