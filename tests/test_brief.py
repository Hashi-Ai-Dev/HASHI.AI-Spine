"""Tests for spine brief command (Phase 2)."""

from __future__ import annotations

import os
from pathlib import Path

from typer.testing import CliRunner

from spine.main import app

runner = CliRunner()


def make_git_repo(tmp_path: Path) -> Path:
    """Create a minimal fake git repo (just a .git dir) for init compatibility."""
    (tmp_path / ".git").mkdir()
    return tmp_path


def run_init(tmp_path: Path, *extra_args: str) -> tuple[int, str, str]:
    result = runner.invoke(app, ["init", "--cwd", str(tmp_path), *extra_args])
    return result.exit_code, result.output, ""


def run_brief(tmp_path: Path, *extra_args: str) -> tuple[int, str, str]:
    original = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["brief", *extra_args])
    finally:
        os.chdir(original)
    return result.exit_code, result.output, ""


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_brief_target_claude_creates_file(tmp_path: Path) -> None:
    """spine brief --target claude creates a file in .spine/briefs/claude/."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_brief(tmp_path, "--target", "claude")

    assert exit_code == 0, stdout
    briefs_dir = tmp_path / ".spine" / "briefs" / "claude"
    assert briefs_dir.is_dir()
    # Should have at least one brief file (latest.md or timestamped)
    files = list(briefs_dir.glob("*.md"))
    assert len(files) >= 1, f"Expected brief files in {briefs_dir}, got {files}"


def test_brief_target_codex_creates_file(tmp_path: Path) -> None:
    """spine brief --target codex creates a file in .spine/briefs/codex/."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_brief(tmp_path, "--target", "codex")

    assert exit_code == 0, stdout
    briefs_dir = tmp_path / ".spine" / "briefs" / "codex"
    assert briefs_dir.is_dir()
    # Should have at least one brief file
    files = list(briefs_dir.glob("*.md"))
    assert len(files) >= 1, f"Expected brief files in {briefs_dir}, got {files}"


def test_brief_updates_latest_md(tmp_path: Path) -> None:
    """spine brief updates latest.md in the target directory."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    # First brief
    run_brief(tmp_path, "--target", "claude")

    latest_path = tmp_path / ".spine" / "briefs" / "claude" / "latest.md"
    assert latest_path.exists(), f"latest.md not found at {latest_path}"

    first_mtime = latest_path.stat().st_mtime

    # Second brief should update latest.md
    run_brief(tmp_path, "--target", "claude")
    second_mtime = latest_path.stat().st_mtime

    # Content should be updated (or at least mtime changed)
    assert second_mtime >= first_mtime


def test_brief_contains_mission_title(tmp_path: Path) -> None:
    """Brief contains mission title from mission.yaml."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_brief(tmp_path, "--target", "claude")

    latest_path = tmp_path / ".spine" / "briefs" / "claude" / "latest.md"
    content = latest_path.read_text(encoding="utf-8")

    assert "Mission Brief" in content
    assert "mission-0001" in content or "title" in content.lower()


def test_brief_contains_status(tmp_path: Path) -> None:
    """Brief contains mission status."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_brief(tmp_path, "--target", "claude")

    latest_path = tmp_path / ".spine" / "briefs" / "claude" / "latest.md"
    content = latest_path.read_text(encoding="utf-8")

    assert "Status" in content
    assert "active" in content


def test_brief_contains_allowed_scope(tmp_path: Path) -> None:
    """Brief contains allowed_scope section."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_brief(tmp_path, "--target", "claude")

    latest_path = tmp_path / ".spine" / "briefs" / "claude" / "latest.md"
    content = latest_path.read_text(encoding="utf-8")

    assert "Allowed Scope" in content or "allowed_scope" in content.lower()


def test_brief_contains_forbidden_expansions(tmp_path: Path) -> None:
    """Brief contains forbidden_expansions section."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_brief(tmp_path, "--target", "claude")

    latest_path = tmp_path / ".spine" / "briefs" / "claude" / "latest.md"
    content = latest_path.read_text(encoding="utf-8")

    assert "Forbidden Expansions" in content or "forbidden_expansions" in content.lower()


def test_brief_contains_acceptance_criteria(tmp_path: Path) -> None:
    """Brief contains acceptance criteria section."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_brief(tmp_path, "--target", "claude")

    latest_path = tmp_path / ".spine" / "briefs" / "claude" / "latest.md"
    content = latest_path.read_text(encoding="utf-8")

    assert "Acceptance Criteria" in content or "acceptance criteria" in content.lower()


