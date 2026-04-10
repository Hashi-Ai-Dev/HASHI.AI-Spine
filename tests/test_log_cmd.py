"""Tests for spine log — short-form evidence add (#74 discipline-tax reduction)."""

from __future__ import annotations

import json
import os
from pathlib import Path

from typer.testing import CliRunner

from spine.main import app

runner = CliRunner()


def make_git_repo(tmp_path: Path) -> Path:
    """Create a minimal fake git repo (just a .git dir)."""
    (tmp_path / ".git").mkdir()
    return tmp_path


def run_init(tmp_path: Path) -> None:
    runner.invoke(app, ["init", "--cwd", str(tmp_path)])


def run_log(tmp_path: Path, *args: str) -> tuple[int, str]:
    original = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["log", *args])
    finally:
        os.chdir(original)
    return result.exit_code, result.output


# ---------------------------------------------------------------------------
# Basic functionality
# ---------------------------------------------------------------------------


def test_log_commit_appends_evidence_record(tmp_path: Path) -> None:
    """spine log commit writes an identical record to evidence.jsonl as evidence add."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout = run_log(tmp_path, "commit", "Implemented X feature")
    assert exit_code == 0, stdout

    evidence_file = tmp_path / ".spine" / "evidence.jsonl"
    assert evidence_file.exists()
    lines = evidence_file.read_text().splitlines()
    assert len(lines) == 1

    record = json.loads(lines[0])
    assert record["kind"] == "commit"
    assert record["description"] == "Implemented X feature"
    assert "created_at" in record


def test_log_all_valid_kinds_accepted(tmp_path: Path) -> None:
    """All 10 evidence kinds are accepted by spine log."""
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

    for kind in valid_kinds:
        exit_code, stdout = run_log(tmp_path, kind, f"evidence for {kind}")
        assert exit_code == 0, f"kind={kind} failed with: {stdout}"

    evidence_file = tmp_path / ".spine" / "evidence.jsonl"
    lines = evidence_file.read_text().splitlines()
    assert len(lines) == 10


def test_log_invalid_kind_rejected(tmp_path: Path) -> None:
    """Invalid kind is rejected before touching canonical state."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout = run_log(tmp_path, "not_a_valid_kind", "test")
    assert exit_code != 0

    # Evidence file should remain empty — no partial write
    evidence_file = tmp_path / ".spine" / "evidence.jsonl"
    if evidence_file.exists():
        assert evidence_file.read_text().strip() == ""


def test_log_without_description_allowed(tmp_path: Path) -> None:
    """Description is optional — kind alone is sufficient."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout = run_log(tmp_path, "commit")
    assert exit_code == 0, stdout

    evidence_file = tmp_path / ".spine" / "evidence.jsonl"
    record = json.loads(evidence_file.read_text().splitlines()[0])
    assert record["kind"] == "commit"
    assert record["description"] == ""


def test_log_with_url_option(tmp_path: Path) -> None:
    """--url stores the URL in the evidence record."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout = run_log(
        tmp_path, "pr", "opened PR", "--url", "https://github.com/example/pull/1"
    )
    assert exit_code == 0, stdout

    evidence_file = tmp_path / ".spine" / "evidence.jsonl"
    record = json.loads(evidence_file.read_text().splitlines()[0])
    assert record["evidence_url"] == "https://github.com/example/pull/1"


# ---------------------------------------------------------------------------
# Canonical record quality — identical to evidence add
# ---------------------------------------------------------------------------


def test_log_record_has_required_fields(tmp_path: Path) -> None:
    """Record produced by spine log has all required canonical fields."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_log(tmp_path, "test_pass", "All green")

    evidence_file = tmp_path / ".spine" / "evidence.jsonl"
    record = json.loads(evidence_file.read_text().splitlines()[0])

    assert "kind" in record
    assert "description" in record
    assert "created_at" in record
    assert "evidence_url" in record


def test_log_multiple_calls_append_multiple_records(tmp_path: Path) -> None:
    """Multiple spine log calls each append a separate record."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_log(tmp_path, "commit", "first change")
    run_log(tmp_path, "test_pass", "tests green")
    run_log(tmp_path, "pr", "opened PR")

    evidence_file = tmp_path / ".spine" / "evidence.jsonl"
    lines = evidence_file.read_text().splitlines()
    assert len(lines) == 3

    kinds = [json.loads(line)["kind"] for line in lines]
    assert kinds == ["commit", "test_pass", "pr"]


# ---------------------------------------------------------------------------
# JSON output mode
# ---------------------------------------------------------------------------


def test_log_json_output_structure(tmp_path: Path) -> None:
    """--json produces a machine-readable response with ok and record fields."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout = run_log(tmp_path, "commit", "Implemented feature", "--json")
    assert exit_code == 0, stdout

    data = json.loads(stdout)
    assert data["ok"] is True
    assert data["kind"] == "commit"
    assert data["description"] == "Implemented feature"
    assert "created_at" in data


def test_log_json_output_on_context_failure() -> None:
    """--json produces structured error output on context failure."""
    result = runner.invoke(
        app, ["log", "commit", "test", "--cwd", "/tmp/no-git-repo-here-xyz", "--json"]
    )
    assert result.exit_code != 0
    data = json.loads(result.output)
    assert "error" in data
    assert "exit_code" in data


# ---------------------------------------------------------------------------
# Backward compatibility — evidence add still works
# ---------------------------------------------------------------------------


def test_evidence_add_still_works_alongside_log(tmp_path: Path) -> None:
    """spine evidence add is unaffected — both commands write to the same file."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    # Use the long form first
    original = os.getcwd()
    try:
        os.chdir(tmp_path)
        runner.invoke(app, ["evidence", "add", "--kind", "commit", "--description", "via evidence add"])
    finally:
        os.chdir(original)

    # Then the short form
    run_log(tmp_path, "commit", "via log")

    evidence_file = tmp_path / ".spine" / "evidence.jsonl"
    lines = evidence_file.read_text().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["description"] == "via evidence add"
    assert json.loads(lines[1])["description"] == "via log"


# ---------------------------------------------------------------------------
# No hidden auto-mutation behavior
# ---------------------------------------------------------------------------


def test_log_does_not_mutate_before_explicit_call(tmp_path: Path) -> None:
    """Evidence file is empty until spine log is explicitly called."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    evidence_file = tmp_path / ".spine" / "evidence.jsonl"
    # After init, evidence file should be empty
    assert not evidence_file.exists() or evidence_file.read_text().strip() == ""

    # Only after explicit log call does a record appear
    run_log(tmp_path, "commit", "explicit call")
    assert evidence_file.exists()
    lines = evidence_file.read_text().splitlines()
    assert len(lines) == 1
