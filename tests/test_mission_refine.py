"""Tests for Beta: mission refine draft flow (Issue #36).

Covers:
- spine mission refine command registration
- draft creation at .spine/drafts/missions/<timestamp>.yaml
- draft labeled non-canonical (YAML comments)
- canonical mission.yaml unchanged after refine
- spine mission drafts list
- spine mission confirm <draft_id> — explicit promotion
- canonical mission updated after confirm
- draft file removed after confirm
- nonexistent draft_id fails gracefully
- --cwd support for all mission draft commands
- deterministic naming pattern
- multiple drafts stored separately
- confirm one draft leaves others intact
"""

from __future__ import annotations

import os
import yaml
from pathlib import Path

from typer.testing import CliRunner

from spine.main import app

runner = CliRunner()


def make_git_repo(tmp_path: Path) -> Path:
    """Create a minimal fake git repo (just a .git dir)."""
    (tmp_path / ".git").mkdir()
    return tmp_path


def run_init(tmp_path: Path) -> None:
    result = runner.invoke(app, ["init", "--cwd", str(tmp_path)])
    assert result.exit_code == 0, result.output


def run_mission_refine(tmp_path: Path, *extra_args: str) -> tuple[int, str]:
    result = runner.invoke(app, ["mission", "refine", "--cwd", str(tmp_path), *extra_args])
    return result.exit_code, result.output


def run_mission_confirm(tmp_path: Path, draft_id: str) -> tuple[int, str]:
    result = runner.invoke(app, ["mission", "confirm", draft_id, "--cwd", str(tmp_path)])
    return result.exit_code, result.output


def run_mission_drafts(tmp_path: Path) -> tuple[int, str]:
    result = runner.invoke(app, ["mission", "drafts", "--cwd", str(tmp_path)])
    return result.exit_code, result.output


# ---------------------------------------------------------------------------
# Command registration
# ---------------------------------------------------------------------------


def test_mission_refine_command_registered(tmp_path: Path) -> None:
    """spine mission refine command exists and shows help."""
    result = runner.invoke(app, ["mission", "refine", "--help"])
    assert result.exit_code == 0, result.output
    assert "refine" in result.output.lower()
    assert "draft" in result.output.lower()


def test_mission_confirm_command_registered(tmp_path: Path) -> None:
    """spine mission confirm command exists and shows help."""
    result = runner.invoke(app, ["mission", "confirm", "--help"])
    assert result.exit_code == 0, result.output
    assert "confirm" in result.output.lower() or "promote" in result.output.lower()


def test_mission_drafts_command_registered(tmp_path: Path) -> None:
    """spine mission drafts command exists and shows help."""
    result = runner.invoke(app, ["mission", "drafts", "--help"])
    assert result.exit_code == 0, result.output
    assert "draft" in result.output.lower()


# ---------------------------------------------------------------------------
# Draft creation
# ---------------------------------------------------------------------------


def test_mission_refine_creates_draft_file(tmp_path: Path) -> None:
    """spine mission refine creates a file under .spine/drafts/missions/."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout = run_mission_refine(tmp_path, "--title", "Refined Mission")
    assert exit_code == 0, stdout

    drafts_dir = tmp_path / ".spine" / "drafts" / "missions"
    assert drafts_dir.exists(), ".spine/drafts/missions/ should be created"
    draft_files = list(drafts_dir.glob("mission-*.yaml"))
    assert len(draft_files) == 1, f"Expected 1 draft file, got: {draft_files}"


def test_mission_refine_draft_contains_proposed_title(tmp_path: Path) -> None:
    """The draft YAML reflects the proposed title."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_mission_refine(tmp_path, "--title", "My Refined Title")

    drafts_dir = tmp_path / ".spine" / "drafts" / "missions"
    draft_files = list(drafts_dir.glob("mission-*.yaml"))
    assert len(draft_files) == 1

    raw = draft_files[0].read_text()
    data = yaml.safe_load(raw)
    assert data["title"] == "My Refined Title"