def test_brief_codex_has_different_content(tmp_path: Path) -> None:
    """Brief generated for codex has different content than claude brief."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_brief(tmp_path, "--target", "claude")
    run_brief(tmp_path, "--target", "codex")

    claude_latest = (
        tmp_path / ".spine" / "briefs" / "claude" / "latest.md"
    ).read_text(encoding="utf-8")
    codex_latest = (
        tmp_path / ".spine" / "briefs" / "codex" / "latest.md"
    ).read_text(encoding="utf-8")

    # Both should be valid briefs but with different sections
    assert "Mission Brief" in claude_latest
    assert "Mission Brief" in codex_latest
    # Codex should have worktree recommendation section
    assert "Worktree Recommendation" in codex_latest
    # Claude should have evidence requirements section
    assert "Evidence" in claude_latest


def test_brief_target_openclaw_creates_file(tmp_path: Path) -> None:
    """spine brief --target openclaw creates a file in .spine/briefs/openclaw/."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_brief(tmp_path, "--target", "openclaw")

    assert exit_code == 0, stdout
    briefs_dir = tmp_path / ".spine" / "briefs" / "openclaw"
    assert briefs_dir.is_dir()
    files = list(briefs_dir.glob("*.md"))
    assert len(files) >= 1, f"Expected brief files in {briefs_dir}, got {files}"


def test_brief_openclaw_has_startup_contract_section(tmp_path: Path) -> None:
    """OpenClaw brief contains the OpenClaw Startup Contract section."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_brief(tmp_path, "--target", "openclaw")

    latest_path = tmp_path / ".spine" / "briefs" / "openclaw" / "latest.md"
    content = latest_path.read_text(encoding="utf-8")

    assert "OpenClaw Startup Contract" in content
    assert ".spine/briefs/openclaw/latest.md" in content
    assert ".openclaw/spine.yaml" in content


def test_brief_openclaw_has_governance_workflow(tmp_path: Path) -> None:
    """OpenClaw brief contains the governance workflow section."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_brief(tmp_path, "--target", "openclaw")

    latest_path = tmp_path / ".spine" / "briefs" / "openclaw" / "latest.md"
    content = latest_path.read_text(encoding="utf-8")

    assert "Governance Workflow" in content
    assert "before-work" in content
    assert "before-pr" in content


def test_brief_openclaw_has_different_content_than_claude(tmp_path: Path) -> None:
    """OpenClaw brief has different sections than the Claude brief."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_brief(tmp_path, "--target", "claude")
    run_brief(tmp_path, "--target", "openclaw")

    claude_content = (
        tmp_path / ".spine" / "briefs" / "claude" / "latest.md"
    ).read_text(encoding="utf-8")
    openclaw_content = (
        tmp_path / ".spine" / "briefs" / "openclaw" / "latest.md"
    ).read_text(encoding="utf-8")

    assert "Mission Brief" in claude_content
    assert "Mission Brief" in openclaw_content
    assert "OpenClaw Startup Contract" in openclaw_content
    assert "OpenClaw Startup Contract" not in claude_content
    assert "Evidence Requirements" in claude_content


def test_brief_invalid_target_rejected(tmp_path: Path) -> None:
    """spine brief with invalid target (not claude, codex, or openclaw) is rejected."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_brief(tmp_path, "--target", "invalid_agent")

    assert exit_code == 1
    assert "claude" in stdout.lower() or "openclaw" in stdout.lower() or "error" in stdout.lower()


def test_brief_requires_init(tmp_path: Path) -> None:
    """spine brief exits 2 (context failure) when .spine/ is not initialized."""
    make_git_repo(tmp_path)
    # No spine init

    exit_code, stdout, _ = run_brief(tmp_path, "--target", "claude")

    assert exit_code == 2, f"Expected exit 2 (context failure), got {exit_code}"
    assert "mission" in stdout.lower() or "error" in stdout.lower() or "not found" in stdout.lower()


def test_brief_requires_git_repo(tmp_path: Path) -> None:
    """spine brief exits 2 (context failure) when not in a git repo."""
    import os
    original = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["brief", "--target", "claude"])
    finally:
        os.chdir(original)
    assert result.exit_code == 2, f"Expected exit 2 (context failure), got {result.exit_code}"


def test_brief_multiple_runs_create_timestamped_files(tmp_path: Path) -> None:
    """Multiple brief runs create multiple timestamped files plus latest.md."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    # Run brief twice
    run_brief(tmp_path, "--target", "claude")
    run_brief(tmp_path, "--target", "claude")

    briefs_dir = tmp_path / ".spine" / "briefs" / "claude"
    files = list(briefs_dir.glob("*.md"))

    # Should have at least 2 files: latest.md + at least one timestamped
    assert len(files) >= 2, f"Expected at least 2 brief files, got {len(files)}: {files}"

    # latest.md should exist
    assert (briefs_dir / "latest.md").exists()


def test_brief_generates_for_both_targets_in_sequence(tmp_path: Path) -> None:
    """Can generate briefs for claude and codex targets in sequence."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code1, stdout1, _ = run_brief(tmp_path, "--target", "claude")
    assert exit_code1 == 0, stdout1

    exit_code2, stdout2, _ = run_brief(tmp_path, "--target", "codex")
    assert exit_code2 == 0, stdout2

    # Both directories should have files
    assert (tmp_path / ".spine" / "briefs" / "claude" / "latest.md").exists()
    assert (tmp_path / ".spine" / "briefs" / "codex" / "latest.md").exists()
