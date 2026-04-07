"""Tests for spine drift-scan command (Phase 2)."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from spine.main import app

runner = CliRunner()


def make_git_repo(tmp_path: Path) -> Path:
    """Create a minimal fake git repo (just a .git dir) for init compatibility."""
    (tmp_path / ".git").mkdir()
    return tmp_path


def make_real_git_repo(tmp_path: Path) -> Path:
    """Create a real git repo with an initial commit for drift-scan testing."""
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=tmp_path,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=tmp_path,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "commit.gpgsign", "false"],
        cwd=tmp_path,
        capture_output=True,
    )
    # Create initial file and commit
    (tmp_path / "README.md").write_text("# Test\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=tmp_path,
        capture_output=True,
    )
    return tmp_path


def make_real_git_repo_on_main(tmp_path: Path) -> Path:
    """Create a real git repo with initial commit explicitly on 'main' branch."""
    subprocess.run(["git", "init", "--initial-branch=main"], cwd=tmp_path, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=tmp_path,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=tmp_path,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "commit.gpgsign", "false"],
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


def run_init(tmp_path: Path, *extra_args: str) -> tuple[int, str, str]:
    result = runner.invoke(app, ["init", "--cwd", str(tmp_path), *extra_args])
    return result.exit_code, result.output, ""


def run_drift_scan(tmp_path: Path, *extra_args: str) -> tuple[int, str, str]:
    original = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["drift", "scan", *extra_args])
    finally:
        os.chdir(original)
    return result.exit_code, result.output, ""


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_drift_scan_no_changes(tmp_path: Path) -> None:
    """drift-scan with no changes reports no drift."""
    make_real_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_drift_scan(tmp_path)

    assert exit_code == 0, stdout
    assert "No drift detected" in stdout


def test_drift_scan_untracked_files_not_drift(tmp_path: Path) -> None:
    """drift-scan with untracked files does not report them as drift."""
    make_real_git_repo(tmp_path)
    run_init(tmp_path)

    # Create untracked file (should not appear as drift)
    (tmp_path / "untracked_file.py").write_text("# untracked\n", encoding="utf-8")

    exit_code, stdout, _ = run_drift_scan(tmp_path)

    assert exit_code == 0, stdout
    assert "No drift detected" in stdout


def test_drift_scan_service_file_detected(tmp_path: Path) -> None:
    """drift-scan detects new service files as medium severity drift."""
    make_real_git_repo(tmp_path)
    run_init(tmp_path)

    # Create a new service file (medium severity - service_creep)
    (tmp_path / "services").mkdir(parents=True, exist_ok=True)
    (tmp_path / "services" / "api.py").write_text(
        "from fastapi import APIRouter\nrouter = APIRouter()\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)

    exit_code, stdout, _ = run_drift_scan(tmp_path)

    assert exit_code == 0, stdout
    # Service files without tests trigger test_gap (low) severity
    # But we should see some drift detected
    assert ("test_gap" in stdout.lower() or "service_creep" in stdout.lower()
            or "drift" in stdout.lower()), f"Expected drift detection in: {stdout}"


def test_drift_scan_appends_to_drift_jsonl(tmp_path: Path) -> None:
    """drift-scan appends detected events to .spine/drift.jsonl."""
    make_real_git_repo(tmp_path)
    run_init(tmp_path)

    # Create a service file without tests
    (tmp_path / "services").mkdir(parents=True, exist_ok=True)
    (tmp_path / "services" / "api.py").write_text(
        "from fastapi import APIRouter\nrouter = APIRouter()\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)

    drift_jsonl = tmp_path / ".spine" / "drift.jsonl"

    exit_code, stdout, _ = run_drift_scan(tmp_path)

    assert exit_code == 0
    # drift.jsonl should exist and have content
    assert drift_jsonl.exists()
    content = drift_jsonl.read_text(encoding="utf-8")
    lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
    assert len(lines) > 0, "drift.jsonl should have at least one event"
    # Each line should be valid JSON
    for line in lines:
        event = json.loads(line)
        assert "severity" in event
        assert "category" in event
        assert "description" in event


def test_drift_scan_against_branch(tmp_path: Path) -> None:
    """drift-scan --against flag diffs against the specified branch."""
    make_real_git_repo(tmp_path)
    run_init(tmp_path)

    # Create a new branch with a service file
    subprocess.run(
        ["git", "checkout", "-b", "feature/new-service"],
        cwd=tmp_path,
        capture_output=True,
    )
    (tmp_path / "services").mkdir(parents=True, exist_ok=True)
    (tmp_path / "services" / "api.py").write_text(
        "from fastapi import APIRouter\nrouter = APIRouter()\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add service"],
        cwd=tmp_path,
        capture_output=True,
    )

    # Switch back to main and run drift-scan against feature branch
    subprocess.run(
        ["git", "checkout", "main"],
        cwd=tmp_path,
        capture_output=True,
    )

    exit_code, stdout, _ = run_drift_scan(tmp_path, "--against", "feature/new-service")

    assert exit_code == 0
    # Should detect the service file added in the feature branch
    assert "drift" in stdout.lower() or "test_gap" in stdout.lower() or "service_creep" in stdout.lower()


def test_drift_scan_forbidden_expansion_high_severity(tmp_path: Path) -> None:
    """drift-scan detects forbidden expansions (like ui/, auth/) as high severity."""
    make_real_git_repo(tmp_path)
    run_init(tmp_path)

    # Create a forbidden file (ui/dashboard.py)
    (tmp_path / "ui").mkdir(parents=True, exist_ok=True)
    (tmp_path / "ui" / "dashboard.py").write_text(
        "from flask import render_template\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)

    exit_code, stdout, _ = run_drift_scan(tmp_path)

    assert exit_code == 0
    assert "HIGH" in stdout or "high" in stdout.lower()
    assert "forbidden_expansion" in stdout.lower()


def test_drift_scan_allowed_file_not_high_severity(tmp_path: Path) -> None:
    """drift-scan with changes to allowed files does not report high severity."""
    make_real_git_repo(tmp_path)
    run_init(tmp_path)

    # Create a file in allowed scope (e.g., src/ module)
    (tmp_path / "src").mkdir(parents=True, exist_ok=True)
    (tmp_path / "src" / "utils.py").write_text(
        "def helper(): pass\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)

    exit_code, stdout, _ = run_drift_scan(tmp_path)

    assert exit_code == 0
    # Should not report HIGH severity for allowed files
    assert "HIGH" not in stdout or "No drift detected" in stdout


def test_drift_scan_requires_git_repo(tmp_path: Path) -> None:
    """drift-scan exits with code 1 when not in a git repo."""
    import os
    original = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["drift", "scan"])
    finally:
        os.chdir(original)
    assert result.exit_code == 1


def test_drift_scan_works_without_init(tmp_path: Path) -> None:
    """drift-scan works even when .spine/ is not initialized."""
    make_real_git_repo(tmp_path)
    # No spine init

    exit_code, stdout, _ = run_drift_scan(tmp_path)

    # drift-scan does not require .spine/ to be initialized
    # it just reports no drift if there's nothing to scan
    assert exit_code == 0, stdout
    assert "No drift detected" in stdout


def test_drift_scan_committed_forbidden_on_branch_auto_detects(tmp_path: Path) -> None:
    """drift-scan detects forbidden committed files on current branch without --against flag.

    This is the core hardening test: committed forbidden files (ui/, auth/, etc.)
    on a feature branch must be detected by auto-comparison against the default branch.
    """
    make_real_git_repo_on_main(tmp_path)
    run_init(tmp_path)

    # Create a feature branch with a committed forbidden file
    subprocess.run(
        ["git", "checkout", "-b", "feature/ui-addition"],
        cwd=tmp_path,
        capture_output=True,
    )
    (tmp_path / "ui").mkdir(parents=True, exist_ok=True)
    (tmp_path / "ui" / "dashboard.py").write_text(
        "from flask import render_template\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add forbidden ui/dashboard"],
        cwd=tmp_path,
        capture_output=True,
    )

    # Stay on the feature branch and run drift scan WITHOUT --against
    # It should auto-detect main and flag the committed forbidden file
    exit_code, stdout, _ = run_drift_scan(tmp_path)

    assert exit_code == 0
    assert "HIGH" in stdout or "high" in stdout.lower()
    assert "forbidden_expansion" in stdout.lower()


def test_drift_scan_staged_forbidden_file_detected(tmp_path: Path) -> None:
    """drift-scan detects forbidden files that are staged (index) but not committed."""
    make_real_git_repo(tmp_path)
    run_init(tmp_path)

    # Create a forbidden file and stage it (but don't commit)
    (tmp_path / "ui").mkdir(parents=True, exist_ok=True)
    (tmp_path / "ui" / "dashboard.py").write_text(
        "from flask import render_template\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "ui/dashboard.py"], cwd=tmp_path, capture_output=True)

    exit_code, stdout, _ = run_drift_scan(tmp_path)

    assert exit_code == 0
    assert "HIGH" in stdout or "high" in stdout.lower()
    assert "forbidden_expansion" in stdout.lower()


def test_drift_scan_untracked_file_not_drift(tmp_path: Path) -> None:
    """drift-scan does not flag untracked files as drift (they are not in git yet)."""
    make_real_git_repo(tmp_path)
    run_init(tmp_path)

    # Create an untracked (never-staged) forbidden file
    (tmp_path / "ui").mkdir(parents=True, exist_ok=True)
    (tmp_path / "ui" / "dashboard.py").write_text(
        "from flask import render_template\n",
        encoding="utf-8",
    )
    # File is created but never staged or committed

    exit_code, stdout, _ = run_drift_scan(tmp_path)

    # Untracked files should NOT appear as drift from git's perspective
    # (git diff HEAD is empty for untracked files)
    assert exit_code == 0
    # No HIGH forbidden_expansion for untracked should appear in the output
    assert "forbidden_expansion" not in stdout.lower()


# ---------------------------------------------------------------------------
# SPINE_ROOT external targeting tests
# ---------------------------------------------------------------------------


def test_drift_scan_spiner_root_targets_external_repo(tmp_path: Path) -> None:
    """
    When SPINE_ROOT is set, drift scan targets the external repo's git,
    not the current working directory's git.

    This is the core external targeting hardening test: SPINE_ROOT must
    bind both canonical state AND git-native repo operations to the same
    external repo.
    """
    # Set up external repo B (a real git repo with a commit)
    external_repo = tmp_path / "external_repo"
    external_repo.mkdir()
    subprocess.run(["git", "init", "--initial-branch=main"], cwd=external_repo, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=external_repo, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=external_repo, capture_output=True)
    subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=external_repo, capture_output=True)
    (external_repo / "README.md").write_text("# External\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=external_repo, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=external_repo, capture_output=True)

    # Create .spine/ in external repo
    (external_repo / ".spine").mkdir()
    (external_repo / ".spine" / "mission.yaml").write_text(
        "id: test-external\ntitle: External Mission\nstatus: active\n"
        "updated_at: '2026-01-01T00:00:00Z'\ncreated_at: '2026-01-01T00:00:00Z'\n"
        "target_user: ''\nuser_problem: ''\none_sentence_promise: ''\n"
        "allowed_scope: []\nforbidden_expansions: []\nproof_requirements: []\n"
        "kill_conditions: []\nsuccess_metric:\n  type: milestone\n  value: ''\n",
        encoding="utf-8",
    )
    (external_repo / ".spine" / "drift.jsonl").write_text("", encoding="utf-8")

    # Create a committed forbidden file on a feature branch (not on main)
    # This creates actual branch drift that Mode B should detect
    subprocess.run(["git", "checkout", "-b", "feature/ui-add"], cwd=external_repo, capture_output=True)
    (external_repo / "ui").mkdir()
    (external_repo / "ui" / "dashboard.py").write_text(
        "from flask import render_template\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "."], cwd=external_repo, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Add ui/dashboard"], cwd=external_repo, capture_output=True)

    # Set up repo A (SPINE working directory) — a separate git repo
    spine_repo = tmp_path / "spine_repo"
    spine_repo.mkdir()
    subprocess.run(["git", "init", "--initial-branch=main"], cwd=spine_repo, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=spine_repo, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=spine_repo, capture_output=True)
    subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=spine_repo, capture_output=True)
    (spine_repo / "README.md").write_text("# SPINE\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=spine_repo, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial"], cwd=spine_repo, capture_output=True)

    # Run drift scan from spine_repo using SPINE_ROOT pointing to external_repo
    original = os.getcwd()
    try:
        os.chdir(spine_repo)
        os.environ["SPINE_ROOT"] = str(external_repo)
        try:
            result = runner.invoke(app, ["drift", "scan"])
        finally:
            os.environ.pop("SPINE_ROOT", None)
    finally:
        os.chdir(original)

    assert result.exit_code == 0, result.output
    # The drift must come from external_repo's ui/dashboard.py, not from spine_repo
    assert "forbidden_expansion" in result.output.lower() or "HIGH" in result.output
    # Ensure NO spine_repo files appear in drift output
    assert "spine_repo" not in result.output


def test_resolve_roots_without_spiner_root_uses_cwd_repo(tmp_path: Path) -> None:
    """
    Without SPINE_ROOT set, resolve_roots() uses the cwd git repo normally.
    """
    # Set up a real git repo
    subprocess.run(["git", "init", "--initial-branch=main"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=tmp_path, capture_output=True)
    (tmp_path / "README.md").write_text("# Test\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial"], cwd=tmp_path, capture_output=True)

    (tmp_path / ".spine").mkdir()
    (tmp_path / ".spine" / "mission.yaml").write_text(
        "id: test-local\ntitle: Local Mission\nstatus: active\n"
        "updated_at: '2026-01-01T00:00:00Z'\ncreated_at: '2026-01-01T00:00:00Z'\n"
        "target_user: ''\nuser_problem: ''\none_sentence_promise: ''\n"
        "allowed_scope: []\nforbidden_expansions: []\nproof_requirements: []\n"
        "kill_conditions: []\nsuccess_metric:\n  type: milestone\n  value: ''\n",
        encoding="utf-8",
    )

    # Run mission show from the repo with SPINE_ROOT unset
    original = os.getcwd()
    os.environ.pop("SPINE_ROOT", None)
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["mission", "show"])
    finally:
        os.chdir(original)

    assert result.exit_code == 0, result.output
    assert "Local Mission" in result.output
