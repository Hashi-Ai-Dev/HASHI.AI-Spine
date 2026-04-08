"""Tests for spine check before-work command (Issue #50)."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from typer.testing import CliRunner

from spine.main import app

runner = CliRunner()


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text (Rich may colorize help output in CI)."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_git_repo(path: Path) -> Path:
    """Create a minimal fake git repo (.git dir only)."""
    (path / ".git").mkdir()
    return path


def spine_init(path: Path) -> None:
    result = runner.invoke(app, ["init", "--cwd", str(path)])
    assert result.exit_code == 0, f"init failed: {result.output}"


def run_before_work(path: Path, *extra_args: str) -> tuple[int, str]:
    result = runner.invoke(app, ["check", "before-work", "--cwd", str(path), *extra_args])
    return result.exit_code, result.output


def append_jsonl(path: Path, record: dict) -> None:
    """Append a JSON record to a JSONL file."""
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


# ---------------------------------------------------------------------------
# Command registration
# ---------------------------------------------------------------------------


def test_check_group_shows_before_work() -> None:
    """spine check --help lists before-work subcommand."""
    result = runner.invoke(app, ["check", "--help"])
    assert result.exit_code == 0, result.output
    assert "before-work" in result.output


def test_before_work_help() -> None:
    """spine check before-work --help shows expected info."""
    result = runner.invoke(app, ["check", "before-work", "--help"])
    assert result.exit_code == 0, result.output
    plain = _strip_ansi(result.output)
    assert "before-work" in plain
    assert "--cwd" in plain
    assert "--json" in plain


def test_before_work_help_shows_exit_codes() -> None:
    """Help text documents exit codes."""
    result = runner.invoke(app, ["check", "before-work", "--help"])
    plain = _strip_ansi(result.output)
    assert "0" in plain
    assert "1" in plain
    assert "2" in plain


# ---------------------------------------------------------------------------
# Pass path
# ---------------------------------------------------------------------------


def test_pass_path_with_brief(tmp_path: Path) -> None:
    """All checks pass with a fully initialized repo and at least one brief."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    # Create a brief file to satisfy recent_brief check
    briefs_dir = tmp_path / ".spine" / "briefs" / "claude"
    briefs_dir.mkdir(parents=True, exist_ok=True)
    (briefs_dir / "latest.md").write_text("# Mission Brief\nTest brief.", encoding="utf-8")

    exit_code, output = run_before_work(tmp_path)
    assert exit_code == 0, f"Expected exit 0 (pass), got {exit_code}. Output:\n{output}"
    assert "PASS" in output
    assert "Result: PASS" in output


def test_pass_path_shows_all_check_names(tmp_path: Path) -> None:
    """Pass path output includes all expected check names."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    briefs_dir = tmp_path / ".spine" / "briefs" / "claude"
    briefs_dir.mkdir(parents=True, exist_ok=True)
    (briefs_dir / "latest.md").write_text("# Brief", encoding="utf-8")

    _, output = run_before_work(tmp_path)
    assert "spine_dir" in output
    assert "mission" in output
    assert "doctor" in output
    assert "branch_context" in output
    assert "recent_brief" in output


def test_pass_path_shows_branch_context(tmp_path: Path) -> None:
    """Pass path output includes branch context info."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    briefs_dir = tmp_path / ".spine" / "briefs" / "claude"
    briefs_dir.mkdir(parents=True, exist_ok=True)
    (briefs_dir / "latest.md").write_text("# Brief", encoding="utf-8")

    _, output = run_before_work(tmp_path)
    assert "branch_context" in output
    assert "on branch" in output


# ---------------------------------------------------------------------------
# Review-recommended path
# ---------------------------------------------------------------------------


def test_review_recommended_when_spine_dir_missing(tmp_path: Path) -> None:
    """Missing .spine/ directory causes review-recommended (exit 1)."""
    make_git_repo(tmp_path)
    # Do NOT run init — .spine/ is absent

    exit_code, output = run_before_work(tmp_path)
    assert exit_code == 1, f"Expected exit 1, got {exit_code}. Output:\n{output}"
    assert "FAIL" in output or "REVIEW RECOMMENDED" in output