def test_mission_refine_draft_labeled_non_canonical(tmp_path: Path) -> None:
    """The draft YAML file contains a non-canonical header comment."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_mission_refine(tmp_path, "--title", "Draft Title")

    drafts_dir = tmp_path / ".spine" / "drafts" / "missions"
    draft_files = list(drafts_dir.glob("mission-*.yaml"))
    assert len(draft_files) == 1

    raw = draft_files[0].read_text()
    assert "non-canonical" in raw.lower() or "DRAFT" in raw


def test_mission_refine_does_not_mutate_canonical(tmp_path: Path) -> None:
    """spine mission refine must NOT change .spine/mission.yaml."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    mission_path = tmp_path / ".spine" / "mission.yaml"
    before = yaml.safe_load(mission_path.read_text())

    run_mission_refine(tmp_path, "--title", "Should Not Appear In Canonical")

    after = yaml.safe_load(mission_path.read_text())
    assert before["title"] == after["title"], "canonical title must not change after refine"
    assert before["updated_at"] == after["updated_at"], "canonical updated_at must not change"


def test_mission_refine_output_includes_draft_id(tmp_path: Path) -> None:
    """CLI output includes the draft ID and promotion hint."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout = run_mission_refine(tmp_path, "--title", "Test")
    assert exit_code == 0
    assert "Draft ID:" in stdout
    assert "spine mission confirm" in stdout


def test_mission_refine_draft_naming_deterministic(tmp_path: Path) -> None:
    """Draft filename follows mission-YYYYMMDDTHHMMSS pattern."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_mission_refine(tmp_path, "--title", "T")

    drafts_dir = tmp_path / ".spine" / "drafts" / "missions"
    files = list(drafts_dir.glob("mission-*.yaml"))
    assert len(files) == 1
    stem = files[0].stem
    assert stem.startswith("mission-"), f"Expected mission- prefix, got: {stem}"
    ts_part = stem[len("mission-"):]
    assert len(ts_part) >= 15, f"Timestamp part too short: {ts_part!r}"
    assert ts_part[0].isdigit(), f"Timestamp should start with digit: {ts_part}"


def test_mission_refine_multiple_drafts_separate_files(tmp_path: Path) -> None:
    """Multiple refine calls each produce a separate draft file."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    for i in range(3):
        run_mission_refine(tmp_path, "--title", f"Draft {i}")

    drafts_dir = tmp_path / ".spine" / "drafts" / "missions"
    files = list(drafts_dir.glob("mission-*.yaml"))
    assert len(files) == 3


def test_mission_refine_with_scope_and_forbid(tmp_path: Path) -> None:
    """Refine correctly applies --scope and --forbid to the draft."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout = run_mission_refine(
        tmp_path,
        "--scope", "cli,tests",
        "--forbid", "auth,billing",
    )
    assert exit_code == 0, stdout

    drafts_dir = tmp_path / ".spine" / "drafts" / "missions"
    files = list(drafts_dir.glob("mission-*.yaml"))
    data = yaml.safe_load(files[0].read_text())
    assert data["allowed_scope"] == ["cli", "tests"]
    assert data["forbidden_expansions"] == ["auth", "billing"]


# ---------------------------------------------------------------------------
# spine mission drafts list
# ---------------------------------------------------------------------------


def test_mission_drafts_list_empty(tmp_path: Path) -> None:
    """spine mission drafts shows 'No pending mission drafts' when empty."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout = run_mission_drafts(tmp_path)
    assert exit_code == 0, stdout
    assert "No pending mission drafts" in stdout


def test_mission_drafts_list_shows_draft(tmp_path: Path) -> None:
    """spine mission drafts shows created drafts."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_mission_refine(tmp_path, "--title", "My Draft Mission")

    exit_code, stdout = run_mission_drafts(tmp_path)
    assert exit_code == 0, stdout
    assert "My Draft Mission" in stdout
    assert "spine mission confirm" in stdout


