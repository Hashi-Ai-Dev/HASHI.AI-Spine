"""Tests for spine mission show and spine mission-set commands (Phase 2)."""

from __future__ import annotations

import os
import yaml
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


def run_mission_show(tmp_path: Path, *extra_args: str) -> tuple[int, str, str]:
    original = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["mission", "show", *extra_args])
    finally:
        os.chdir(original)
    return result.exit_code, result.output, ""


def run_mission_set(tmp_path: Path, *extra_args: str) -> tuple[int, str, str]:
    original = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["mission", "set", *extra_args])
    finally:
        os.chdir(original)
    return result.exit_code, result.output, ""


# ---------------------------------------------------------------------------
# Tests: spine mission show
# ---------------------------------------------------------------------------

def test_mission_show_displays_fields(tmp_path: Path) -> None:
    """mission show displays all key mission fields in a table."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_mission_show(tmp_path)
    assert exit_code == 0, stdout

    # Check that key fields appear in the output
    assert "mission-0001" in stdout
    assert "Define active mission" in stdout
    assert "active" in stdout  # default status


def test_mission_show_requires_init(tmp_path: Path) -> None:
    """mission show exits with error when .spine/mission.yaml does not exist."""
    make_git_repo(tmp_path)
    # Do NOT run init

    exit_code, stdout, _ = run_mission_show(tmp_path)
    assert exit_code == 1
    assert "mission.yaml" in stdout.lower() or "not found" in stdout.lower()


# ---------------------------------------------------------------------------
# Tests: spine mission-set --title
# ---------------------------------------------------------------------------

def test_mission_set_title_updates_title(tmp_path: Path) -> None:
    """mission-set --title updates the mission title."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_mission_set(tmp_path, "--title", "My New Mission")
    assert exit_code == 0, stdout
    assert "My New Mission" in stdout

    # Verify the file was updated
    mission_path = tmp_path / ".spine" / "mission.yaml"
    raw = mission_path.read_text()
    mission = yaml.safe_load(raw)
    assert mission["title"] == "My New Mission"


# ---------------------------------------------------------------------------
# Tests: spine mission-set --status
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("valid_status", ["active", "paused", "complete", "killed"])
def test_mission_set_status_accepts_valid_values(tmp_path: Path, valid_status: str) -> None:
    """mission-set --status accepts active, paused, complete, killed."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_mission_set(tmp_path, "--status", valid_status)
    assert exit_code == 0, stdout
    assert valid_status in stdout


@pytest.mark.parametrize("invalid_status", ["running", "pending", "deleted", "Active", "ACTIVE", ""])
def test_mission_set_status_rejects_invalid_values(tmp_path: Path, invalid_status: str) -> None:
    """mission-set --status rejects invalid status values."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_mission_set(tmp_path, "--status", invalid_status)
    assert exit_code == 1
    assert "Validation error" in stdout or "Invalid" in stdout


# ---------------------------------------------------------------------------
# Tests: spine mission-set --scope
# ---------------------------------------------------------------------------

def test_mission_set_scope_accepts_comma_separated_items(tmp_path: Path) -> None:
    """mission-set --scope accepts comma-separated allowed scope items."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_mission_set(
        tmp_path,
        "--scope", "web,api,database",
    )
    assert exit_code == 0, stdout

    mission_path = tmp_path / ".spine" / "mission.yaml"
    mission = yaml.safe_load(mission_path.read_text())
    assert mission["allowed_scope"] == ["web", "api", "database"]


def test_mission_set_scope_trims_whitespace(tmp_path: Path) -> None:
    """mission-set --scope trims whitespace from each item."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_mission_set(
        tmp_path,
        "--scope", "  web  ,  api  ,  database  ",
    )
    assert exit_code == 0, stdout

    mission_path = tmp_path / ".spine" / "mission.yaml"
    mission = yaml.safe_load(mission_path.read_text())
    assert mission["allowed_scope"] == ["web", "api", "database"]


# ---------------------------------------------------------------------------
# Tests: spine mission-set --forbid
# ---------------------------------------------------------------------------

def test_mission_set_forbid_accepts_comma_separated_items(tmp_path: Path) -> None:
    """mission-set --forbid accepts comma-separated forbidden expansions."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_mission_set(
        tmp_path,
        "--forbid", "billing,auth,notifications",
    )
    assert exit_code == 0, stdout

    mission_path = tmp_path / ".spine" / "mission.yaml"
    mission = yaml.safe_load(mission_path.read_text())
    assert mission["forbidden_expansions"] == ["billing", "auth", "notifications"]


# ---------------------------------------------------------------------------
# Tests: updated_at refresh
# ---------------------------------------------------------------------------

def test_mission_show_json_output(tmp_path: Path) -> None:
    """mission show --json outputs valid JSON with expected fields."""
    import json as json_module
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_mission_show(tmp_path, "--json")
    assert exit_code == 0, stdout

    data = json_module.loads(stdout)
    assert data["id"] == "mission-0001"
    assert data["title"] == "Define active mission"
    assert data["status"] == "active"
    assert "allowed_scope" in data
    assert "forbidden_expansions" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_mission_set_refreshes_updated_at(tmp_path: Path) -> None:
    """mission-set updates the updated_at timestamp."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    mission_path = tmp_path / ".spine" / "mission.yaml"
    before = yaml.safe_load(mission_path.read_text())["updated_at"]

    # Wait a moment so the new timestamp is distinguishable
    import time
    time.sleep(0.01)

    run_mission_set(tmp_path, "--title", "Updated Title")
    after = yaml.safe_load(mission_path.read_text())["updated_at"]

    assert after != before