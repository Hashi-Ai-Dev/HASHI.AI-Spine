"""Tests for spine doctor command (Phase 2)."""

from __future__ import annotations

import os
from pathlib import Path

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


def run_doctor(tmp_path: Path, *extra_args: str) -> tuple[int, str, str]:
    original = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["doctor", *extra_args])
    finally:
        os.chdir(original)
    return result.exit_code, result.output, ""


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_doctor_passes_with_valid_spine_state(tmp_path: Path) -> None:
    """doctor with valid .spine/ state passes with no errors."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_doctor(tmp_path)
    assert exit_code == 0, f"Expected exit 0, got {exit_code}. Output: {stdout}"
    assert "All checks passed" in stdout or "passed" in stdout.lower()


def test_doctor_fails_when_spine_dir_missing(tmp_path: Path) -> None:
    """doctor with missing .spine/ directory reports error."""
    make_git_repo(tmp_path)

    exit_code, stdout, _ = run_doctor(tmp_path)
    assert exit_code == 1, f"Expected exit 1, got {exit_code}. Output: {stdout}"
    assert ".spine" in stdout or "does not exist" in stdout.lower()


def test_doctor_fails_on_corrupted_mission_yaml(tmp_path: Path) -> None:
    """doctor with corrupted mission.yaml reports YAML parse error."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    # Corrupt mission.yaml
    mission_path = tmp_path / ".spine" / "mission.yaml"
    mission_path.write_text("INVALID YAML: [}\n  broken: ", encoding="utf-8")

    exit_code, stdout, _ = run_doctor(tmp_path)
    assert exit_code == 1, f"Expected exit 1, got {exit_code}. Output: {stdout}"
    assert "mission.yaml" in stdout.lower() or "yaml" in stdout.lower()
    # Should indicate parse error
    assert "parse" in stdout.lower() or "error" in stdout.lower()


def test_doctor_fails_on_corrupted_constraints_yaml(tmp_path: Path) -> None:
    """doctor with corrupted constraints.yaml reports YAML parse error."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    # Corrupt constraints.yaml
    constraints_path = tmp_path / ".spine" / "constraints.yaml"
    constraints_path.write_text("INVALID YAML: [}\n  broken: ", encoding="utf-8")

    exit_code, stdout, _ = run_doctor(tmp_path)
    assert exit_code == 1, f"Expected exit 1, got {exit_code}. Output: {stdout}"
    assert "constraints.yaml" in stdout.lower() or "yaml" in stdout.lower()
    # Should indicate parse error
    assert "parse" in stdout.lower() or "error" in stdout.lower()


def test_doctor_fails_on_corrupted_jsonl_file(tmp_path: Path) -> None:
    """doctor with corrupted JSONL file reports JSON parse error."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    # Corrupt evidence.jsonl
    evidence_path = tmp_path / ".spine" / "evidence.jsonl"
    evidence_path.write_text('{"kind": "test"}\n{"broken": json\n', encoding="utf-8")

    exit_code, stdout, _ = run_doctor(tmp_path)
    assert exit_code == 1, f"Expected exit 1, got {exit_code}. Output: {stdout}"
    assert "evidence.jsonl" in stdout.lower() or "json" in stdout.lower()
    # Should indicate parse error
    assert "parse" in stdout.lower() or "error" in stdout.lower()


def test_doctor_fails_when_agents_md_missing(tmp_path: Path) -> None:
    """doctor with missing AGENTS.md reports error."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    # Remove AGENTS.md
    (tmp_path / "AGENTS.md").unlink()

    exit_code, stdout, _ = run_doctor(tmp_path)
    assert exit_code == 1, f"Expected exit 1, got {exit_code}. Output: {stdout}"
    assert "AGENTS.md" in stdout or "missing" in stdout.lower()


def test_doctor_fails_when_claude_settings_missing(tmp_path: Path) -> None:
    """doctor with missing .claude/settings.json reports error."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    # Remove .claude/settings.json
    settings_path = tmp_path / ".claude" / "settings.json"
    settings_path.unlink()

    exit_code, stdout, _ = run_doctor(tmp_path)
    assert exit_code == 1, f"Expected exit 1, got {exit_code}. Output: {stdout}"
    assert "settings.json" in stdout or ".claude" in stdout.lower() or "missing" in stdout.lower()


