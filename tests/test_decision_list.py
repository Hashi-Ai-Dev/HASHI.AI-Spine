"""Tests for spine decision list command (Issue #64)."""

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


def add_decision(
    tmp_path: Path,
    title: str,
    why: str,
    decision: str,
    alternatives: str | None = None,
) -> None:
    args = [
        "decision", "add", "--cwd", str(tmp_path),
        "--title", title,
        "--why", why,
        "--decision", decision,
    ]
    if alternatives:
        args += ["--alternatives", alternatives]
    result = runner.invoke(app, args)
    assert result.exit_code == 0, f"decision add failed: {result.output}"


# ---------------------------------------------------------------------------
# Empty state
# ---------------------------------------------------------------------------


def test_decision_list_empty_human(tmp_path: Path) -> None:
    """Empty decisions.jsonl produces a friendly message, exit 0."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    result = runner.invoke(app, ["decision", "list", "--cwd", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "no decision" in result.output.lower()


def test_decision_list_empty_json(tmp_path: Path) -> None:
    """Empty decisions.jsonl with --json returns ok=True, count=0, records=[]."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    result = runner.invoke(app, ["decision", "list", "--cwd", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["count"] == 0
    assert data["records"] == []


# ---------------------------------------------------------------------------
# Populated state — human output
# ---------------------------------------------------------------------------


def test_decision_list_populated_human(tmp_path: Path) -> None:
    """Populated decisions.jsonl shows all records in human output."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    add_decision(tmp_path, "Use pydantic", "Type safety", "Adopt pydantic v2")
    add_decision(tmp_path, "Use typer", "Great UX", "Adopt typer")

    result = runner.invoke(app, ["decision", "list", "--cwd", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "Use pydantic" in result.output
    assert "Adopt pydantic v2" in result.output
    assert "Use typer" in result.output
    assert "Adopt typer" in result.output


def test_decision_list_shows_alternatives_in_human_output(tmp_path: Path) -> None:
    """Alternatives appear in human output when present."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    add_decision(
        tmp_path, "Choose Python", "Ecosystem", "Python",
        alternatives="Rust, Go",
    )

    result = runner.invoke(app, ["decision", "list", "--cwd", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "Rust" in result.output
    assert "Go" in result.output


# ---------------------------------------------------------------------------
# Populated state — JSON output
# ---------------------------------------------------------------------------


def test_decision_list_json_shape(tmp_path: Path) -> None:
    """--json output has ok, count, and records with all decision fields."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    add_decision(
        tmp_path, "A title", "A reason", "A decision", alternatives="Alt1, Alt2"
    )

    result = runner.invoke(app, ["decision", "list", "--cwd", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)

    assert data["ok"] is True
    assert data["count"] == 1
    assert len(data["records"]) == 1
    rec = data["records"][0]
    assert rec["title"] == "A title"
    assert rec["why"] == "A reason"
    assert rec["decision"] == "A decision"
    assert rec["alternatives"] == ["Alt1", "Alt2"]
    assert "created_at" in rec


def test_decision_list_json_count_matches_records(tmp_path: Path) -> None:
    """count in JSON equals len(records)."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    for i in range(3):
        add_decision(tmp_path, f"Decision {i}", f"Reason {i}", f"Outcome {i}")

    result = runner.invoke(app, ["decision", "list", "--cwd", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["count"] == 3
    assert len(data["records"]) == 3


# ---------------------------------------------------------------------------
# Ordering
# ---------------------------------------------------------------------------


def test_decision_list_deterministic_order(tmp_path: Path) -> None:
    """Records are returned in created_at ascending order (earliest first)."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    add_decision(tmp_path, "First", "r1", "d1")
    add_decision(tmp_path, "Second", "r2", "d2")
    add_decision(tmp_path, "Third", "r3", "d3")

    result = runner.invoke(app, ["decision", "list", "--cwd", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    timestamps = [r["created_at"] for r in data["records"]]
    assert timestamps == sorted(timestamps)


# ---------------------------------------------------------------------------
# --cwd support
# ---------------------------------------------------------------------------


def test_decision_list_cwd(tmp_path: Path) -> None:
    """--cwd targets the correct repo without changing process cwd."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    add_decision(tmp_path, "CWD decision", "cwd reason", "cwd outcome")

    result = runner.invoke(app, ["decision", "list", "--cwd", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "CWD decision" in result.output


def test_decision_list_cwd_json(tmp_path: Path) -> None:
    """--cwd with --json targets the correct repo."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    add_decision(tmp_path, "CWD JSON decision", "cwd json reason", "cwd json outcome")

    result = runner.invoke(app, ["decision", "list", "--cwd", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["count"] == 1
    assert data["records"][0]["title"] == "CWD JSON decision"
