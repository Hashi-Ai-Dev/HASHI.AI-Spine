"""Tests for spine init command (Phase 1)."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from spine.main import app
from spine.models import ConstraintsModel, MissionModel

runner = CliRunner()


def make_git_repo(tmp_path: Path) -> Path:
    """Create a minimal fake git repo (just a .git dir)."""
    (tmp_path / ".git").mkdir()
    return tmp_path


# ---------------------------------------------------------------------------
# Helper: run spine init with --cwd pointing at a temp dir
# ---------------------------------------------------------------------------

def run_init(tmp_path: Path, *extra_args: str) -> tuple[int, str, str]:
    result = runner.invoke(app, ["init", "--cwd", str(tmp_path), *extra_args])
    return result.exit_code, result.output, ""


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_init_fresh_git_repo(tmp_path: Path) -> None:
    """init in a fresh git repo creates all expected files and directories."""
    make_git_repo(tmp_path)
    exit_code, stdout, _ = run_init(tmp_path)

    assert exit_code == 0, stdout

    spine = tmp_path / ".spine"
    assert spine.is_dir()
    assert (spine / "mission.yaml").exists()
    assert (spine / "constraints.yaml").exists()

    for fname in [
        "opportunities.jsonl",
        "not_now.jsonl",
        "evidence.jsonl",
        "decisions.jsonl",
        "drift.jsonl",
        "runs.jsonl",
    ]:
        assert (spine / fname).exists(), f"Missing {fname}"

    assert (spine / "state.db").exists()

    for dname in ["reviews", "briefs", "skills", "checks"]:
        assert (spine / dname).is_dir(), f"Missing dir {dname}"

    assert (tmp_path / "AGENTS.md").exists()
    assert (tmp_path / "CLAUDE.md").exists()
    assert (tmp_path / ".claude" / "settings.json").exists()
    assert (tmp_path / ".codex" / "config.toml").exists()


def test_init_no_overwrite_without_force(tmp_path: Path) -> None:
    """init exits with code 3 when conflicting files exist and --force is not passed."""
    make_git_repo(tmp_path)
    # Pre-create a conflict file
    spine = tmp_path / ".spine"
    spine.mkdir()
    (spine / "mission.yaml").write_text("version: 1\n", encoding="utf-8")

    exit_code, output, _ = run_init(tmp_path)
    assert exit_code == 3
    assert ".spine/mission.yaml" in output


def test_init_force_overwrites(tmp_path: Path) -> None:
    """init with --force overwrites existing files."""
    make_git_repo(tmp_path)
    spine = tmp_path / ".spine"
    spine.mkdir()
    mission_path = spine / "mission.yaml"
    mission_path.write_text("version: 1\ntitle: old\n", encoding="utf-8")

    exit_code, stdout, _ = run_init(tmp_path, "--force")
    assert exit_code == 0

    # Content should be the fresh generated YAML, not the old stub
    new_content = mission_path.read_text()
    assert "old" not in new_content
    assert "mission-0001" in new_content


def test_init_no_git_exits_2(tmp_path: Path) -> None:
    """init exits with code 2 when not in a git repo."""
    exit_code, _, stderr = run_init(tmp_path)
    assert exit_code == 2


def test_init_allow_no_git(tmp_path: Path) -> None:
    """init with --allow-no-git succeeds outside a git repo."""
    exit_code, stdout, _ = run_init(tmp_path, "--allow-no-git")
    assert exit_code == 0
    assert (tmp_path / ".spine" / "mission.yaml").exists()


def test_mission_yaml_validates(tmp_path: Path) -> None:
    """Generated mission.yaml parses and validates with MissionModel."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    raw = (tmp_path / ".spine" / "mission.yaml").read_text()
    model = MissionModel.from_yaml(raw)
    assert model.version == 1
    assert model.status == "active"
    assert model.id == "mission-0001"


def test_constraints_yaml_validates(tmp_path: Path) -> None:
    """Generated constraints.yaml parses and validates with ConstraintsModel."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    raw = (tmp_path / ".spine" / "constraints.yaml").read_text()
    model = ConstraintsModel.from_yaml(raw)
    assert model.version == 1
    assert model.profile_name == "default"
    assert model.parallel_limits.max_active_missions == 1


def test_agents_md_created(tmp_path: Path) -> None:
    """AGENTS.md is created with expected content."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    agents_md = (tmp_path / "AGENTS.md").read_text()
    assert ".spine/" in agents_md
    assert "uv run pytest" in agents_md


def test_claude_md_created(tmp_path: Path) -> None:
    """CLAUDE.md is created."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    assert (tmp_path / "CLAUDE.md").exists()
    content = (tmp_path / "CLAUDE.md").read_text()
    assert "Phase 1" in content


def test_claude_settings_created(tmp_path: Path) -> None:
    """.claude/settings.json is created and contains valid JSON."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    settings_path = tmp_path / ".claude" / "settings.json"
    assert settings_path.exists()
    data = json.loads(settings_path.read_text())
    assert "permissions" in data


def test_codex_config_created(tmp_path: Path) -> None:
    """.codex/config.toml is created."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    config_path = tmp_path / ".codex" / "config.toml"
    assert config_path.exists()
    content = config_path.read_text()
    assert "workspace-write" in content


def test_init_idempotent_second_run(tmp_path: Path) -> None:
    """Running init twice without --force succeeds (only YAML/config conflict on first)."""
    make_git_repo(tmp_path)

    # First run
    exit_code, _, _ = run_init(tmp_path)
    assert exit_code == 0

    # Second run — existing YAML files trigger conflict
    exit_code2, output2, _ = run_init(tmp_path)
    assert exit_code2 == 3
    assert ".spine/mission.yaml" in output2


def test_init_idempotent_with_force(tmp_path: Path) -> None:
    """Running init twice with --force always succeeds."""
    make_git_repo(tmp_path)

    run_init(tmp_path, "--force")
    exit_code, stdout, _ = run_init(tmp_path, "--force")
    assert exit_code == 0
