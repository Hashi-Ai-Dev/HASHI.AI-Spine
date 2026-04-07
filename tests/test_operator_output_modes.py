"""Tests for Issue #17 — Operator/CI output modes + stable exit codes.

Covers:
- Exit code contract (0=success, 1=validation, 2=context)
- JSON output mode: structure, purity, failure behavior
- Quiet mode: suppression on success, preservation on failure
- No regression to Phase 3A.2 context-visibility behavior
- --cwd / SPINE_ROOT context failure exit codes
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


def make_git_repo(tmp_path: Path) -> Path:
    """Create a minimal fake git repo (just a .git dir) for init compatibility."""
    (tmp_path / ".git").mkdir()
    return tmp_path


def run_init(tmp_path: Path) -> None:
    runner.invoke(app, ["init", "--cwd", str(tmp_path)])


def run_cmd(args: list[str], cwd: Path) -> tuple[int, str]:
    original = os.getcwd()
    try:
        os.chdir(cwd)
        result = runner.invoke(app, args)
    finally:
        os.chdir(original)
    return result.exit_code, result.output


# ---------------------------------------------------------------------------
# Exit code contract — validation failures (exit 1)
# ---------------------------------------------------------------------------


class TestValidationExitCode:
    def test_brief_invalid_target_exits_1(self, tmp_path: Path) -> None:
        """brief with invalid --target exits 1 (validation failure)."""
        make_git_repo(tmp_path)
        run_init(tmp_path)

        code, out = run_cmd(["brief", "--target", "invalid_agent"], tmp_path)
        assert code == 1, f"Expected exit 1 (validation), got {code}"
        assert "claude" in out.lower() or "codex" in out.lower() or "error" in out.lower()

    def test_mission_set_invalid_status_exits_1(self, tmp_path: Path) -> None:
        """mission set with invalid --status exits 1 (validation failure)."""
        make_git_repo(tmp_path)
        run_init(tmp_path)

        code, out = run_cmd(["mission", "set", "--status", "bogus"], tmp_path)
        assert code == 1, f"Expected exit 1 (validation), got {code}"
        assert "validation" in out.lower() or "invalid" in out.lower()

    def test_review_invalid_recommendation_exits_1(self, tmp_path: Path) -> None:
        """review weekly with invalid --recommendation exits 1 (validation failure)."""
        make_git_repo(tmp_path)
        run_init(tmp_path)

        code, out = run_cmd(["review", "weekly", "--recommendation", "bogus"], tmp_path)
        assert code == 1, f"Expected exit 1 (validation), got {code}"

    def test_doctor_check_failure_exits_1(self, tmp_path: Path) -> None:
        """doctor with corrupted mission.yaml exits 1 (validation failure)."""
        make_git_repo(tmp_path)
        run_init(tmp_path)

        (tmp_path / ".spine" / "mission.yaml").write_text("INVALID: [}\n", encoding="utf-8")

        code, out = run_cmd(["doctor"], tmp_path)
        assert code == 1, f"Expected exit 1 (validation), got {code}"


# ---------------------------------------------------------------------------
# Exit code contract — context failures (exit 2)
# ---------------------------------------------------------------------------


class TestContextExitCode:
    def test_doctor_no_git_repo_exits_2(self, tmp_path: Path) -> None:
        """doctor in a non-git directory exits 2 (context failure)."""
        code, out = run_cmd(["doctor"], tmp_path)
        assert code == 2, f"Expected exit 2 (context), got {code}"

    def test_brief_no_git_repo_exits_2(self, tmp_path: Path) -> None:
        """brief in a non-git directory exits 2 (context failure)."""
        code, out = run_cmd(["brief", "--target", "claude"], tmp_path)
        assert code == 2, f"Expected exit 2 (context), got {code}"

    def test_drift_scan_no_git_repo_exits_2(self, tmp_path: Path) -> None:
        """drift scan in a non-git directory exits 2 (context failure)."""
        code, out = run_cmd(["drift", "scan"], tmp_path)
        assert code == 2, f"Expected exit 2 (context), got {code}"

    def test_mission_show_missing_state_exits_2(self, tmp_path: Path) -> None:
        """mission show with missing mission.yaml exits 2 (context failure)."""
        make_git_repo(tmp_path)
        # No spine init

        code, out = run_cmd(["mission", "show"], tmp_path)
        assert code == 2, f"Expected exit 2 (context), got {code}"

    def test_mission_set_missing_state_exits_2(self, tmp_path: Path) -> None:
        """mission set with missing mission.yaml exits 2 (context failure)."""
        make_git_repo(tmp_path)
        # No spine init

        code, out = run_cmd(["mission", "set", "--title", "test"], tmp_path)
        assert code == 2, f"Expected exit 2 (context), got {code}"

    def test_brief_missing_mission_yaml_exits_2(self, tmp_path: Path) -> None:
        """brief with missing mission.yaml exits 2 (context failure)."""
        make_git_repo(tmp_path)
        # No spine init

        code, out = run_cmd(["brief", "--target", "claude"], tmp_path)
        assert code == 2, f"Expected exit 2 (context), got {code}"

    def test_doctor_invalid_cwd_exits_2(self, tmp_path: Path) -> None:
        """doctor --cwd pointing to a non-repo exits 2 (context failure)."""
        not_a_repo = tmp_path / "not_a_repo"
        not_a_repo.mkdir()

        result = runner.invoke(app, ["doctor", "--cwd", str(not_a_repo)])
        assert result.exit_code == 2, f"Expected exit 2 (context), got {result.exit_code}"

    def test_doctor_spine_root_missing_path_exits_2(self, tmp_path: Path) -> None:
        """doctor with SPINE_ROOT pointing to missing path exits 2 (context failure)."""
        old = os.environ.pop("SPINE_ROOT", None)
        try:
            os.environ["SPINE_ROOT"] = str(tmp_path / "no_such_dir")
            result = runner.invoke(app, ["doctor"])
            assert result.exit_code == 2, f"Expected exit 2 (context), got {result.exit_code}"
        finally:
            os.environ.pop("SPINE_ROOT", None)
            if old is not None:
                os.environ["SPINE_ROOT"] = old


# ---------------------------------------------------------------------------
# Success exit code (exit 0)
# ---------------------------------------------------------------------------


class TestSuccessExitCode:
    def test_doctor_success_exits_0(self, tmp_path: Path) -> None:
        """doctor with valid state exits 0."""
        make_git_repo(tmp_path)
        run_init(tmp_path)

        code, out = run_cmd(["doctor"], tmp_path)
        assert code == 0, f"Expected exit 0 (success), got {code}. Output: {out}"

    def test_mission_show_success_exits_0(self, tmp_path: Path) -> None:
        """mission show with valid state exits 0."""
        make_git_repo(tmp_path)
        run_init(tmp_path)

        code, out = run_cmd(["mission", "show"], tmp_path)
        assert code == 0, f"Expected exit 0 (success), got {code}"

    def test_brief_success_exits_0(self, tmp_path: Path) -> None:
        """brief with valid state exits 0."""
        make_git_repo(tmp_path)
        run_init(tmp_path)

        code, out = run_cmd(["brief", "--target", "claude"], tmp_path)
        assert code == 0, f"Expected exit 0 (success), got {code}"

    def test_drift_scan_success_exits_0(self, tmp_path: Path) -> None:
        """drift scan with valid git repo exits 0."""
        import subprocess
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=tmp_path, capture_output=True)
        (tmp_path / "README.md").write_text("# Test\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, capture_output=True)

        code, out = run_cmd(["drift", "scan"], tmp_path)
        assert code == 0, f"Expected exit 0 (success), got {code}"


# ---------------------------------------------------------------------------
# --json output: structure and purity
# ---------------------------------------------------------------------------


class TestJsonOutput:
    def test_doctor_json_success_structure(self, tmp_path: Path) -> None:
        """doctor --json on success emits valid JSON with required fields."""
        make_git_repo(tmp_path)
        run_init(tmp_path)

        code, out = run_cmd(["doctor", "--json"], tmp_path)
        assert code == 0, f"Expected exit 0, got {code}. Output: {out}"

        data = json.loads(out)
        assert data["passed"] is True
        assert "repo" in data
        assert "branch" in data
        assert "checked_at" in data
        assert "error_count" in data
        assert "warning_count" in data
        assert "issues" in data
        assert isinstance(data["issues"], list)

    def test_doctor_json_failure_structure(self, tmp_path: Path) -> None:
        """doctor --json on failure emits valid JSON and exits 1."""
        make_git_repo(tmp_path)
        run_init(tmp_path)
        (tmp_path / "AGENTS.md").unlink()

        code, out = run_cmd(["doctor", "--json"], tmp_path)
        assert code == 1, f"Expected exit 1 (validation), got {code}"

        data = json.loads(out)
        assert data["passed"] is False
        assert data["error_count"] > 0
        assert len(data["issues"]) > 0
        for issue in data["issues"]:
            assert "severity" in issue
            assert "file" in issue
            assert "message" in issue

    def test_doctor_json_context_failure_structure(self, tmp_path: Path) -> None:
        """doctor --json with context failure emits valid JSON and exits 2."""
        not_a_repo = tmp_path / "not_a_repo"
        not_a_repo.mkdir()

        result = runner.invoke(app, ["doctor", "--json", "--cwd", str(not_a_repo)])
        assert result.exit_code == 2, f"Expected exit 2 (context), got {result.exit_code}"

        data = json.loads(result.output)
        assert "error" in data
        assert data["exit_code"] == 2

    def test_mission_show_json_structure(self, tmp_path: Path) -> None:
        """mission show --json emits valid JSON with mission fields."""
        make_git_repo(tmp_path)
        run_init(tmp_path)

        code, out = run_cmd(["mission", "show", "--json"], tmp_path)
        assert code == 0, f"Expected exit 0, got {code}"

        data = json.loads(out)
        assert "id" in data
        assert "title" in data
        assert "status" in data

    def test_mission_show_json_purity(self, tmp_path: Path) -> None:
        """mission show --json stdout contains only valid JSON (no chatter)."""
        make_git_repo(tmp_path)
        run_init(tmp_path)

        code, out = run_cmd(["mission", "show", "--json"], tmp_path)
        assert code == 0

        # Must parse cleanly as JSON — no prefix/suffix chatter
        data = json.loads(out)
        assert isinstance(data, dict)

    def test_brief_json_success_structure(self, tmp_path: Path) -> None:
        """brief --json emits valid JSON with expected fields."""
        make_git_repo(tmp_path)
        run_init(tmp_path)

        code, out = run_cmd(["brief", "--json", "--target", "claude"], tmp_path)
        assert code == 0, f"Expected exit 0, got {code}. Output: {out}"

        data = json.loads(out)
        assert data["target"] == "claude"
        assert "canonical_path" in data
        assert "latest_path" in data
        assert "mission_title" in data
        assert "generated_at" in data

    def test_brief_json_codex_target(self, tmp_path: Path) -> None:
        """brief --json works for codex target too."""
        make_git_repo(tmp_path)
        run_init(tmp_path)

        code, out = run_cmd(["brief", "--json", "--target", "codex"], tmp_path)
        assert code == 0, f"Expected exit 0, got {code}"

        data = json.loads(out)
        assert data["target"] == "codex"

    def test_brief_json_validation_failure_structure(self, tmp_path: Path) -> None:
        """brief --json with invalid target emits JSON error and exits 1."""
        make_git_repo(tmp_path)
        run_init(tmp_path)

        code, out = run_cmd(["brief", "--json", "--target", "not_valid"], tmp_path)
        assert code == 1, f"Expected exit 1 (validation), got {code}"

        data = json.loads(out)
        assert "error" in data
        assert data["exit_code"] == 1

    def test_brief_json_context_failure_structure(self, tmp_path: Path) -> None:
        """brief --json with no git repo emits JSON error and exits 2."""
        code, out = run_cmd(["brief", "--json", "--target", "claude"], tmp_path)
        assert code == 2, f"Expected exit 2 (context), got {code}"

        data = json.loads(out)
        assert "error" in data
        assert data["exit_code"] == 2

    def test_drift_scan_json_clean_structure(self, tmp_path: Path) -> None:
        """drift scan --json on clean repo emits valid JSON."""
        import subprocess
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=tmp_path, capture_output=True)
        (tmp_path / "README.md").write_text("# Test\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, capture_output=True)

        code, out = run_cmd(["drift", "scan", "--json"], tmp_path)
        assert code == 0, f"Expected exit 0, got {code}"

        data = json.loads(out)
        assert data["clean"] is True
        assert "repo" in data
        assert "branch" in data
        assert "scanned_at" in data
        assert "event_count" in data
        assert data["event_count"] == 0
        assert "severity_summary" in data
        assert "events" in data
        assert isinstance(data["events"], list)

    def test_drift_scan_json_with_drift(self, tmp_path: Path) -> None:
        """drift scan --json with forbidden files emits drift events in JSON."""
        import subprocess
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=tmp_path, capture_output=True)
        (tmp_path / "README.md").write_text("# Test\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, capture_output=True)
        run_init(tmp_path)

        # Add a forbidden file and stage it
        (tmp_path / "ui").mkdir()
        (tmp_path / "ui" / "dashboard.py").write_text("from flask import render_template\n", encoding="utf-8")
        subprocess.run(["git", "add", "ui/dashboard.py"], cwd=tmp_path, capture_output=True)

        code, out = run_cmd(["drift", "scan", "--json"], tmp_path)
        assert code == 0

        data = json.loads(out)
        assert data["clean"] is False
        assert data["event_count"] > 0
        assert len(data["events"]) > 0
        for event in data["events"]:
            assert "severity" in event
            assert "category" in event
            assert "description" in event
            assert "file_path" in event

    def test_drift_scan_json_context_failure(self, tmp_path: Path) -> None:
        """drift scan --json with no git repo emits JSON error and exits 2."""
        code, out = run_cmd(["drift", "scan", "--json"], tmp_path)
        assert code == 2, f"Expected exit 2 (context), got {code}"

        data = json.loads(out)
        assert "error" in data
        assert data["exit_code"] == 2

    def test_json_stdout_only_no_mixed_chatter(self, tmp_path: Path) -> None:
        """In JSON mode, stdout is parseable JSON only — no extra lines."""
        make_git_repo(tmp_path)
        run_init(tmp_path)

        code, out = run_cmd(["doctor", "--json"], tmp_path)
        assert code == 0

        # Strip and parse — should work with no leading/trailing non-JSON content
        parsed = json.loads(out.strip())
        assert isinstance(parsed, dict)


# ---------------------------------------------------------------------------
# --quiet mode
# ---------------------------------------------------------------------------


class TestQuietMode:
    def test_doctor_quiet_suppresses_output_on_success(self, tmp_path: Path) -> None:
        """doctor --quiet on success produces no output."""
        make_git_repo(tmp_path)
        run_init(tmp_path)

        code, out = run_cmd(["doctor", "--quiet"], tmp_path)
        assert code == 0
        assert out.strip() == "", f"Expected no output in quiet success mode, got: {repr(out)}"

    def test_doctor_quiet_preserves_errors_on_failure(self, tmp_path: Path) -> None:
        """doctor --quiet on failure still shows issues."""
        make_git_repo(tmp_path)
        run_init(tmp_path)
        (tmp_path / "AGENTS.md").unlink()

        code, out = run_cmd(["doctor", "--quiet"], tmp_path)
        assert code == 1
        # Issues must still appear even in quiet mode
        assert "AGENTS.md" in out or "error" in out.lower() or "missing" in out.lower()

    def test_doctor_quiet_suppresses_context_line(self, tmp_path: Path) -> None:
        """doctor --quiet suppresses the repo/branch context line on success."""
        make_git_repo(tmp_path)
        run_init(tmp_path)

        code, out = run_cmd(["doctor", "--quiet"], tmp_path)
        assert code == 0
        # Context line contains "repo:" prefix — should be absent in quiet mode
        assert "repo:" not in out

    def test_drift_scan_quiet_suppresses_output_on_clean(self, tmp_path: Path) -> None:
        """drift scan --quiet on clean repo produces no output."""
        import subprocess
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=tmp_path, capture_output=True)
        (tmp_path / "README.md").write_text("# Test\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, capture_output=True)

        code, out = run_cmd(["drift", "scan", "--quiet"], tmp_path)
        assert code == 0
        assert out.strip() == "", f"Expected no output in quiet clean mode, got: {repr(out)}"

    def test_drift_scan_quiet_shows_drift_when_present(self, tmp_path: Path) -> None:
        """drift scan --quiet still shows drift events when present."""
        import subprocess
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=tmp_path, capture_output=True)
        (tmp_path / "README.md").write_text("# Test\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, capture_output=True)
        run_init(tmp_path)

        (tmp_path / "ui").mkdir()
        (tmp_path / "ui" / "dashboard.py").write_text("from flask import render_template\n", encoding="utf-8")
        subprocess.run(["git", "add", "ui/dashboard.py"], cwd=tmp_path, capture_output=True)

        code, out = run_cmd(["drift", "scan", "--quiet"], tmp_path)
        assert code == 0
        # Drift still visible in quiet mode
        assert "HIGH" in out or "forbidden" in out.lower() or "drift" in out.lower()

    def test_brief_quiet_suppresses_context_and_alias_lines(self, tmp_path: Path) -> None:
        """brief --quiet suppresses context line and 'Latest alias updated' message."""
        make_git_repo(tmp_path)
        run_init(tmp_path)

        code, out = run_cmd(["brief", "--quiet", "--target", "claude"], tmp_path)
        assert code == 0

        # Should still show the canonical path
        assert "Brief generated" in out or ".md" in out
        # Context line should be absent
        assert "repo:" not in out
        # Latest alias line should be absent
        assert "Latest alias" not in out

    def test_brief_quiet_still_shows_generated_path(self, tmp_path: Path) -> None:
        """brief --quiet still outputs the canonical brief path."""
        make_git_repo(tmp_path)
        run_init(tmp_path)

        code, out = run_cmd(["brief", "--quiet", "--target", "claude"], tmp_path)
        assert code == 0
        # The brief path must appear for scripting use
        assert ".md" in out or "brief" in out.lower()

    def test_quiet_and_json_not_combined(self, tmp_path: Path) -> None:
        """--json mode takes precedence; quiet is irrelevant when JSON is used."""
        make_git_repo(tmp_path)
        run_init(tmp_path)

        code, out = run_cmd(["doctor", "--json", "--quiet"], tmp_path)
        assert code == 0
        # Must still be parseable JSON
        data = json.loads(out.strip())
        assert isinstance(data, dict)


# ---------------------------------------------------------------------------
# No regression: Phase 3A.2 context visibility (non-quiet, non-json)
# ---------------------------------------------------------------------------


class TestContextVisibilityRegression:
    def test_doctor_shows_context_line_normally(self, tmp_path: Path) -> None:
        """Without --quiet, doctor still shows repo/branch context line."""
        make_git_repo(tmp_path)
        run_init(tmp_path)

        code, out = run_cmd(["doctor"], tmp_path)
        assert code == 0
        assert "repo:" in out

    def test_drift_scan_shows_context_line_normally(self, tmp_path: Path) -> None:
        """Without --quiet, drift scan shows repo/branch context line."""
        import subprocess
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=tmp_path, capture_output=True)
        (tmp_path / "README.md").write_text("# Test\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, capture_output=True)

        code, out = run_cmd(["drift", "scan"], tmp_path)
        assert code == 0
        assert "repo:" in out

    def test_brief_shows_context_line_normally(self, tmp_path: Path) -> None:
        """Without --quiet, brief shows repo/branch context line."""
        make_git_repo(tmp_path)
        run_init(tmp_path)

        code, out = run_cmd(["brief", "--target", "claude"], tmp_path)
        assert code == 0
        assert "repo:" in out
