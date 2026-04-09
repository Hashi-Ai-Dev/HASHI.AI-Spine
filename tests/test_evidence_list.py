"""Tests for spine evidence list command (Issue #64)."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from spine.main import app

runner = CliRunner()


def make_git_repo(tmp_path: Path) -> Path:
    (tmp_path / ".git").mkdir()
    return tmp_path


def spine_init(tmp_path: Path) -> None:
    result = runner.invoke(app, ["init", "--cwd", str(tmp_path)])
    assert result.exit_code == 0, f"init failed: {result.output}"


def add_evidence(tmp_path: Path, kind: str, description: str, url: str = "") -> None:
    args = ["evidence", "add", "--cwd", str(tmp_path), "--kind", kind, "--description", description]
    if url:
        args += ["--url", url]
    result = runner.invoke(app, args)
    assert result.exit_code == 0, f"evidence add failed: {result.output}"


# ---------------------------------------------------------------------------
# Empty state
# ---------------------------------------------------------------------------


def test_evidence_list_empty_human(tmp_path: Path) -> None:
    """Empty evidence.jsonl produces a friendly message, exit 0."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    result = runner.invoke(app, ["evidence", "list", "--cwd", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "no evidence" in result.output.lower()


def test_evidence_list_empty_json(tmp_path: Path) -> None:
    """Empty evidence.jsonl with --json returns ok=True, count=0, records=[]."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    result = runner.invoke(app, ["evidence", "list", "--cwd", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["count"] == 0
    assert data["records"] == []


# ---------------------------------------------------------------------------
# Populated state — human output
# ---------------------------------------------------------------------------


def test_evidence_list_populated_human(tmp_path: Path) -> None:
    """Populated evidence.jsonl shows all records in human output."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    add_evidence(tmp_path, "commit", "first commit")
    add_evidence(tmp_path, "test_pass", "all tests green")

    result = runner.invoke(app, ["evidence", "list", "--cwd", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "commit" in result.output
    assert "first commit" in result.output
    assert "test_pass" in result.output
    assert "all tests green" in result.output


def test_evidence_list_shows_url_in_human_output(tmp_path: Path) -> None:
    """URL field appears in human output when present."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    add_evidence(tmp_path, "pr", "pull request", url="https://github.com/example/pull/1")

    result = runner.invoke(app, ["evidence", "list", "--cwd", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "https://github.com/example/pull/1" in result.output


# ---------------------------------------------------------------------------
# Populated state — JSON output
# ---------------------------------------------------------------------------


def test_evidence_list_json_shape(tmp_path: Path) -> None:
    """--json output has ok, count, and records fields with expected record shape."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    add_evidence(tmp_path, "commit", "a commit", url="https://example.com/commit/abc")

    result = runner.invoke(app, ["evidence", "list", "--cwd", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)

    assert data["ok"] is True
    assert data["count"] == 1
    assert len(data["records"]) == 1
    rec = data["records"][0]
    assert rec["kind"] == "commit"
    assert rec["description"] == "a commit"
    assert rec["evidence_url"] == "https://example.com/commit/abc"
    assert "created_at" in rec


def test_evidence_list_json_count_matches_records(tmp_path: Path) -> None:
    """count in JSON equals len(records)."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    for i in range(4):
        add_evidence(tmp_path, "commit", f"commit {i}")

    result = runner.invoke(app, ["evidence", "list", "--cwd", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["count"] == 4
    assert len(data["records"]) == 4


# ---------------------------------------------------------------------------
# Ordering
# ---------------------------------------------------------------------------


def test_evidence_list_deterministic_order(tmp_path: Path) -> None:
    """Records are returned in created_at ascending order (earliest first)."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    add_evidence(tmp_path, "commit", "first")
    add_evidence(tmp_path, "test_pass", "second")
    add_evidence(tmp_path, "pr", "third")

    result = runner.invoke(app, ["evidence", "list", "--cwd", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    timestamps = [r["created_at"] for r in data["records"]]
    assert timestamps == sorted(timestamps)


# ---------------------------------------------------------------------------
# --cwd support
# ---------------------------------------------------------------------------


def test_evidence_list_cwd(tmp_path: Path) -> None:
    """--cwd targets the correct repo without changing process cwd."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    add_evidence(tmp_path, "review_done", "cwd test evidence")

    result = runner.invoke(app, ["evidence", "list", "--cwd", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "review_done" in result.output
    assert "cwd test evidence" in result.output


def test_evidence_list_cwd_json(tmp_path: Path) -> None:
    """--cwd with --json targets the correct repo."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    add_evidence(tmp_path, "demo", "cwd json test")

    result = runner.invoke(app, ["evidence", "list", "--cwd", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["count"] == 1
    assert data["records"][0]["kind"] == "demo"