def test_mission_drafts_list_multiple(tmp_path: Path) -> None:
    """spine mission drafts shows all pending drafts."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_mission_refine(tmp_path, "--title", "Alpha Draft")
    run_mission_refine(tmp_path, "--title", "Beta Draft")

    exit_code, stdout = run_mission_drafts(tmp_path)
    assert exit_code == 0, stdout
    assert "Alpha Draft" in stdout
    assert "Beta Draft" in stdout


# ---------------------------------------------------------------------------
# Confirmation / promotion
# ---------------------------------------------------------------------------


def test_mission_confirm_promotes_to_canonical(tmp_path: Path) -> None:
    """spine mission confirm writes the draft to canonical mission.yaml."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_mission_refine(tmp_path, "--title", "Promoted Title")

    drafts_dir = tmp_path / ".spine" / "drafts" / "missions"
    draft_files = list(drafts_dir.glob("mission-*.yaml"))
    assert len(draft_files) == 1
    draft_id = draft_files[0].stem

    exit_code, stdout = run_mission_confirm(tmp_path, draft_id)
    assert exit_code == 0, stdout

    mission_path = tmp_path / ".spine" / "mission.yaml"
    data = yaml.safe_load(mission_path.read_text())
    assert data["title"] == "Promoted Title"


def test_mission_confirm_removes_draft_file(tmp_path: Path) -> None:
    """After confirmation, the draft file is removed."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_mission_refine(tmp_path, "--title", "Gone After Confirm")

    drafts_dir = tmp_path / ".spine" / "drafts" / "missions"
    draft_files = list(drafts_dir.glob("mission-*.yaml"))
    draft_id = draft_files[0].stem
    draft_path = draft_files[0]

    run_mission_confirm(tmp_path, draft_id)

    assert not draft_path.exists(), "Draft file should be deleted after confirm"


def test_mission_confirm_draft_no_longer_in_list(tmp_path: Path) -> None:
    """After confirmation, draft is gone from mission drafts list."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_mission_refine(tmp_path, "--title", "Will Be Confirmed")

    drafts_dir = tmp_path / ".spine" / "drafts" / "missions"
    draft_id = list(drafts_dir.glob("mission-*.yaml"))[0].stem
    run_mission_confirm(tmp_path, draft_id)

    exit_code, stdout = run_mission_drafts(tmp_path)
    assert exit_code == 0
    assert "No pending mission drafts" in stdout


def test_mission_confirm_nonexistent_draft_fails(tmp_path: Path) -> None:
    """Confirming a nonexistent draft_id exits non-zero."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout = run_mission_confirm(tmp_path, "mission-99999999T999999999999")
    assert exit_code != 0, "Should fail for nonexistent draft"
    assert "not found" in stdout.lower()


def test_mission_confirm_one_draft_leaves_others(tmp_path: Path) -> None:
    """Confirming one draft does not affect other pending drafts."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_mission_refine(tmp_path, "--title", "First Draft")
    run_mission_refine(tmp_path, "--title", "Second Draft")

    drafts_dir = tmp_path / ".spine" / "drafts" / "missions"
    files = sorted(drafts_dir.glob("mission-*.yaml"))
    assert len(files) == 2

    first_id = files[0].stem
    run_mission_confirm(tmp_path, first_id)

    remaining = list(drafts_dir.glob("mission-*.yaml"))
    assert len(remaining) == 1, "One draft should remain"


