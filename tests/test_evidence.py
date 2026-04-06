"""Tests for spine evidence-add command (Phase 2)."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from spine.main import app

runner = CliRunner()


def make_git_repo(tmp_path: Path) -> Path:
    """Create a minimal fake git repo (just a .git dir)."""
    (tmp_path / ".git").mkdir()
    return tmp_path


def run_init(tmp_path: Path, *extra_args: str) -> tuple[int, str, str]:
    result = runner.invoke(app, ["init", "--cwd", str(tmp_path), *extra_args])
    return result.exit_code, result.output, ""


def run_evidence_add(
    tmp_path: Path, *extra_args: str
) -> tuple[int, str, str]:
    original = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["evidence", "add", *extra_args])
    finally:
        os.chdir(original)
    return result.exit_code, result.output, ""


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_evidence_add_appends_to_evidence_jsonl(tmp_path: Path) -> None:
    """spine evidence-add appends a record to evidence.jsonl."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_evidence_add(
        tmp_path,
        "--kind", "commit",
        "--description", "test commit evidence",
    )
    assert exit_code == 0, stdout

    evidence_file = tmp_path / ".spine" / "evidence.jsonl"
    assert evidence_file.exists()

    lines = evidence_file.read_text().splitlines()
    assert len(lines) == 1

    record = json.loads(lines[0])
    assert record["kind"] == "commit"
    assert record["description"] == "test commit evidence"
    assert "created_at" in record


def test_evidence_add_all_valid_kinds(tmp_path: Path) -> None:
    """All 10 evidence kinds are accepted."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    valid_kinds = [
        "brief_generated",
        "commit",
        "pr",
        "test_pass",
        "review_done",
        "demo",
        "user_feedback",
        "payment",
        "kill",
        "narrow",
    ]

    evidence_file = tmp_path / ".spine" / "evidence.jsonl"

    for kind in valid_kinds:
        exit_code, stdout, _ = run_evidence_add(
            tmp_path,
            "--kind", kind,
            "--description", f"evidence for {kind}",
        )
        assert exit_code == 0, f"kind={kind} failed: {stdout}"

    lines = evidence_file.read_text().splitlines()
    assert len(lines) == 10


def test_evidence_record_contains_required_fields(tmp_path: Path) -> None:
    """Evidence record contains kind, description, and created_at."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_evidence_add(
        tmp_path,
        "--kind", "commit",
        "--description", "test description",
    )

    evidence_file = tmp_path / ".spine" / "evidence.jsonl"
    record = json.loads(evidence_file.read_text().splitlines()[0])

    assert "kind" in record
    assert "description" in record
    assert "created_at" in record


def test_evidence_add_with_url(tmp_path: Path) -> None:
    """--url is stored in the evidence record."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_evidence_add(
        tmp_path,
        "--kind", "pr",
        "--description", "PR evidence",
        "--url", "https://github.com/example/pull/123",
    )
    assert exit_code == 0, stdout

    evidence_file = tmp_path / ".spine" / "evidence.jsonl"
    record = json.loads(evidence_file.read_text().splitlines()[0])

    assert record["evidence_url"] == "https://github.com/example/pull/123"


def test_evidence_add_empty_description_allowed(tmp_path: Path) -> None:
    """Empty description is allowed."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_evidence_add(
        tmp_path,
        "--kind", "commit",
        "--description", "",
    )
    assert exit_code == 0, stdout

    evidence_file = tmp_path / ".spine" / "evidence.jsonl"
    record = json.loads(evidence_file.read_text().splitlines()[0])

    assert record["description"] == ""


def test_evidence_add_invalid_kind_rejected(tmp_path: Path) -> None:
    """Invalid kind is rejected with a non-zero exit code."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_evidence_add(
        tmp_path,
        "--kind", "not_a_valid_kind",
        "--description", "test",
    )
    assert exit_code != 0


def test_evidence_add_multiple_records(tmp_path: Path) -> None:
    """Multiple evidence-add calls append multiple records."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    for i in range(3):
        exit_code, stdout, _ = run_evidence_add(
            tmp_path,
            "--kind", "commit",
            "--description", f"record {i}",
        )
        assert exit_code == 0, stdout

    evidence_file = tmp_path / ".spine" / "evidence.jsonl"
    lines = evidence_file.read_text().splitlines()
    assert len(lines) == 3


def test_evidence_add_requires_kind(tmp_path: Path) -> None:
    """evidence-add without --kind exits non-zero."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_evidence_add(tmp_path, "--description", "test")
    assert exit_code != 0
