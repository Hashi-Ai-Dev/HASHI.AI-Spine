"""Tests for spine review handoff command (Issue #32)."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from typer.testing import CliRunner

from spine.main import app

runner = CliRunner()


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text."""
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


def run_handoff(path: Path, *extra_args: str) -> tuple[int, str]:
    result = runner.invoke(app, ["review", "handoff", "--cwd", str(path), *extra_args])
    return result.exit_code, result.output


def append_jsonl(path: Path, record: dict) -> None:
    """Append a JSON record to a JSONL file."""
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


# ---------------------------------------------------------------------------
# Command registration
# ---------------------------------------------------------------------------


def test_review_group_has_handoff() -> None:
    """spine review subgroup lists handoff as a command."""
    result = runner.invoke(app, ["review", "--help"])
    assert result.exit_code == 0, result.output
    assert "handoff" in result.output


def test_handoff_help() -> None:
    """spine review handoff --help shows expected flags."""
    result = runner.invoke(app, ["review", "handoff", "--help"])
    assert result.exit_code == 0, result.output
    plain = _strip_ansi(result.output)
    assert "handoff" in plain
    assert "--cwd" in plain
    assert "--json" in plain
    assert "--days" in plain


# ---------------------------------------------------------------------------
# Basic behavior
# ---------------------------------------------------------------------------


def test_handoff_exits_zero(tmp_path: Path) -> None:
    """review handoff exits 0 on a valid repo."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)
    exit_code, output = run_handoff(tmp_path)
    assert exit_code == 0, f"Expected exit 0, got {exit_code}. Output:\n{output}"


def test_handoff_stdout_required(tmp_path: Path) -> None:
    """review handoff always produces output on stdout."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)
    exit_code, output = run_handoff(tmp_path)
    assert exit_code == 0
    assert len(output.strip()) > 0, "Expected non-empty stdout"


def test_handoff_no_state_mutation(tmp_path: Path) -> None:
    """review handoff does NOT write any files to .spine/."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    spine_dir = tmp_path / ".spine"
    before = set(f.name for f in spine_dir.iterdir())

    run_handoff(tmp_path)

    after = set(f.name for f in spine_dir.iterdir())
    assert before == after, f"handoff mutated .spine/: new files {after - before}"


# ---------------------------------------------------------------------------
# Summary content shape
# ---------------------------------------------------------------------------


def test_handoff_contains_mission_section(tmp_path: Path) -> None:
    """Handoff output includes MISSION section."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)
    _, output = run_handoff(tmp_path)
    plain = _strip_ansi(output)
    assert "MISSION" in plain
    assert "Title:" in plain
    assert "Status:" in plain


def test_handoff_contains_decisions_section(tmp_path: Path) -> None:
    """Handoff output includes RECENT DECISIONS section."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)
    _, output = run_handoff(tmp_path)
    plain = _strip_ansi(output)
    assert "RECENT DECISIONS" in plain


def test_handoff_contains_evidence_section(tmp_path: Path) -> None:
    """Handoff output includes RECENT EVIDENCE section."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)
    _, output = run_handoff(tmp_path)
    plain = _strip_ansi(output)
    assert "RECENT EVIDENCE" in plain


def test_handoff_contains_drift_section(tmp_path: Path) -> None:
    """Handoff output includes DRIFT STATE section."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)
    _, output = run_handoff(tmp_path)
    plain = _strip_ansi(output)
    assert "DRIFT STATE" in plain


def test_handoff_shows_mission_title(tmp_path: Path) -> None:
    """Handoff output shows the mission title from mission.yaml."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    mission_path = tmp_path / ".spine" / "mission.yaml"
    raw = mission_path.read_text()
    raw = raw.replace("Define active mission", "Ship the handoff feature")
    mission_path.write_text(raw)

    _, output = run_handoff(tmp_path)
    plain = _strip_ansi(output)
    assert "Ship the handoff feature" in plain


def test_handoff_shows_recent_decisions(tmp_path: Path) -> None:
    """Handoff shows recent decisions from decisions.jsonl."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    decisions_path = tmp_path / ".spine" / "decisions.jsonl"
    append_jsonl(decisions_path, {
        "title": "Use HandoffService for handoff",
        "why": "Clean separation",
        "decision": "Create HandoffService in services/",
        "alternatives": [],
        "created_at": "2026-04-08T00:00:00+00:00",
    })

    _, output = run_handoff(tmp_path)
    plain = _strip_ansi(output)
    assert "Use HandoffService for handoff" in plain


def test_handoff_shows_recent_evidence(tmp_path: Path) -> None:
    """Handoff shows recent evidence from evidence.jsonl."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    evidence_path = tmp_path / ".spine" / "evidence.jsonl"
    append_jsonl(evidence_path, {
        "kind": "commit",
        "description": "Implemented handoff command",
        "evidence_url": None,
        "created_at": "2026-04-08T00:00:00+00:00",
    })

    _, output = run_handoff(tmp_path)
    plain = _strip_ansi(output)
    assert "Implemented handoff command" in plain


def test_handoff_shows_drift_events(tmp_path: Path) -> None:
    """Handoff shows drift records from drift.jsonl."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    drift_path = tmp_path / ".spine" / "drift.jsonl"
    append_jsonl(drift_path, {
        "severity": "high",
        "category": "forbidden_expansion",
        "description": "File path matches drift pattern: ui/dashboard.py",
        "file_path": "ui/dashboard.py",
        "diff_hunk": "",
        "created_at": "2026-04-08T00:00:00+00:00",
    })

    _, output = run_handoff(tmp_path)
    plain = _strip_ansi(output)
    assert "ui/dashboard.py" in plain or "HIGH" in plain


def test_handoff_empty_state_no_crash(tmp_path: Path) -> None:
    """Handoff handles empty evidence/decisions/drift gracefully."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)
    exit_code, output = run_handoff(tmp_path)
    assert exit_code == 0
    plain = _strip_ansi(output)
    assert "none in this period" in plain or "no drift recorded" in plain


