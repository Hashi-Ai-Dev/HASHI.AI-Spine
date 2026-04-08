"""Tests for spine check before-pr command (Issue #31)."""

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


def run_before_pr(path: Path, *extra_args: str) -> tuple[int, str]:
    result = runner.invoke(app, ["check", "before-pr", "--cwd", str(path), *extra_args])
    return result.exit_code, result.output


def append_jsonl(path: Path, record: dict) -> None:
    """Append a JSON record to a JSONL file."""
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


# ---------------------------------------------------------------------------
# Command registration
# ---------------------------------------------------------------------------


def test_check_group_registered() -> None:
    """spine check subgroup is registered and has help."""
    result = runner.invoke(app, ["check", "--help"])
    assert result.exit_code == 0, result.output
    assert "before-pr" in result.output


def test_before_pr_help() -> None:
    """spine check before-pr --help shows expected info."""
    result = runner.invoke(app, ["check", "before-pr", "--help"])
    assert result.exit_code == 0, result.output
    plain = _strip_ansi(result.output)
    assert "before-pr" in plain
    assert "--cwd" in plain
    assert "--json" in plain


# ---------------------------------------------------------------------------
# Pass path
# ---------------------------------------------------------------------------


def test_pass_path_all_checks_pass(tmp_path: Path) -> None:
    """All checks pass with a fully initialised SPINE repo and evidence+decisions."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    # Add evidence and a decision
    evidence_path = tmp_path / ".spine" / "evidence.jsonl"
    decisions_path = tmp_path / ".spine" / "decisions.jsonl"
    append_jsonl(evidence_path, {
        "kind": "commit",
        "description": "Implemented feature X",
        "evidence_url": None,
        "created_at": "2026-04-08T00:00:00+00:00",
    })
    append_jsonl(decisions_path, {
        "title": "Use DriftService for drift checks",
        "why": "Reuses existing tested code",
        "decision": "Compose DriftService in CheckService",
        "alternatives": [],
        "created_at": "2026-04-08T00:00:00+00:00",
    })

    exit_code, output = run_before_pr(tmp_path)
    assert exit_code == 0, f"Expected exit 0 (pass), got {exit_code}. Output:\n{output}"
    assert "PASS" in output
    assert "Result: PASS" in output


def test_pass_path_shows_all_check_names(tmp_path: Path) -> None:
    """Pass path output includes all expected check names."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    evidence_path = tmp_path / ".spine" / "evidence.jsonl"
    decisions_path = tmp_path / ".spine" / "decisions.jsonl"
    append_jsonl(evidence_path, {"kind": "commit", "description": "x", "evidence_url": None, "created_at": "2026-04-08T00:00:00+00:00"})
    append_jsonl(decisions_path, {"title": "t", "why": "y", "decision": "d", "alternatives": [], "created_at": "2026-04-08T00:00:00+00:00"})

    _, output = run_before_pr(tmp_path)
    assert "spine_dir" in output
    assert "mission" in output
    assert "doctor" in output
    assert "drift" in output
    assert "evidence" in output
    assert "decisions" in output


# ---------------------------------------------------------------------------
# Review-recommended path
# ---------------------------------------------------------------------------


def test_review_recommended_when_spine_dir_missing(tmp_path: Path) -> None:
    """Missing .spine/ directory causes review-recommended (exit 1)."""
    make_git_repo(tmp_path)
    # Do NOT run init — .spine/ is absent

    exit_code, output = run_before_pr(tmp_path)
    assert exit_code == 1, f"Expected exit 1, got {exit_code}. Output:\n{output}"
    assert "FAIL" in output or "REVIEW RECOMMENDED" in output


def test_review_recommended_when_mission_yaml_corrupt(tmp_path: Path) -> None:
    """Corrupted mission.yaml causes review-recommended (exit 1)."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    mission_path = tmp_path / ".spine" / "mission.yaml"
    mission_path.write_text("INVALID YAML: [}\n  broken: ", encoding="utf-8")

    exit_code, output = run_before_pr(tmp_path)
    assert exit_code == 1, f"Expected exit 1, got {exit_code}. Output:\n{output}"
    assert "mission" in output.lower()


def test_review_recommended_when_no_evidence(tmp_path: Path) -> None:
    """Empty evidence.jsonl causes review-recommended (exit 1)."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    # Add a decision but NO evidence — evidence JSONL should be empty
    decisions_path = tmp_path / ".spine" / "decisions.jsonl"
    append_jsonl(decisions_path, {"title": "t", "why": "y", "decision": "d", "alternatives": [], "created_at": "2026-04-08T00:00:00+00:00"})

    exit_code, output = run_before_pr(tmp_path)
    # Empty evidence → warn → review_recommended → exit 1
    assert exit_code == 1, f"Expected exit 1 (evidence warn), got {exit_code}. Output:\n{output}"
    assert "evidence" in output.lower()


