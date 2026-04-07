"""Tests for Issue #16 — repo/branch context visibility + deterministic defaults.

Covers:
- get_default_branch() utility: resolves main/master locally, returns None when absent
- format_context_line(): produces consistent output format
- get_current_branch(): detached HEAD returns detached string
- mission show: prints context line in human mode, not in JSON mode
- drift scan: prints context line; warns when default branch unresolved
- doctor: human mode context line includes default branch; JSON mode includes default_branch field
- brief: prints context line
- review weekly: prints context line
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from spine.main import app
from spine.utils.paths import (
    format_context_line,
    get_current_branch,
    get_default_branch,
)

runner = CliRunner()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_git_repo_with_commit(tmp_path: Path, branch: str = "main") -> Path:
    """Create a real git repo with one commit on the specified branch."""
    subprocess.run(
        ["git", "init", f"--initial-branch={branch}"],
        cwd=tmp_path,
        capture_output=True,
    )
    for key, val in [
        ("user.email", "test@test.com"),
        ("user.name", "Test User"),
        ("commit.gpgsign", "false"),
    ]:
        subprocess.run(
            ["git", "config", key, val],
            cwd=tmp_path,
            capture_output=True,
        )
    (tmp_path / "README.md").write_text("# Test\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=tmp_path,
        capture_output=True,
    )
    return tmp_path


def spine_init(tmp_path: Path) -> None:
    result = runner.invoke(app, ["init", "--cwd", str(tmp_path)])
    assert result.exit_code == 0, f"init failed: {result.output}"


# ---------------------------------------------------------------------------
# Unit: get_default_branch()
# ---------------------------------------------------------------------------


def test_get_default_branch_finds_main(tmp_path: Path) -> None:
    make_git_repo_with_commit(tmp_path, branch="main")
    branch = get_default_branch(tmp_path)
    assert branch == "main"


def test_get_default_branch_finds_master(tmp_path: Path) -> None:
    make_git_repo_with_commit(tmp_path, branch="master")
    branch = get_default_branch(tmp_path)
    assert branch == "master"


def test_get_default_branch_returns_none_when_absent(tmp_path: Path) -> None:
    """No main/master/remote — returns None."""
    make_git_repo_with_commit(tmp_path, branch="develop")
    branch = get_default_branch(tmp_path)
    assert branch is None


# ---------------------------------------------------------------------------
# Unit: format_context_line()
# ---------------------------------------------------------------------------


def test_format_context_line_with_default_branch(tmp_path: Path) -> None:
    line = format_context_line(tmp_path, "main", "main")
    assert str(tmp_path) in line
    assert "branch: main" in line
    assert "default: main" in line


def test_format_context_line_unresolved_default(tmp_path: Path) -> None:
    line = format_context_line(tmp_path, "feature/foo", None)
    assert "default: (unresolved)" in line


def test_format_context_line_with_compare_target(tmp_path: Path) -> None:
    line = format_context_line(tmp_path, "feature/foo", None, compare_target="main")
    assert "compare: main" in line
    assert "default:" not in line


def test_format_context_line_detached(tmp_path: Path) -> None:
    line = format_context_line(tmp_path, "(detached:abc1234)", "main")
    assert "branch: (detached:abc1234)" in line


# ---------------------------------------------------------------------------
# Unit: get_current_branch() detached HEAD
# ---------------------------------------------------------------------------


def test_get_current_branch_detached_head(tmp_path: Path) -> None:
    make_git_repo_with_commit(tmp_path, branch="main")
    # Detach HEAD by checking out the commit SHA directly
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    sha = result.stdout.strip()
    subprocess.run(["git", "checkout", sha], cwd=tmp_path, capture_output=True)

    branch = get_current_branch(tmp_path)
    assert branch.startswith("(detached:")


# ---------------------------------------------------------------------------
# Integration: doctor context output
# ---------------------------------------------------------------------------


def test_doctor_shows_context_line(tmp_path: Path) -> None:
    make_git_repo_with_commit(tmp_path, branch="main")
    spine_init(tmp_path)

    result = runner.invoke(app, ["doctor", "--cwd", str(tmp_path)])
    assert result.exit_code == 0
    assert "repo:" in result.output
    assert "branch:" in result.output
    assert "default:" in result.output


def test_doctor_json_includes_default_branch(tmp_path: Path) -> None:
    import json as json_mod

    make_git_repo_with_commit(tmp_path, branch="main")
    spine_init(tmp_path)

    result = runner.invoke(app, ["doctor", "--cwd", str(tmp_path), "--json"])
    assert result.exit_code == 0
    data = json_mod.loads(result.output)
    assert "default_branch" in data
    assert data["default_branch"] == "main"


def test_doctor_warns_when_default_branch_unresolved(tmp_path: Path) -> None:
    make_git_repo_with_commit(tmp_path, branch="develop")
    spine_init(tmp_path)

    result = runner.invoke(app, ["doctor", "--cwd", str(tmp_path)])
    assert result.exit_code == 0
    assert "default: (unresolved)" in result.output
    assert "Warning" in result.output


# ---------------------------------------------------------------------------
# Integration: drift scan context output
# ---------------------------------------------------------------------------


def test_drift_scan_shows_context_line(tmp_path: Path) -> None:
    make_git_repo_with_commit(tmp_path, branch="main")
    spine_init(tmp_path)

    result = runner.invoke(app, ["drift", "scan", "--cwd", str(tmp_path)])
    assert result.exit_code == 0
    assert "repo:" in result.output
    assert "branch:" in result.output


def test_drift_scan_shows_compare_when_against_given(tmp_path: Path) -> None:
    make_git_repo_with_commit(tmp_path, branch="main")
    spine_init(tmp_path)

    result = runner.invoke(
        app, ["drift", "scan", "--cwd", str(tmp_path), "--against", "main"]
    )
    assert result.exit_code == 0
    assert "compare: main" in result.output


def test_drift_scan_warns_when_default_unresolved(tmp_path: Path) -> None:
    make_git_repo_with_commit(tmp_path, branch="develop")
    spine_init(tmp_path)

    result = runner.invoke(app, ["drift", "scan", "--cwd", str(tmp_path)])
    assert result.exit_code == 0
    assert "default: (unresolved)" in result.output
    assert "Warning" in result.output


# ---------------------------------------------------------------------------
# Integration: mission show context output
# ---------------------------------------------------------------------------


def test_mission_show_displays_context_line(tmp_path: Path) -> None:
    make_git_repo_with_commit(tmp_path, branch="main")
    spine_init(tmp_path)

    result = runner.invoke(app, ["mission", "show", "--cwd", str(tmp_path)])
    assert result.exit_code == 0
    assert "repo:" in result.output
    assert "branch:" in result.output
    assert "default:" in result.output


def test_mission_show_json_no_context_line(tmp_path: Path) -> None:
    """JSON output should not contain the context line (machine-readable)."""
    import json as json_mod

    make_git_repo_with_commit(tmp_path, branch="main")
    spine_init(tmp_path)

    result = runner.invoke(app, ["mission", "show", "--cwd", str(tmp_path), "--json"])
    assert result.exit_code == 0
    # Should be valid JSON
    data = json_mod.loads(result.output)
    assert "title" in data


# ---------------------------------------------------------------------------
# Integration: review weekly context output
# ---------------------------------------------------------------------------


def test_review_weekly_shows_context_line(tmp_path: Path) -> None:
    make_git_repo_with_commit(tmp_path, branch="main")
    spine_init(tmp_path)

    result = runner.invoke(
        app,
        ["review", "weekly", "--cwd", str(tmp_path), "--recommendation", "continue"],
    )
    assert result.exit_code == 0
    assert "repo:" in result.output
    assert "branch:" in result.output


# ---------------------------------------------------------------------------
# Integration: brief context output
# ---------------------------------------------------------------------------


def test_brief_shows_context_line(tmp_path: Path) -> None:
    make_git_repo_with_commit(tmp_path, branch="main")
    spine_init(tmp_path)

    result = runner.invoke(
        app, ["brief", "--cwd", str(tmp_path), "--target", "claude"]
    )
    assert result.exit_code == 0
    assert "repo:" in result.output
    assert "branch:" in result.output
