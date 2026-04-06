"""Tests for spine decision-add command (Phase 2)."""

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


def run_decision_add(
    tmp_path: Path, *extra_args: str
) -> tuple[int, str, str]:
    original = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["decision", "add", *extra_args])
    finally:
        os.chdir(original)
    return result.exit_code, result.output, ""


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_decision_add_appends_to_decisions_jsonl(tmp_path: Path) -> None:
    """spine decision-add appends a record to decisions.jsonl."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_decision_add(
        tmp_path,
        "--title", "Use pydantic for models",
        "--why", "Type safety and validation",
        "--decision", "Adopt pydantic v2",
    )
    assert exit_code == 0, stdout

    decisions_file = tmp_path / ".spine" / "decisions.jsonl"
    assert decisions_file.exists()

    lines = decisions_file.read_text().splitlines()
    assert len(lines) == 1

    record = json.loads(lines[0])
    assert record["title"] == "Use pydantic for models"
    assert record["why"] == "Type safety and validation"
    assert record["decision"] == "Adopt pydantic v2"
    assert "created_at" in record


def test_decision_add_all_fields_required(tmp_path: Path) -> None:
    """title, why, and decision are all required."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    # Missing --why
    exit_code, _, _ = run_decision_add(
        tmp_path,
        "--title", "Test",
        "--decision", "Test decision",
    )
    assert exit_code != 0

    # Missing --decision
    exit_code, _, _ = run_decision_add(
        tmp_path,
        "--title", "Test",
        "--why", "Test why",
    )
    assert exit_code != 0

    # Missing --title
    exit_code, _, _ = run_decision_add(
        tmp_path,
        "--why", "Test why",
        "--decision", "Test decision",
    )
    assert exit_code != 0


def test_decision_record_contains_all_fields(tmp_path: Path) -> None:
    """Decision record contains title, why, decision, alternatives, and created_at."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_decision_add(
        tmp_path,
        "--title", "Test decision",
        "--why", "Test reason",
        "--decision", "Test outcome",
    )

    decisions_file = tmp_path / ".spine" / "decisions.jsonl"
    record = json.loads(decisions_file.read_text().splitlines()[0])

    assert "title" in record
    assert "why" in record
    assert "decision" in record
    assert "alternatives" in record
    assert "created_at" in record


def test_decision_add_with_alternatives(tmp_path: Path) -> None:
    """--alternatives as comma-separated list is parsed into a list."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_decision_add(
        tmp_path,
        "--title", "Choose a language",
        "--why", "Need broad ecosystem",
        "--decision", "Python",
        "--alternatives", "Rust, Go, TypeScript",
    )
    assert exit_code == 0, stdout

    decisions_file = tmp_path / ".spine" / "decisions.jsonl"
    record = json.loads(decisions_file.read_text().splitlines()[0])

    assert record["alternatives"] == ["Rust", "Go", "TypeScript"]


def test_decision_add_empty_title_rejected(tmp_path: Path) -> None:
    """Empty title is rejected with a non-zero exit code."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_decision_add(
        tmp_path,
        "--title", "",
        "--why", "test why",
        "--decision", "test decision",
    )
    assert exit_code != 0


def test_decision_add_empty_why_rejected(tmp_path: Path) -> None:
    """Empty why is rejected with a non-zero exit code."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_decision_add(
        tmp_path,
        "--title", "test title",
        "--why", "",
        "--decision", "test decision",
    )
    assert exit_code != 0


def test_decision_add_empty_decision_rejected(tmp_path: Path) -> None:
    """Empty decision is rejected with a non-zero exit code."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_decision_add(
        tmp_path,
        "--title", "test title",
        "--why", "test why",
        "--decision", "",
    )
    assert exit_code != 0


def test_decision_add_whitespace_only_rejected(tmp_path: Path) -> None:
    """Whitespace-only title/why/decision is rejected."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_decision_add(
        tmp_path,
        "--title", "   ",
        "--why", "test why",
        "--decision", "test decision",
    )
    assert exit_code != 0


def test_decision_add_multiple_records(tmp_path: Path) -> None:
    """Multiple decision-add calls append multiple records."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    for i in range(3):
        exit_code, stdout, _ = run_decision_add(
            tmp_path,
            "--title", f"Decision {i}",
            "--why", f"Reason {i}",
            "--decision", f"Outcome {i}",
        )
        assert exit_code == 0, stdout

    decisions_file = tmp_path / ".spine" / "decisions.jsonl"
    lines = decisions_file.read_text().splitlines()
    assert len(lines) == 3


def test_decision_add_alternatives_with_whitespace(tmp_path: Path) -> None:
    """Alternatives with extra whitespace are trimmed."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_decision_add(
        tmp_path,
        "--title", "Choose a language",
        "--why", "Need ecosystem",
        "--decision", "Python",
        "--alternatives", "Rust , Go , TypeScript ",
    )
    assert exit_code == 0, stdout

    decisions_file = tmp_path / ".spine" / "decisions.jsonl"
    record = json.loads(decisions_file.read_text().splitlines()[0])

    assert record["alternatives"] == ["Rust", "Go", "TypeScript"]
