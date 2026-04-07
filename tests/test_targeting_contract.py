"""Tests for the explicit repo targeting contract (Issue #15 — Phase 3A.2).

Contract:
    Target resolution precedence (highest to lowest):
    1. --cwd <path>   if explicitly provided
    2. SPINE_ROOT     if set in the environment
    3. current working directory

Tests cover:
    - --cwd overrides SPINE_ROOT
    - SPINE_ROOT overrides cwd fallback
    - invalid --cwd (not a git repo) produces a clear error
    - invalid SPINE_ROOT (path does not exist) produces a clear error
    - deterministic targeting in multi-repo scenarios
    - resolve_roots() unit-level precedence checks
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from spine.main import app
from spine.cli.app import resolve_roots
from spine.utils.paths import GitRepoNotFoundError

runner = CliRunner()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_git_repo(path: Path) -> Path:
    """Create a minimal fake git repo (just a .git dir)."""
    (path / ".git").mkdir(parents=True, exist_ok=True)
    return path


def spine_init(path: Path) -> None:
    result = runner.invoke(app, ["init", "--cwd", str(path)])
    assert result.exit_code == 0, f"init failed: {result.output}"


# ---------------------------------------------------------------------------
# Unit tests: resolve_roots() precedence
# ---------------------------------------------------------------------------


def test_resolve_roots_cwd_wins_over_spine_root(tmp_path: Path) -> None:
    """--cwd takes precedence over SPINE_ROOT when both are supplied."""
    repo_a = tmp_path / "repo_a"
    repo_b = tmp_path / "repo_b"
    make_git_repo(repo_a)
    make_git_repo(repo_b)

    old = os.environ.pop("SPINE_ROOT", None)
    try:
        os.environ["SPINE_ROOT"] = str(repo_b)
        git_root, spine_root = resolve_roots(cwd=repo_a)
        # --cwd=repo_a wins; repo_b (SPINE_ROOT) is ignored
        assert git_root == repo_a.resolve()
        assert spine_root == repo_a.resolve() / ".spine"
    finally:
        os.environ.pop("SPINE_ROOT", None)
        if old is not None:
            os.environ["SPINE_ROOT"] = old


def test_resolve_roots_spine_root_wins_over_cwd_fallback(tmp_path: Path) -> None:
    """SPINE_ROOT wins over the current working directory when --cwd is absent."""
    repo_a = tmp_path / "repo_a"
    make_git_repo(repo_a)

    old = os.environ.pop("SPINE_ROOT", None)
    original_dir = os.getcwd()
    try:
        os.environ["SPINE_ROOT"] = str(repo_a)
        # resolve_roots(cwd=None) with SPINE_ROOT set → should use repo_a
        git_root, spine_root = resolve_roots(cwd=None)
        assert git_root == repo_a.resolve()
        assert spine_root == repo_a.resolve() / ".spine"
    finally:
        os.environ.pop("SPINE_ROOT", None)
        if old is not None:
            os.environ["SPINE_ROOT"] = old
        os.chdir(original_dir)


def test_resolve_roots_cwd_fallback_when_nothing_set(tmp_path: Path) -> None:
    """Without --cwd or SPINE_ROOT, resolve_roots() uses the current directory."""
    make_git_repo(tmp_path)

    old = os.environ.pop("SPINE_ROOT", None)
    original_dir = os.getcwd()
    try:
        os.chdir(tmp_path)
        git_root, spine_root = resolve_roots(cwd=None)
        assert git_root == tmp_path.resolve()
    finally:
        os.environ.pop("SPINE_ROOT", None)
        if old is not None:
            os.environ["SPINE_ROOT"] = old
        os.chdir(original_dir)


# ---------------------------------------------------------------------------
# Failure semantics: invalid targets
# ---------------------------------------------------------------------------


def test_resolve_roots_invalid_cwd_not_a_git_repo(tmp_path: Path) -> None:
    """--cwd pointing to a non-repo path raises GitRepoNotFoundError with clear message."""
    not_a_repo = tmp_path / "not_a_repo"
    not_a_repo.mkdir()

    old = os.environ.pop("SPINE_ROOT", None)
    try:
        with pytest.raises(GitRepoNotFoundError) as exc_info:
            resolve_roots(cwd=not_a_repo)
        msg = str(exc_info.value)
        assert str(not_a_repo.resolve()) in msg
        assert "--cwd" in msg
    finally:
        os.environ.pop("SPINE_ROOT", None)
        if old is not None:
            os.environ["SPINE_ROOT"] = old


def test_resolve_roots_invalid_spine_root_path_missing(tmp_path: Path) -> None:
    """SPINE_ROOT pointing to a non-existent path raises FileNotFoundError with clear message."""
    missing_path = tmp_path / "does_not_exist"

    old = os.environ.pop("SPINE_ROOT", None)
    try:
        os.environ["SPINE_ROOT"] = str(missing_path)
        with pytest.raises(FileNotFoundError) as exc_info:
            resolve_roots(cwd=None)
        msg = str(exc_info.value)
        assert str(missing_path) in msg
        assert "SPINE_ROOT" in msg
    finally:
        os.environ.pop("SPINE_ROOT", None)
        if old is not None:
            os.environ["SPINE_ROOT"] = old


def test_resolve_roots_no_repo_in_cwd(tmp_path: Path) -> None:
    """No git repo in cwd (no --cwd or SPINE_ROOT) raises GitRepoNotFoundError."""
    # tmp_path is outside any git repo
    old = os.environ.pop("SPINE_ROOT", None)
    original_dir = os.getcwd()
    try:
        os.chdir(tmp_path)
        with pytest.raises(GitRepoNotFoundError) as exc_info:
            resolve_roots(cwd=None)
        msg = str(exc_info.value)
        # Message should mention cwd source
        assert "current working directory" in msg
    finally:
        os.environ.pop("SPINE_ROOT", None)
        if old is not None:
            os.environ["SPINE_ROOT"] = old
        os.chdir(original_dir)


# ---------------------------------------------------------------------------
# CLI integration: --cwd overrides SPINE_ROOT
# ---------------------------------------------------------------------------


def test_cli_cwd_overrides_spine_root(tmp_path: Path) -> None:
    """CLI: --cwd targets the correct repo even when SPINE_ROOT points elsewhere."""
    repo_a = tmp_path / "repo_a"
    repo_b = tmp_path / "repo_b"
    repo_a.mkdir()
    repo_b.mkdir()

    make_git_repo(repo_a)
    make_git_repo(repo_b)
    spine_init(repo_a)
    spine_init(repo_b)

    # Give each repo a distinct mission title
    runner.invoke(app, ["mission", "set", "--cwd", str(repo_a), "--title", "Mission A"])
    runner.invoke(app, ["mission", "set", "--cwd", str(repo_b), "--title", "Mission B"])

    old = os.environ.pop("SPINE_ROOT", None)
    try:
        # Set SPINE_ROOT to repo_b; --cwd=repo_a should win
        os.environ["SPINE_ROOT"] = str(repo_b)
        result = runner.invoke(app, ["mission", "show", "--cwd", str(repo_a)])
        assert result.exit_code == 0, result.output
        assert "Mission A" in result.output
        assert "Mission B" not in result.output
    finally:
        os.environ.pop("SPINE_ROOT", None)
        if old is not None:
            os.environ["SPINE_ROOT"] = old


def test_cli_spine_root_used_when_no_cwd(tmp_path: Path) -> None:
    """CLI: SPINE_ROOT governs when --cwd is not provided."""
    repo_a = tmp_path / "repo_a"
    repo_b = tmp_path / "repo_b"
    repo_a.mkdir()
    repo_b.mkdir()

    make_git_repo(repo_a)
    make_git_repo(repo_b)
    spine_init(repo_a)
    spine_init(repo_b)

    runner.invoke(app, ["mission", "set", "--cwd", str(repo_a), "--title", "Mission A"])
    runner.invoke(app, ["mission", "set", "--cwd", str(repo_b), "--title", "Mission B"])

    old = os.environ.pop("SPINE_ROOT", None)
    original_dir = os.getcwd()
    try:
        # Set SPINE_ROOT to repo_a; cwd is repo_b; expect repo_a to win
        os.environ["SPINE_ROOT"] = str(repo_a)
        os.chdir(repo_b)
        result = runner.invoke(app, ["mission", "show"])
        assert result.exit_code == 0, result.output
        assert "Mission A" in result.output
        assert "Mission B" not in result.output
    finally:
        os.environ.pop("SPINE_ROOT", None)
        if old is not None:
            os.environ["SPINE_ROOT"] = old
        os.chdir(original_dir)


# ---------------------------------------------------------------------------
# CLI integration: clear error on invalid target
# ---------------------------------------------------------------------------


def test_cli_invalid_cwd_exit_code_and_message(tmp_path: Path) -> None:
    """CLI: --cwd pointing to a non-repo directory exits 2 (context failure) with a useful message."""
    not_a_repo = tmp_path / "not_a_repo"
    not_a_repo.mkdir()

    old = os.environ.pop("SPINE_ROOT", None)
    try:
        result = runner.invoke(app, ["doctor", "--cwd", str(not_a_repo)])
        assert result.exit_code == 2, f"Expected exit 2 (context failure), got {result.exit_code}"
        combined = (result.output or "") + (result.stderr if hasattr(result, "stderr") and result.stderr else "")
        assert "No git repository" in combined or "git" in combined.lower()
    finally:
        os.environ.pop("SPINE_ROOT", None)
        if old is not None:
            os.environ["SPINE_ROOT"] = old


def test_cli_invalid_spine_root_exit_code_and_message(tmp_path: Path) -> None:
    """CLI: SPINE_ROOT pointing to a missing path exits 2 (context failure) with a useful message."""
    missing = tmp_path / "no_such_dir"

    old = os.environ.pop("SPINE_ROOT", None)
    try:
        os.environ["SPINE_ROOT"] = str(missing)
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 2, f"Expected exit 2 (context failure), got {result.exit_code}"
        combined = (result.output or "") + (result.stderr if hasattr(result, "stderr") and result.stderr else "")
        assert "SPINE_ROOT" in combined
    finally:
        os.environ.pop("SPINE_ROOT", None)
        if old is not None:
            os.environ["SPINE_ROOT"] = old


# ---------------------------------------------------------------------------
# Multi-repo determinism
# ---------------------------------------------------------------------------


def test_deterministic_targeting_multi_repo(tmp_path: Path) -> None:
    """Multiple repos side-by-side: --cwd always targets the correct one."""
    repos = {}
    for name in ("alpha", "beta", "gamma"):
        repo = tmp_path / name
        repo.mkdir()
        make_git_repo(repo)
        spine_init(repo)
        runner.invoke(app, ["mission", "set", "--cwd", str(repo), "--title", f"Mission {name}"])
        repos[name] = repo

    old = os.environ.pop("SPINE_ROOT", None)
    try:
        for name, repo in repos.items():
            result = runner.invoke(app, ["mission", "show", "--cwd", str(repo)])
            assert result.exit_code == 0, result.output
            assert f"Mission {name}" in result.output
            for other_name in repos:
                if other_name != name:
                    assert f"Mission {other_name}" not in result.output
    finally:
        os.environ.pop("SPINE_ROOT", None)
        if old is not None:
            os.environ["SPINE_ROOT"] = old