# ---------------------------------------------------------------------------
# Issue #18: error quality — actionable messages and no absolute paths
# ---------------------------------------------------------------------------


def test_doctor_missing_spine_dir_error_mentions_init(tmp_path: Path) -> None:
    """doctor with missing .spine/ tells operator to run 'spine init'."""
    make_git_repo(tmp_path)

    exit_code, stdout, _ = run_doctor(tmp_path)
    assert exit_code == 1
    assert "spine init" in stdout


def test_doctor_contract_error_uses_relative_path(tmp_path: Path) -> None:
    """doctor contract file errors show relative paths (not absolute paths) in file column."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    # Remove AGENTS.md
    (tmp_path / "AGENTS.md").unlink()

    exit_code, stdout, _ = run_doctor(tmp_path)
    assert exit_code == 1
    assert "AGENTS.md" in stdout
    # The file column should show just "AGENTS.md", not "/tmp/.../AGENTS.md".
    # The context line ("repo: /path/...") may contain the absolute path, but
    # the error row's file field must be a relative name.
    abs_agents_path = str(tmp_path / "AGENTS.md")
    assert abs_agents_path not in stdout, (
        f"Doctor file column should show relative 'AGENTS.md', not absolute '{abs_agents_path}'"
    )


def test_doctor_contract_error_actionable(tmp_path: Path) -> None:
    """doctor contract file error tells operator how to fix it."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    (tmp_path / "AGENTS.md").unlink()

    exit_code, stdout, _ = run_doctor(tmp_path)
    assert exit_code == 1
    # Should suggest running spine init
    assert "spine init" in stdout


# ---------------------------------------------------------------------------
# Blank mission field warnings
# ---------------------------------------------------------------------------


def test_doctor_warns_on_blank_mission_fields(tmp_path: Path) -> None:
    """doctor warns (but still passes) when critical mission fields are blank after init."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_doctor(tmp_path)
    # Warnings do not fail doctor — exit code should still be 0
    assert exit_code == 0, f"Expected exit 0 (warnings only), got {exit_code}. Output: {stdout}"
    # Should mention the blank fields
    assert "target_user" in stdout
    assert "user_problem" in stdout
    assert "one_sentence_promise" in stdout
    # Should suggest how to fix
    assert "spine mission set" in stdout


def test_doctor_no_blank_field_warn_when_mission_complete(tmp_path: Path) -> None:
    """doctor does not warn about blank fields when all critical mission fields are set."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    # Write a fully-populated mission.yaml
    mission_path = tmp_path / ".spine" / "mission.yaml"
    mission_path.write_text(
        "version: 1\n"
        "id: mission-0001\n"
        "title: Test Mission\n"
        "status: active\n"
        "target_user: solo developers\n"
        "user_problem: no governance layer for AI agents\n"
        "one_sentence_promise: Keep agents on target\n"
        "success_metric:\n"
        "  type: milestone\n"
        "  value: 100 users\n"
        "deadline_window_days: 42\n"
        "review_cadence: weekly\n"
        "preferred_runtimes: []\n"
        "preferred_models: {}\n"
        "allowed_scope: []\n"
        "forbidden_expansions: []\n"
        "proof_requirements: []\n"
        "kill_conditions: []\n"
        "created_at: '2026-01-01T00:00:00+00:00'\n"
        "updated_at: '2026-01-01T00:00:00+00:00'\n",
        encoding="utf-8",
    )

    exit_code, stdout, _ = run_doctor(tmp_path)
    assert exit_code == 0, f"Expected exit 0, got {exit_code}. Output: {stdout}"
    # Should NOT warn about blank mission fields
    assert "Mission fields are blank" not in stdout