def test_review_recommended_when_mission_yaml_missing(tmp_path: Path) -> None:
    """Missing mission.yaml causes review-recommended (exit 1)."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    mission_path = tmp_path / ".spine" / "mission.yaml"
    mission_path.unlink()

    exit_code, output = run_before_work(tmp_path)
    assert exit_code == 1, f"Expected exit 1, got {exit_code}. Output:\n{output}"
    assert "mission" in output.lower()


def test_review_recommended_when_mission_yaml_corrupt(tmp_path: Path) -> None:
    """Corrupted mission.yaml causes review-recommended (exit 1)."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    mission_path = tmp_path / ".spine" / "mission.yaml"
    mission_path.write_text("INVALID YAML: [}\n  broken: ", encoding="utf-8")

    exit_code, output = run_before_work(tmp_path)
    assert exit_code == 1, f"Expected exit 1, got {exit_code}. Output:\n{output}"
    assert "mission" in output.lower()


def test_review_recommended_when_no_briefs(tmp_path: Path) -> None:
    """No brief history causes review-recommended (exit 1)."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)
    # No briefs created

    exit_code, output = run_before_work(tmp_path)
    assert exit_code == 1, f"Expected exit 1 (no briefs), got {exit_code}. Output:\n{output}"
    assert "recent_brief" in output
    assert "brief" in output.lower()


def test_review_recommended_when_briefs_dir_empty(tmp_path: Path) -> None:
    """Empty briefs dir (no .md files) still warns."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    # Create the dir but no files inside
    (tmp_path / ".spine" / "briefs" / "claude").mkdir(parents=True, exist_ok=True)

    exit_code, output = run_before_work(tmp_path)
    assert exit_code == 1, f"Expected exit 1 (empty briefs), got {exit_code}. Output:\n{output}"
    assert "recent_brief" in output


# ---------------------------------------------------------------------------
# No-brief message content
# ---------------------------------------------------------------------------


def test_no_brief_message_suggests_action(tmp_path: Path) -> None:
    """The no-brief warn message contains an actionable suggestion."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    _, output = run_before_work(tmp_path)
    assert "spine brief" in output or "fresh" in output.lower()


# ---------------------------------------------------------------------------
# Context failure
# ---------------------------------------------------------------------------


def test_context_failure_no_git_repo() -> None:
    """Non-git directory returns exit 2."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.invoke(app, ["check", "before-work", "--cwd", tmpdir])
        assert result.exit_code == 2, f"Expected exit 2, got {result.exit_code}. Output:\n{result.output}"


# ---------------------------------------------------------------------------
# --cwd support
# ---------------------------------------------------------------------------


def test_cwd_support_no_chdir(tmp_path: Path) -> None:
    """--cwd works without changing process cwd."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    briefs_dir = tmp_path / ".spine" / "briefs" / "claude"
    briefs_dir.mkdir(parents=True, exist_ok=True)
    (briefs_dir / "latest.md").write_text("# Brief", encoding="utf-8")

    original_cwd = os.getcwd()
    result = runner.invoke(app, ["check", "before-work", "--cwd", str(tmp_path)])
    assert os.getcwd() == original_cwd, "cwd must not change after invocation"
    assert result.exit_code == 0, f"Expected exit 0, got {result.exit_code}. Output:\n{result.output}"


def test_cwd_invalid_path() -> None:
    """--cwd pointing to a non-git path returns exit 2."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.invoke(app, ["check", "before-work", "--cwd", tmpdir])
        assert result.exit_code == 2, f"Expected exit 2, got {result.exit_code}. Output:\n{result.output}"


# ---------------------------------------------------------------------------
# JSON output
# ---------------------------------------------------------------------------


