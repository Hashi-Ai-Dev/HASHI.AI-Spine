"""Tests for Issue #73: SPINE_ROOT ergonomics for long-running shells and multi-repo use.

Covers:
- spine target: shows resolved target with source annotation
- spine target --json: machine-readable output
- spine target --cwd: shows --cwd source, highest precedence
- SPINE_ROOT env: shows SPINE_ROOT source
- --cwd overrides SPINE_ROOT (existing contract, verified)
- one-shot SPINE_ROOT pattern (no shell pollution)
- multi-repo isolation via repeated targeting
- invalid target exits 2 with clear message
- backward compatibility: existing targeting contract unchanged
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from typer.testing import CliRunner

from spine.main import app

runner = CliRunner()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_git_repo(path: Path) -> Path:
    """Create a minimal fake git repo."""
    (path / ".git").mkdir(parents=True, exist_ok=True)
    return path


def spine_init(path: Path) -> None:
    result = runner.invoke(app, ["init", "--cwd", str(path)])
    assert result.exit_code == 0, f"init failed: {result.output}"


# ---------------------------------------------------------------------------
# spine target — source annotation
# ---------------------------------------------------------------------------


def test_target_shows_current_directory_source(tmp_path: Path) -> None:
    """spine target with no --cwd and no SPINE_ROOT reports 'current directory'."""
    make_git_repo(tmp_path)
    old = os.environ.pop("SPINE_ROOT", None)
    original_dir = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["target"])
        assert result.exit_code == 0, result.output
        assert "current directory" in result.output
        assert str(tmp_path) in result.output
    finally:
        os.environ.pop("SPINE_ROOT", None)
        if old is not None:
            os.environ["SPINE_ROOT"] = old
        os.chdir(original_dir)


def test_target_shows_spine_root_source(tmp_path: Path) -> None:
    """spine target reports SPINE_ROOT as source when env var is set."""
    make_git_repo(tmp_path)
    old = os.environ.pop("SPINE_ROOT", None)
    try:
        os.environ["SPINE_ROOT"] = str(tmp_path)
        result = runner.invoke(app, ["target"])
        assert result.exit_code == 0, result.output
        assert "SPINE_ROOT" in result.output
        assert str(tmp_path) in result.output
    finally:
        os.environ.pop("SPINE_ROOT", None)
        if old is not None:
            os.environ["SPINE_ROOT"] = old


def test_target_shows_cwd_flag_source(tmp_path: Path) -> None:
    """spine target --cwd reports --cwd as source."""
    make_git_repo(tmp_path)
    old = os.environ.pop("SPINE_ROOT", None)
    try:
        result = runner.invoke(app, ["target", "--cwd", str(tmp_path)])
        assert result.exit_code == 0, result.output
        assert "--cwd" in result.output
        assert str(tmp_path) in result.output
    finally:
        os.environ.pop("SPINE_ROOT", None)
        if old is not None:
            os.environ["SPINE_ROOT"] = old


def test_target_cwd_overrides_spine_root(tmp_path: Path) -> None:
    """spine target --cwd wins over SPINE_ROOT — preserves existing precedence contract."""
    repo_a = tmp_path / "repo_a"
    repo_b = tmp_path / "repo_b"
    make_git_repo(repo_a)
    make_git_repo(repo_b)

    old = os.environ.pop("SPINE_ROOT", None)
    try:
        os.environ["SPINE_ROOT"] = str(repo_b)
        result = runner.invoke(app, ["target", "--cwd", str(repo_a)])
        assert result.exit_code == 0, result.output
        assert str(repo_a.resolve()) in result.output
        # repo_b should not appear as the resolved target
        assert "--cwd" in result.output
    finally:
        os.environ.pop("SPINE_ROOT", None)
        if old is not None:
            os.environ["SPINE_ROOT"] = old


# ---------------------------------------------------------------------------
# spine target --json
# ---------------------------------------------------------------------------


def test_target_json_current_directory(tmp_path: Path) -> None:
    """spine target --json returns correct fields when resolved from cwd."""
    make_git_repo(tmp_path)
    old = os.environ.pop("SPINE_ROOT", None)
    original_dir = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["target", "--json"])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["source"] == "current_directory"
        assert str(tmp_path) in data["target"]
        assert ".spine" in data["spine_dir"]
        assert data["spine_root_env"] is None
    finally:
        os.environ.pop("SPINE_ROOT", None)
        if old is not None:
            os.environ["SPINE_ROOT"] = old
        os.chdir(original_dir)


def test_target_json_spine_root_env(tmp_path: Path) -> None:
    """spine target --json reports spine_root_env and source=spine_root_env."""
    make_git_repo(tmp_path)
    old = os.environ.pop("SPINE_ROOT", None)
    try:
        os.environ["SPINE_ROOT"] = str(tmp_path)
        result = runner.invoke(app, ["target", "--json"])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["source"] == "spine_root_env"
        assert str(tmp_path) in data["target"]
        assert data["spine_root_env"] == str(tmp_path)
    finally:
        os.environ.pop("SPINE_ROOT", None)
        if old is not None:
            os.environ["SPINE_ROOT"] = old


def test_target_json_cwd_flag(tmp_path: Path) -> None:
    """spine target --json with --cwd reports source=cwd_flag."""
    make_git_repo(tmp_path)
    old = os.environ.pop("SPINE_ROOT", None)
    try:
        result = runner.invoke(app, ["target", "--cwd", str(tmp_path), "--json"])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["source"] == "cwd_flag"
        assert str(tmp_path.resolve()) in data["target"]
    finally:
        os.environ.pop("SPINE_ROOT", None)
        if old is not None:
            os.environ["SPINE_ROOT"] = old


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


def test_target_invalid_cwd_exits_2(tmp_path: Path) -> None:
    """spine target --cwd pointing to a non-repo exits 2."""
    not_a_repo = tmp_path / "not_a_repo"
    not_a_repo.mkdir()
    old = os.environ.pop("SPINE_ROOT", None)
    try:
        result = runner.invoke(app, ["target", "--cwd", str(not_a_repo)])
        assert result.exit_code == 2, f"Expected exit 2, got {result.exit_code}: {result.output}"
    finally:
        os.environ.pop("SPINE_ROOT", None)
        if old is not None:
            os.environ["SPINE_ROOT"] = old


def test_target_invalid_spine_root_exits_2(tmp_path: Path) -> None:
    """spine target with SPINE_ROOT pointing to a missing path exits 2."""
    missing = tmp_path / "no_such_dir"
    old = os.environ.pop("SPINE_ROOT", None)
    try:
        os.environ["SPINE_ROOT"] = str(missing)
        result = runner.invoke(app, ["target"])
        assert result.exit_code == 2, f"Expected exit 2, got {result.exit_code}: {result.output}"
        assert "SPINE_ROOT" in result.output
    finally:
        os.environ.pop("SPINE_ROOT", None)
        if old is not None:
            os.environ["SPINE_ROOT"] = old


def test_target_invalid_cwd_json_exits_2(tmp_path: Path) -> None:
    """spine target --cwd non-repo --json exits 2 with JSON error."""
    not_a_repo = tmp_path / "not_a_repo"
    not_a_repo.mkdir()
    old = os.environ.pop("SPINE_ROOT", None)
    try:
        result = runner.invoke(app, ["target", "--cwd", str(not_a_repo), "--json"])
        assert result.exit_code == 2
        data = json.loads(result.output)
        assert "error" in data
    finally:
        os.environ.pop("SPINE_ROOT", None)
        if old is not None:
            os.environ["SPINE_ROOT"] = old


# ---------------------------------------------------------------------------
# Multi-repo: one-shot SPINE_ROOT pattern (no shell pollution)
# ---------------------------------------------------------------------------


def test_one_shot_spine_root_targets_correct_repo(tmp_path: Path) -> None:
    """One-shot SPINE_ROOT per-command targets the correct repo without persisting."""
    repo_a = tmp_path / "repo_a"
    repo_b = tmp_path / "repo_b"
    make_git_repo(repo_a)
    make_git_repo(repo_b)
    spine_init(repo_a)
    spine_init(repo_b)

    runner.invoke(app, ["mission", "set", "--cwd", str(repo_a), "--title", "Mission Alpha"])
    runner.invoke(app, ["mission", "set", "--cwd", str(repo_b), "--title", "Mission Beta"])

    old = os.environ.pop("SPINE_ROOT", None)
    try:
        # Simulate "one-shot": set SPINE_ROOT for a single command, then unset
        os.environ["SPINE_ROOT"] = str(repo_a)
        res_a = runner.invoke(app, ["target", "--json"])
        os.environ.pop("SPINE_ROOT", None)

        os.environ["SPINE_ROOT"] = str(repo_b)
        res_b = runner.invoke(app, ["target", "--json"])
        os.environ.pop("SPINE_ROOT", None)

        data_a = json.loads(res_a.output)
        data_b = json.loads(res_b.output)

        assert str(repo_a.resolve()) in data_a["target"]
        assert str(repo_b.resolve()) in data_b["target"]
        assert data_a["source"] == "spine_root_env"
        assert data_b["source"] == "spine_root_env"
    finally:
        os.environ.pop("SPINE_ROOT", None)
        if old is not None:
            os.environ["SPINE_ROOT"] = old


def test_multi_repo_targeting_isolation(tmp_path: Path) -> None:
    """spine target correctly isolates multi-repo targeting across --cwd calls."""
    repos = {}
    for name in ("alpha", "beta", "gamma"):
        repo = tmp_path / name
        repo.mkdir()
        make_git_repo(repo)
        repos[name] = repo

    old = os.environ.pop("SPINE_ROOT", None)
    try:
        for name, repo in repos.items():
            result = runner.invoke(app, ["target", "--cwd", str(repo), "--json"])
            assert result.exit_code == 0, result.output
            data = json.loads(result.output)
            assert str(repo.resolve()) in data["target"]
            assert data["source"] == "cwd_flag"
            # Other repos must not appear as the target
            for other_name, other_repo in repos.items():
                if other_name != name:
                    assert str(other_repo.resolve()) not in data["target"]
    finally:
        os.environ.pop("SPINE_ROOT", None)
        if old is not None:
            os.environ["SPINE_ROOT"] = old


# ---------------------------------------------------------------------------
# Backward compatibility: existing commands unaffected
# ---------------------------------------------------------------------------


def test_existing_cwd_contract_unchanged(tmp_path: Path) -> None:
    """Adding spine target does not change --cwd behavior for other commands."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    result = runner.invoke(app, ["doctor", "--cwd", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "passed" in result.output.lower()