def test_review_recommended_when_no_decisions(tmp_path: Path) -> None:
    """Empty decisions.jsonl causes review-recommended (exit 1)."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    evidence_path = tmp_path / ".spine" / "evidence.jsonl"
    append_jsonl(evidence_path, {"kind": "commit", "description": "x", "evidence_url": None, "created_at": "2026-04-08T00:00:00+00:00"})
    # Leave decisions empty

    exit_code, output = run_before_pr(tmp_path)
    assert exit_code == 1, f"Expected exit 1 (decisions warn), got {exit_code}. Output:\n{output}"
    assert "decisions" in output.lower() or "decision" in output.lower()


def test_review_recommended_when_drift_present(tmp_path: Path) -> None:
    """Drift events in drift.jsonl cause review-recommended (exit 1)."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    # Add evidence and decisions so those checks pass
    evidence_path = tmp_path / ".spine" / "evidence.jsonl"
    decisions_path = tmp_path / ".spine" / "decisions.jsonl"
    append_jsonl(evidence_path, {"kind": "commit", "description": "x", "evidence_url": None, "created_at": "2026-04-08T00:00:00+00:00"})
    append_jsonl(decisions_path, {"title": "t", "why": "y", "decision": "d", "alternatives": [], "created_at": "2026-04-08T00:00:00+00:00"})

    # Inject a drift event
    drift_path = tmp_path / ".spine" / "drift.jsonl"
    append_jsonl(drift_path, {
        "severity": "high",
        "category": "forbidden_expansion",
        "description": "File path matches drift pattern: ui/dashboard.py",
        "file_path": "ui/dashboard.py",
        "diff_hunk": "",
        "created_at": "2026-04-08T00:00:00+00:00",
    })

    exit_code, output = run_before_pr(tmp_path)
    assert exit_code == 1, f"Expected exit 1 (drift warn), got {exit_code}. Output:\n{output}"
    assert "drift" in output.lower()
    assert "WARN" in output or "review" in output.lower()


# ---------------------------------------------------------------------------
# --cwd support
# ---------------------------------------------------------------------------


def test_cwd_support_no_chdir(tmp_path: Path) -> None:
    """--cwd works without changing process cwd."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    evidence_path = tmp_path / ".spine" / "evidence.jsonl"
    decisions_path = tmp_path / ".spine" / "decisions.jsonl"
    append_jsonl(evidence_path, {"kind": "commit", "description": "x", "evidence_url": None, "created_at": "2026-04-08T00:00:00+00:00"})
    append_jsonl(decisions_path, {"title": "t", "why": "y", "decision": "d", "alternatives": [], "created_at": "2026-04-08T00:00:00+00:00"})

    original_cwd = os.getcwd()
    # Invoke without cd-ing into tmp_path — --cwd must handle it
    result = runner.invoke(app, ["check", "before-pr", "--cwd", str(tmp_path)])
    assert os.getcwd() == original_cwd, "cwd must not change after invocation"
    assert result.exit_code == 0, f"Expected exit 0, got {result.exit_code}. Output:\n{result.output}"


def test_cwd_invalid_path() -> None:
    """--cwd pointing to a non-git path returns exit 2."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.invoke(app, ["check", "before-pr", "--cwd", tmpdir])
        assert result.exit_code == 2, f"Expected exit 2, got {result.exit_code}. Output:\n{result.output}"


# ---------------------------------------------------------------------------
# JSON output
# ---------------------------------------------------------------------------


def test_json_output_structure(tmp_path: Path) -> None:
    """--json flag emits valid JSON with expected keys."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    result = runner.invoke(app, ["check", "before-pr", "--cwd", str(tmp_path), "--json"])
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


def test_json_output_exit_codes(tmp_path: Path) -> None:
    """--json exit codes match result field."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    evidence_path = tmp_path / ".spine" / "evidence.jsonl"
    decisions_path = tmp_path / ".spine" / "decisions.jsonl"
    append_jsonl(evidence_path, {"kind": "commit", "description": "x", "evidence_url": None, "created_at": "2026-04-08T00:00:00+00:00"})
    append_jsonl(decisions_path, {"title": "t", "why": "y", "decision": "d", "alternatives": [], "created_at": "2026-04-08T00:00:00+00:00"})

    result = runner.invoke(app, ["check", "before-pr", "--cwd", str(tmp_path), "--json"])
    data = json.loads(result.output)
    if data["passed"]:
        assert result.exit_code == 0
    else:
        assert result.exit_code == 1