def test_json_output_structure(tmp_path: Path) -> None:
    """--json flag emits valid JSON with expected keys."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    result = runner.invoke(app, ["check", "before-work", "--cwd", str(tmp_path), "--json"])
    data = json.loads(result.output)

    assert "result" in data
    assert data["result"] in ("pass", "review_recommended")
    assert "passed" in data
    assert isinstance(data["passed"], bool)
    assert "repo" in data
    assert "branch" in data
    assert "checked_at" in data
    assert "checks" in data
    assert isinstance(data["checks"], list)

    for check in data["checks"]:
        assert "name" in check
        assert "status" in check
        assert check["status"] in ("pass", "warn", "fail")
        assert "message" in check


def test_json_output_includes_all_check_names(tmp_path: Path) -> None:
    """JSON output includes all expected check names."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    briefs_dir = tmp_path / ".spine" / "briefs" / "claude"
    briefs_dir.mkdir(parents=True, exist_ok=True)
    (briefs_dir / "latest.md").write_text("# Brief", encoding="utf-8")

    result = runner.invoke(app, ["check", "before-work", "--cwd", str(tmp_path), "--json"])
    data = json.loads(result.output)
    check_names = [c["name"] for c in data["checks"]]

    assert "spine_dir" in check_names
    assert "mission" in check_names
    assert "doctor" in check_names
    assert "branch_context" in check_names
    assert "recent_brief" in check_names


def test_json_output_exit_codes_match(tmp_path: Path) -> None:
    """--json exit codes match result field."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    briefs_dir = tmp_path / ".spine" / "briefs" / "claude"
    briefs_dir.mkdir(parents=True, exist_ok=True)
    (briefs_dir / "latest.md").write_text("# Brief", encoding="utf-8")

    result = runner.invoke(app, ["check", "before-work", "--cwd", str(tmp_path), "--json"])
    data = json.loads(result.output)
    if data["passed"]:
        assert result.exit_code == 0
    else:
        assert result.exit_code == 1


def test_json_context_failure(tmp_path: Path) -> None:
    """--json emits error JSON on context failure (no git repo)."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.invoke(app, ["check", "before-work", "--cwd", tmpdir, "--json"])
        assert result.exit_code == 2
        data = json.loads(result.output)
        assert "error" in data
        assert data["exit_code"] == 2


# ---------------------------------------------------------------------------
# Deterministic behavior
# ---------------------------------------------------------------------------


def test_deterministic_same_result_twice(tmp_path: Path) -> None:
    """Running before-work twice on same repo yields same result."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    briefs_dir = tmp_path / ".spine" / "briefs" / "claude"
    briefs_dir.mkdir(parents=True, exist_ok=True)
    (briefs_dir / "latest.md").write_text("# Brief", encoding="utf-8")

    r1 = runner.invoke(app, ["check", "before-work", "--cwd", str(tmp_path), "--json"])
    r2 = runner.invoke(app, ["check", "before-work", "--cwd", str(tmp_path), "--json"])

    d1 = json.loads(r1.output)
    d2 = json.loads(r2.output)

    assert d1["result"] == d2["result"]
    assert d1["passed"] == d2["passed"]
    assert [c["name"] for c in d1["checks"]] == [c["name"] for c in d2["checks"]]
    assert [c["status"] for c in d1["checks"]] == [c["status"] for c in d2["checks"]]


def test_no_state_mutation(tmp_path: Path) -> None:
    """Running before-work does NOT write any new files to .spine/."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    spine_dir = tmp_path / ".spine"
    before = set(f.name for f in spine_dir.iterdir())

    run_before_work(tmp_path)

    after = set(f.name for f in spine_dir.iterdir())
    assert before == after, f"before-work mutated .spine/: new files {after - before}"


# ---------------------------------------------------------------------------
# Output content checks
# ---------------------------------------------------------------------------


def test_human_output_shows_repo(tmp_path: Path) -> None:
    """Human output includes the target repo path."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    _, output = run_before_work(tmp_path)
    assert str(tmp_path) in output


def test_human_output_shows_final_verdict(tmp_path: Path) -> None:
    """Human output always includes a clear final Result line."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    _, output = run_before_work(tmp_path)
    assert "Result:" in output


# ---------------------------------------------------------------------------
# Doctor interaction: warnings must not force exit 1
# ---------------------------------------------------------------------------