def test_existing_spine_root_contract_unchanged(tmp_path: Path) -> None:
    """Adding spine target does not change SPINE_ROOT behavior for other commands."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    old = os.environ.pop("SPINE_ROOT", None)
    try:
        os.environ["SPINE_ROOT"] = str(tmp_path)
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0, result.output
        assert "passed" in result.output.lower()
    finally:
        os.environ.pop("SPINE_ROOT", None)
        if old is not None:
            os.environ["SPINE_ROOT"] = old


def test_repeated_targeting_long_running_shell(tmp_path: Path) -> None:
    """Repeated commands in a 'long-running shell' (SPINE_ROOT set once) work correctly."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    old = os.environ.pop("SPINE_ROOT", None)
    try:
        os.environ["SPINE_ROOT"] = str(tmp_path)

        # Simulate repeated commands in the same shell session
        for _ in range(3):
            res = runner.invoke(app, ["target", "--json"])
            assert res.exit_code == 0, res.output
            data = json.loads(res.output)
            assert str(tmp_path.resolve()) in data["target"]
            assert data["source"] == "spine_root_env"

        # Also verify an actual governance command works
        res2 = runner.invoke(app, ["doctor"])
        assert res2.exit_code == 0, res2.output
    finally:
        os.environ.pop("SPINE_ROOT", None)
        if old is not None:
            os.environ["SPINE_ROOT"] = old