def test_json_context_failure(tmp_path: Path) -> None:
    """--json emits error JSON on context failure (no git repo)."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.invoke(app, ["check", "before-pr", "--cwd", tmpdir, "--json"])
        assert result.exit_code == 2
        data = json.loads(result.output)
        assert "error" in data
        assert data["exit_code"] == 2


# ---------------------------------------------------------------------------
# Deterministic behavior
# ---------------------------------------------------------------------------


def test_deterministic_same_result_twice(tmp_path: Path) -> None:
    """Running before-pr twice on same repo yields same result."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    evidence_path = tmp_path / ".spine" / "evidence.jsonl"
    decisions_path = tmp_path / ".spine" / "decisions.jsonl"
    append_jsonl(evidence_path, {"kind": "commit", "description": "x", "evidence_url": None, "created_at": "2026-04-08T00:00:00+00:00"})
    append_jsonl(decisions_path, {"title": "t", "why": "y", "decision": "d", "alternatives": [], "created_at": "2026-04-08T00:00:00+00:00"})

    r1 = runner.invoke(app, ["check", "before-pr", "--cwd", str(tmp_path), "--json"])
    r2 = runner.invoke(app, ["check", "before-pr", "--cwd", str(tmp_path), "--json"])

    d1 = json.loads(r1.output)
    d2 = json.loads(r2.output)

    # Result and check statuses must match (timestamps may differ)
    assert d1["result"] == d2["result"]
    assert d1["passed"] == d2["passed"]
    assert [c["name"] for c in d1["checks"]] == [c["name"] for c in d2["checks"]]
    assert [c["status"] for c in d1["checks"]] == [c["status"] for c in d2["checks"]]


def test_no_state_mutation(tmp_path: Path) -> None:
    """Running before-pr does NOT write any new files to .spine/."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    spine_dir = tmp_path / ".spine"
    before = set(f.name for f in spine_dir.iterdir())

    run_before_pr(tmp_path)

    after = set(f.name for f in spine_dir.iterdir())
    assert before == after, f"before-pr mutated .spine/: new files {after - before}"


# ---------------------------------------------------------------------------
# Output content checks
# ---------------------------------------------------------------------------


def test_human_output_shows_repo(tmp_path: Path) -> None:
    """Human output includes the target repo path."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    _, output = run_before_pr(tmp_path)
    assert str(tmp_path) in output


def test_human_output_shows_final_verdict(tmp_path: Path) -> None:
    """Human output always includes a clear final Result line."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    _, output = run_before_pr(tmp_path)
    assert "Result:" in output


# ---------------------------------------------------------------------------
# Issue #43 regression: doctor warnings must not force exit 1
# ---------------------------------------------------------------------------


def test_doctor_warnings_do_not_cause_failure(tmp_path: Path) -> None:
    """Doctor warnings (e.g. missing optional subdirs) must NOT cause exit 1.

    Regression test for #43: benign/expected doctor warnings on a freshly-
    cloned or partially-initialized repo were incorrectly treated as failures,
    causing `check before-pr` to exit 1 on healthy repos.
    """
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    # Add evidence and decisions so those checks pass
    evidence_path = tmp_path / ".spine" / "evidence.jsonl"
    decisions_path = tmp_path / ".spine" / "decisions.jsonl"
    append_jsonl(evidence_path, {
        "kind": "commit",
        "description": "Implemented feature X",
        "evidence_url": None,
        "created_at": "2026-04-08T00:00:00+00:00",
    })
    append_jsonl(decisions_path, {
        "title": "Use DriftService",
        "why": "Reuses tested code",
        "decision": "Compose DriftService",
        "alternatives": [],
        "created_at": "2026-04-08T00:00:00+00:00",
    })

    # Remove optional subdirectories to trigger doctor warnings
    # (simulates a freshly cloned repo where empty dirs weren't git-tracked)
    for subdir in ["reviews", "briefs", "skills", "checks"]:
        d = tmp_path / ".spine" / subdir
        if d.exists():
            d.rmdir()

    exit_code, output = run_before_pr(tmp_path)
    assert exit_code == 0, (
        f"Expected exit 0: doctor warnings are advisory, not failures.\n"
        f"Output:\n{output}"
    )
    assert "PASS" in output or "pass" in output.lower()
    # Doctor check must still appear in output (signal preserved)
    assert "doctor" in output.lower()


def test_doctor_errors_still_cause_failure(tmp_path: Path) -> None:
    """Doctor errors (not warnings) must still cause exit 1.

    Ensures the #43 fix only relaxes warnings, not genuine errors.
    """
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    # Corrupt mission.yaml to trigger a doctor error
    mission_path = tmp_path / ".spine" / "mission.yaml"
    mission_path.write_text("INVALID YAML: [}\n  broken: ", encoding="utf-8")

    exit_code, output = run_before_pr(tmp_path)
    assert exit_code == 1, (
        f"Expected exit 1: doctor errors must still block before-pr.\n"
        f"Output:\n{output}"
    )