# ---------------------------------------------------------------------------
# --cwd support
# ---------------------------------------------------------------------------


def test_cwd_support_no_chdir(tmp_path: Path) -> None:
    """--cwd works without changing process cwd."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    original_cwd = os.getcwd()
    result = runner.invoke(app, ["review", "handoff", "--cwd", str(tmp_path)])
    assert os.getcwd() == original_cwd, "cwd must not change after invocation"
    assert result.exit_code == 0, f"Expected exit 0, got {result.exit_code}. Output:\n{result.output}"


def test_cwd_invalid_path_returns_exit_2() -> None:
    """--cwd pointing to a non-git path returns exit 2."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.invoke(app, ["review", "handoff", "--cwd", tmpdir])
        assert result.exit_code == 2, f"Expected exit 2, got {result.exit_code}. Output:\n{result.output}"


# ---------------------------------------------------------------------------
# --days parameter
# ---------------------------------------------------------------------------


def test_days_parameter_filters_old_records(tmp_path: Path) -> None:
    """--days=1 excludes records older than 1 day."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    decisions_path = tmp_path / ".spine" / "decisions.jsonl"
    # Old record — well outside 1-day window
    append_jsonl(decisions_path, {
        "title": "Old decision from 30 days ago",
        "why": "Historical",
        "decision": "Do something old",
        "alternatives": [],
        "created_at": "2026-03-01T00:00:00+00:00",
    })

    _, output = run_handoff(tmp_path, "--days", "1")
    plain = _strip_ansi(output)
    assert "Old decision from 30 days ago" not in plain


def test_days_parameter_includes_recent_records(tmp_path: Path) -> None:
    """--days=30 includes records within 30 days."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    decisions_path = tmp_path / ".spine" / "decisions.jsonl"
    append_jsonl(decisions_path, {
        "title": "Recent decision",
        "why": "Current",
        "decision": "Do something recent",
        "alternatives": [],
        "created_at": "2026-04-08T00:00:00+00:00",
    })

    _, output = run_handoff(tmp_path, "--days", "30")
    plain = _strip_ansi(output)
    assert "Recent decision" in plain


# ---------------------------------------------------------------------------
# Deterministic behavior
# ---------------------------------------------------------------------------


def test_deterministic_same_result_twice(tmp_path: Path) -> None:
    """Running handoff twice on same repo yields same content shape."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    r1 = runner.invoke(app, ["review", "handoff", "--cwd", str(tmp_path), "--json"])
    r2 = runner.invoke(app, ["review", "handoff", "--cwd", str(tmp_path), "--json"])

    d1 = json.loads(r1.output)
    d2 = json.loads(r2.output)

    # Content must match (timestamps will differ slightly but structure is same)
    assert d1["mission"]["title"] == d2["mission"]["title"]
    assert d1["mission"]["status"] == d2["mission"]["status"]
    assert len(d1["recent_decisions"]) == len(d2["recent_decisions"])
    assert len(d1["recent_evidence"]) == len(d2["recent_evidence"])
    assert len(d1["drift_records"]) == len(d2["drift_records"])


# ---------------------------------------------------------------------------
# --json output
# ---------------------------------------------------------------------------


def test_json_output_structure(tmp_path: Path) -> None:
    """--json emits valid JSON with all expected top-level keys."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    result = runner.invoke(app, ["review", "handoff", "--cwd", str(tmp_path), "--json"])
    assert result.exit_code == 0, f"Expected exit 0. Output:\n{result.output}"
    data = json.loads(result.output)

    assert "repo" in data
    assert "branch" in data
    assert "period_days" in data
    assert "generated_at" in data
    assert "mission" in data
    assert "recent_decisions" in data
    assert "recent_evidence" in data
    assert "drift_records" in data
    assert "totals" in data


def test_json_mission_fields(tmp_path: Path) -> None:
    """--json mission block includes title, status, promise, metric."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    result = runner.invoke(app, ["review", "handoff", "--cwd", str(tmp_path), "--json"])
    data = json.loads(result.output)

    mission = data["mission"]
    assert "title" in mission
    assert "status" in mission
    assert "promise" in mission
    assert "metric" in mission


def test_json_totals_are_integers(tmp_path: Path) -> None:
    """--json totals block contains integer counts."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    result = runner.invoke(app, ["review", "handoff", "--cwd", str(tmp_path), "--json"])
    data = json.loads(result.output)

    totals = data["totals"]
    assert isinstance(totals["decisions"], int)
    assert isinstance(totals["evidence"], int)
    assert isinstance(totals["drift"], int)


def test_json_context_failure(tmp_path: Path) -> None:
    """--json emits error JSON on context failure (no git repo)."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.invoke(app, ["review", "handoff", "--cwd", tmpdir, "--json"])
        assert result.exit_code == 2
        data = json.loads(result.output)
        assert "error" in data
        assert data["exit_code"] == 2


def test_json_period_days_reflects_flag(tmp_path: Path) -> None:
    """--json period_days matches the --days argument."""
    make_git_repo(tmp_path)
    spine_init(tmp_path)

    result = runner.invoke(app, ["review", "handoff", "--cwd", str(tmp_path), "--json", "--days", "14"])
    data = json.loads(result.output)
    assert data["period_days"] == 14