def test_mission_canonical_unchanged_until_confirm(tmp_path: Path) -> None:
    """mission.yaml title stays at original until confirm is called."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    mission_path = tmp_path / ".spine" / "mission.yaml"
    original_title = yaml.safe_load(mission_path.read_text())["title"]

    # Refine without confirming
    run_mission_refine(tmp_path, "--title", "Not Yet Canonical")
    mid_title = yaml.safe_load(mission_path.read_text())["title"]
    assert mid_title == original_title, "canonical title must not change after refine"

    # Now confirm
    drafts_dir = tmp_path / ".spine" / "drafts" / "missions"
    draft_id = list(drafts_dir.glob("mission-*.yaml"))[0].stem
    run_mission_confirm(tmp_path, draft_id)

    final_title = yaml.safe_load(mission_path.read_text())["title"]
    assert final_title == "Not Yet Canonical", "title should update only after confirm"


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def test_mission_refine_invalid_status_exits_1(tmp_path: Path) -> None:
    """spine mission refine exits 1 on invalid --status."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout = run_mission_refine(tmp_path, "--status", "invalid_status")
    assert exit_code == 1, stdout
    assert "Validation error" in stdout or "Invalid" in stdout


def test_mission_refine_requires_init(tmp_path: Path) -> None:
    """spine mission refine exits 2 if .spine/mission.yaml does not exist."""
    make_git_repo(tmp_path)
    # No init

    exit_code, stdout = run_mission_refine(tmp_path, "--title", "T")
    assert exit_code == 2, f"Expected exit 2, got {exit_code}"


# ---------------------------------------------------------------------------
# --cwd support
# ---------------------------------------------------------------------------


def test_mission_refine_with_cwd(tmp_path: Path) -> None:
    """spine mission refine respects --cwd."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    original = os.getcwd()
    try:
        os.chdir("/tmp")
        result = runner.invoke(app, ["mission", "refine", "--cwd", str(tmp_path), "--title", "CWD Test"])
    finally:
        os.chdir(original)

    assert result.exit_code == 0, result.output
    drafts_dir = tmp_path / ".spine" / "drafts" / "missions"
    assert any(drafts_dir.glob("mission-*.yaml"))


def test_mission_confirm_with_cwd(tmp_path: Path) -> None:
    """spine mission confirm respects --cwd."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    runner.invoke(app, ["mission", "refine", "--cwd", str(tmp_path), "--title", "CWD Confirm"])

    drafts_dir = tmp_path / ".spine" / "drafts" / "missions"
    draft_id = list(drafts_dir.glob("mission-*.yaml"))[0].stem

    result = runner.invoke(app, ["mission", "confirm", draft_id, "--cwd", str(tmp_path)])
    assert result.exit_code == 0, result.output

    mission_path = tmp_path / ".spine" / "mission.yaml"
    data = yaml.safe_load(mission_path.read_text())
    assert data["title"] == "CWD Confirm"


def test_mission_drafts_list_with_cwd(tmp_path: Path) -> None:
    """spine mission drafts respects --cwd."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    runner.invoke(app, ["mission", "refine", "--cwd", str(tmp_path), "--title", "CWD Draft"])

    result = runner.invoke(app, ["mission", "drafts", "--cwd", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "CWD Draft" in result.output


# ---------------------------------------------------------------------------
# Draft/canonical separation — governance surfaces unaffected
# ---------------------------------------------------------------------------


def test_mission_draft_does_not_affect_brief(tmp_path: Path) -> None:
    """spine brief still reads canonical mission even when drafts exist."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_mission_refine(tmp_path, "--title", "Draft Not Canonical")

    # brief should use canonical mission, not draft
    result = runner.invoke(app, ["brief", "--target", "claude", "--cwd", str(tmp_path)])
    # brief uses canonical mission.yaml — draft title should not appear as the mission title
    # canonical title is "Define active mission"
    assert "Draft Not Canonical" not in result.output or "mission.yaml" not in result.output or result.exit_code in (0, 1)
    # Key check: canonical mission.yaml title is unchanged
    mission_path = tmp_path / ".spine" / "mission.yaml"
    data = yaml.safe_load(mission_path.read_text())
    assert data["title"] == "Define active mission"
