"""Tests for --cwd support across Phase 2 commands (Issue #5).

Each test invokes a command with --cwd pointing to a tmp_path that is a fake
git repo with .spine/ already initialised, without changing the process cwd.
This validates that commands work for external-repo usage without requiring
cd or the SPINE_ROOT env var.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from spine.main import app

runner = CliRunner()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_git_repo(path: Path) -> Path:
    """Create a minimal fake git repo (.git dir only)."""
    (path / ".git").mkdir()
    return path


def spine_init(path: Path) -> None:
    result = runner.invoke(app, ["init", "--cwd", str(path)])
    assert result.exit_code == 0, f"init failed: {result.output}"


# ---------------------------------------------------------------------------
# spine doctor --cwd
# ---------------------------------------------------------------------------


def test_doctor_cwd(tmp_path: Path) -> None:
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    result = runner.invoke(app, ["doctor", "--cwd", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "passed" in result.output.lower()


def test_doctor_cwd_json(tmp_path: Path) -> None:
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    result = runner.invoke(app, ["doctor", "--cwd", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["passed"] is True
    assert str(tmp_path) in data["repo"]


# ---------------------------------------------------------------------------
# spine mission show --cwd
# ---------------------------------------------------------------------------


def test_mission_show_cwd(tmp_path: Path) -> None:
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    result = runner.invoke(app, ["mission", "show", "--cwd", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "mission-0001" in result.output


def test_mission_show_cwd_json(tmp_path: Path) -> None:
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    result = runner.invoke(app, ["mission", "show", "--cwd", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["id"] == "mission-0001"


# ---------------------------------------------------------------------------
# spine mission set --cwd
# ---------------------------------------------------------------------------


def test_mission_set_cwd(tmp_path: Path) -> None:
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    result = runner.invoke(
        app,
        ["mission", "set", "--cwd", str(tmp_path), "--title", "CWD Test Mission"],
    )
    assert result.exit_code == 0, result.output
    assert "CWD Test Mission" in result.output

    # Verify persisted
    result2 = runner.invoke(app, ["mission", "show", "--cwd", str(tmp_path), "--json"])
    assert result2.exit_code == 0, result2.output
    data = json.loads(result2.output)
    assert data["title"] == "CWD Test Mission"


# ---------------------------------------------------------------------------
# spine evidence add --cwd
# ---------------------------------------------------------------------------


def test_evidence_add_cwd(tmp_path: Path) -> None:
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    result = runner.invoke(
        app,
        ["evidence", "add", "--cwd", str(tmp_path), "--kind", "commit", "--description", "cwd test"],
    )
    assert result.exit_code == 0, result.output
    assert "Evidence added" in result.output

    evidence_file = tmp_path / ".spine" / "evidence.jsonl"
    record = json.loads(evidence_file.read_text().splitlines()[0])
    assert record["kind"] == "commit"
    assert record["description"] == "cwd test"


# ---------------------------------------------------------------------------
# spine decision add --cwd
# ---------------------------------------------------------------------------


def test_decision_add_cwd(tmp_path: Path) -> None:
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    result = runner.invoke(
        app,
        [
            "decision", "add",
            "--cwd", str(tmp_path),
            "--title", "CWD decision",
            "--why", "testing --cwd",
            "--decision", "add --cwd to all commands",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "CWD decision" in result.output

    decisions_file = tmp_path / ".spine" / "decisions.jsonl"
    record = json.loads(decisions_file.read_text().splitlines()[0])
    assert record["title"] == "CWD decision"


# ---------------------------------------------------------------------------
# spine opportunity score --cwd
# ---------------------------------------------------------------------------


def test_opportunity_score_cwd(tmp_path: Path) -> None:
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    result = runner.invoke(
        app,
        ["opportunity", "score", "CWD Opportunity", "--cwd", str(tmp_path)],
    )
    assert result.exit_code == 0, result.output
    assert "CWD Opportunity" in result.output

    opp_file = tmp_path / ".spine" / "opportunities.jsonl"
    record = json.loads(opp_file.read_text().splitlines()[0])
    assert record["title"] == "CWD Opportunity"


# ---------------------------------------------------------------------------
# spine drift scan --cwd
# ---------------------------------------------------------------------------


def test_drift_scan_cwd(tmp_path: Path) -> None:
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    result = runner.invoke(app, ["drift", "scan", "--cwd", str(tmp_path)])
    # Drift scan can legitimately succeed with no drift on a clean repo
    assert result.exit_code == 0, result.output


# ---------------------------------------------------------------------------
# spine brief --cwd
# ---------------------------------------------------------------------------


def test_brief_cwd(tmp_path: Path) -> None:
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    result = runner.invoke(
        app,
        ["brief", "--cwd", str(tmp_path), "--target", "claude"],
    )
    assert result.exit_code == 0, result.output
    assert "Brief generated" in result.output


# ---------------------------------------------------------------------------
# spine review weekly --cwd  (was already working; ensure non-hidden)
# ---------------------------------------------------------------------------


def test_review_weekly_cwd(tmp_path: Path) -> None:
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    result = runner.invoke(
        app,
        ["review", "weekly", "--cwd", str(tmp_path), "--recommendation", "continue"],
    )
    assert result.exit_code == 0, result.output
    assert "Weekly review generated" in result.output


def test_review_weekly_cwd_json(tmp_path: Path) -> None:
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    result = runner.invoke(
        app,
        ["review", "weekly", "--cwd", str(tmp_path), "--json"],
    )
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["recommendation"] == "continue"


# ---------------------------------------------------------------------------
# Isolation: two repos side-by-side
# ---------------------------------------------------------------------------


def test_cwd_two_repos_isolated(tmp_path: Path) -> None:
    """--cwd targets the correct repo even when two repos exist side by side."""
    repo_a = tmp_path / "repo_a"
    repo_b = tmp_path / "repo_b"
    repo_a.mkdir()
    repo_b.mkdir()

    make_git_repo(repo_a)
    make_git_repo(repo_b)
    spine_init(repo_a)
    spine_init(repo_b)

    # Set different titles in each repo
    runner.invoke(
        app,
        ["mission", "set", "--cwd", str(repo_a), "--title", "Repo A Mission"],
    )
    runner.invoke(
        app,
        ["mission", "set", "--cwd", str(repo_b), "--title", "Repo B Mission"],
    )

    # Verify targeting is isolated
    res_a = runner.invoke(app, ["mission", "show", "--cwd", str(repo_a), "--json"])
    res_b = runner.invoke(app, ["mission", "show", "--cwd", str(repo_b), "--json"])
    assert json.loads(res_a.output)["title"] == "Repo A Mission"
    assert json.loads(res_b.output)["title"] == "Repo B Mission"