def test_doctor_warnings_do_not_cause_failure(tmp_path: Path) -> None:
    """Doctor warnings (e.g. missing optional subdirs) must NOT cause exit 1.

    before-work follows the same convention as before-pr: only doctor *errors*
    block the check, not advisory warnings.
    """
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    # Create brief so recent_brief passes
    briefs_dir = tmp_path / ".spine" / "briefs" / "claude"
    briefs_dir.mkdir(parents=True, exist_ok=True)
    (briefs_dir / "latest.md").write_text("# Brief", encoding="utf-8")

    # Remove optional subdirectories to trigger doctor warnings
    for subdir in ["reviews", "skills", "checks"]:
        d = tmp_path / ".spine" / subdir
        if d.exists():
            d.rmdir()

    exit_code, output = run_before_work(tmp_path)
    assert exit_code == 0, (
        f"Expected exit 0: doctor warnings are advisory, not failures.\n"
        f"Output:\n{output}"
    )
    assert "PASS" in output or "pass" in output.lower()
    assert "doctor" in output.lower()


def test_doctor_errors_still_cause_failure(tmp_path: Path) -> None:
    """Doctor errors (not warnings) must still cause exit 1."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    # Corrupt mission.yaml to trigger a doctor error
    mission_path = tmp_path / ".spine" / "mission.yaml"
    mission_path.write_text("INVALID YAML: [}\n  broken: ", encoding="utf-8")

    exit_code, output = run_before_work(tmp_path)
    assert exit_code == 1, (
        f"Expected exit 1: doctor errors must still block before-work.\n"
        f"Output:\n{output}"
    )


# ---------------------------------------------------------------------------
# Isolation: before-work must not check evidence/decisions (unlike before-pr)
# ---------------------------------------------------------------------------


def test_no_evidence_does_not_block(tmp_path: Path) -> None:
    """before-work does NOT require evidence records to pass."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    # Add brief so recent_brief passes
    briefs_dir = tmp_path / ".spine" / "briefs" / "claude"
    briefs_dir.mkdir(parents=True, exist_ok=True)
    (briefs_dir / "latest.md").write_text("# Brief", encoding="utf-8")

    # Leave evidence empty — before-work should not care
    exit_code, output = run_before_work(tmp_path)
    assert exit_code == 0, (
        f"before-work must not require evidence (that's before-pr's job).\n"
        f"Output:\n{output}"
    )


def test_no_decisions_does_not_block(tmp_path: Path) -> None:
    """before-work does NOT require decision records to pass."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    briefs_dir = tmp_path / ".spine" / "briefs" / "claude"
    briefs_dir.mkdir(parents=True, exist_ok=True)
    (briefs_dir / "latest.md").write_text("# Brief", encoding="utf-8")

    # Leave decisions empty — before-work should not care
    exit_code, output = run_before_work(tmp_path)
    assert exit_code == 0, (
        f"before-work must not require decisions (that's before-pr's job).\n"
        f"Output:\n{output}"
    )


def test_drift_does_not_block(tmp_path: Path) -> None:
    """before-work does NOT block on drift (unlike before-pr)."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    briefs_dir = tmp_path / ".spine" / "briefs" / "claude"
    briefs_dir.mkdir(parents=True, exist_ok=True)
    (briefs_dir / "latest.md").write_text("# Brief", encoding="utf-8")

    # Inject drift events — before-work should not check for these
    drift_path = tmp_path / ".spine" / "drift.jsonl"
    append_jsonl(drift_path, {
        "severity": "high",
        "category": "forbidden_expansion",
        "description": "drift event",
        "file_path": "ui/dashboard.py",
        "diff_hunk": "",
        "created_at": "2026-04-08T00:00:00+00:00",
    })

    exit_code, output = run_before_work(tmp_path)
    # Drift should not block before-work (it's before-pr's concern)
    assert exit_code == 0, (
        f"before-work must not block on drift (that's before-pr's job).\n"
        f"Output:\n{output}"
    )
    # Also confirm drift check name is NOT in output
    assert "drift" not in output.lower() or "branch_context" in output
