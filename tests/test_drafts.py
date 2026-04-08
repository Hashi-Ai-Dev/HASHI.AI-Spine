"""Tests for Beta: draftable governance records (Issue #33).

Covers:
- spine evidence add --draft
- spine decision add --draft
- deterministic draft storage under .spine/drafts/
- spine drafts list
- spine drafts confirm <id> (explicit promotion)
- default exclusion of drafts from canonical surfaces (evidence.jsonl, decisions.jsonl)
- --cwd support for all draft commands
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
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


def run_evidence_add(tmp_path: Path, *extra_args: str) -> tuple[int, str]:
    original = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["evidence", "add", *extra_args])
    finally:
        os.chdir(original)
    return result.exit_code, result.output


def run_decision_add(tmp_path: Path, *extra_args: str) -> tuple[int, str]:
    original = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["decision", "add", *extra_args])
    finally:
        os.chdir(original)
    return result.exit_code, result.output


def run_drafts_list(tmp_path: Path) -> tuple[int, str]:
    result = runner.invoke(app, ["drafts", "list", "--cwd", str(tmp_path)])
    return result.exit_code, result.output


def run_drafts_confirm(tmp_path: Path, draft_id: str) -> tuple[int, str]:
    result = runner.invoke(app, ["drafts", "confirm", draft_id, "--cwd", str(tmp_path)])
    return result.exit_code, result.output


# ---------------------------------------------------------------------------
# Draft evidence creation
# ---------------------------------------------------------------------------


def test_evidence_draft_creates_file_in_drafts_dir(tmp_path: Path) -> None:
    """--draft stores evidence under .spine/drafts/ not evidence.jsonl."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout = run_evidence_add(
        tmp_path,
        "--kind", "commit",
        "--description", "draft commit evidence",
        "--draft",
    )
    assert exit_code == 0, stdout

    drafts_dir = tmp_path / ".spine" / "drafts"
    assert drafts_dir.exists(), ".spine/drafts/ should be created"
    draft_files = list(drafts_dir.glob("evidence-*.json"))
    assert len(draft_files) == 1, f"Expected 1 draft file, got: {draft_files}"


def test_evidence_draft_not_appended_to_canonical(tmp_path: Path) -> None:
    """--draft must NOT append to evidence.jsonl."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_evidence_add(
        tmp_path,
        "--kind", "commit",
        "--description", "draft only",
        "--draft",
    )

    evidence_file = tmp_path / ".spine" / "evidence.jsonl"
    lines = [l for l in evidence_file.read_text().splitlines() if l.strip()]
    assert len(lines) == 0, "Draft must not appear in evidence.jsonl"


def test_evidence_draft_file_contains_correct_fields(tmp_path: Path) -> None:
    """Draft JSON file contains record fields + _record_type."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_evidence_add(
        tmp_path,
        "--kind", "pr",
        "--description", "PR draft",
        "--url", "https://example.com/pr/1",
        "--draft",
    )

    drafts_dir = tmp_path / ".spine" / "drafts"
    draft_files = list(drafts_dir.glob("evidence-*.json"))
    assert len(draft_files) == 1

    data = json.loads(draft_files[0].read_text())
    assert data["_record_type"] == "evidence"
    assert data["kind"] == "pr"
    assert data["description"] == "PR draft"
    assert data["evidence_url"] == "https://example.com/pr/1"
    assert "created_at" in data


def test_evidence_draft_id_in_output(tmp_path: Path) -> None:
    """CLI output should include the draft ID and promotion hint."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout = run_evidence_add(
        tmp_path,
        "--kind", "commit",
        "--description", "a draft",
        "--draft",
    )
    assert exit_code == 0
    assert "Draft ID:" in stdout or "draft saved" in stdout.lower()
    assert "spine drafts confirm" in stdout


def test_evidence_draft_deterministic_naming(tmp_path: Path) -> None:
    """Draft filename prefix matches expected pattern evidence-YYYYMMDDTHHMMSS."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_evidence_add(tmp_path, "--kind", "commit", "--description", "x", "--draft")

    drafts_dir = tmp_path / ".spine" / "drafts"
    files = list(drafts_dir.glob("evidence-*.json"))
    assert len(files) == 1
    stem = files[0].stem
    assert stem.startswith("evidence-"), f"Expected evidence- prefix, got: {stem}"
    # After prefix, should be a timestamp-like string (digits and T)
    ts_part = stem[len("evidence-"):]
    assert len(ts_part) >= 15, f"Timestamp part too short: {ts_part!r}"
    assert ts_part[0].isdigit(), f"Timestamp should start with digit: {ts_part}"


# ---------------------------------------------------------------------------
# Draft decision creation
# ---------------------------------------------------------------------------


def test_decision_draft_creates_file_in_drafts_dir(tmp_path: Path) -> None:
    """--draft stores decision under .spine/drafts/ not decisions.jsonl."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout = run_decision_add(
        tmp_path,
        "--title", "Draft decision",
        "--why", "Testing drafts",
        "--decision", "Use draft system",
        "--draft",
    )
    assert exit_code == 0, stdout

    drafts_dir = tmp_path / ".spine" / "drafts"
    assert drafts_dir.exists()
    draft_files = list(drafts_dir.glob("decision-*.json"))
    assert len(draft_files) == 1


def test_decision_draft_not_appended_to_canonical(tmp_path: Path) -> None:
    """--draft must NOT append to decisions.jsonl."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_decision_add(
        tmp_path,
        "--title", "Draft only",
        "--why", "Test",
        "--decision", "Stay draft",
        "--draft",
    )

    decisions_file = tmp_path / ".spine" / "decisions.jsonl"
    lines = [l for l in decisions_file.read_text().splitlines() if l.strip()]
    assert len(lines) == 0, "Draft must not appear in decisions.jsonl"


def test_decision_draft_file_contains_correct_fields(tmp_path: Path) -> None:
    """Draft JSON file contains record fields + _record_type."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_decision_add(
        tmp_path,
        "--title", "Use pydantic",
        "--why", "Type safety",
        "--decision", "Adopt pydantic v2",
        "--alternatives", "attrs, dataclasses",
        "--draft",
    )

    drafts_dir = tmp_path / ".spine" / "drafts"
    draft_files = list(drafts_dir.glob("decision-*.json"))
    assert len(draft_files) == 1

    data = json.loads(draft_files[0].read_text())
    assert data["_record_type"] == "decision"
    assert data["title"] == "Use pydantic"
    assert data["why"] == "Type safety"
    assert data["decision"] == "Adopt pydantic v2"
    assert data["alternatives"] == ["attrs", "dataclasses"]
    assert "created_at" in data


def test_decision_draft_id_in_output(tmp_path: Path) -> None:
    """CLI output includes draft ID and promotion hint."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout = run_decision_add(
        tmp_path,
        "--title", "T",
        "--why", "W",
        "--decision", "D",
        "--draft",
    )
    assert exit_code == 0
    assert "Draft ID:" in stdout or "draft saved" in stdout.lower()
    assert "spine drafts confirm" in stdout


# ---------------------------------------------------------------------------
# Drafts list
# ---------------------------------------------------------------------------


def test_drafts_list_empty(tmp_path: Path) -> None:
    """spine drafts list shows 'No pending drafts' when none exist."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout = run_drafts_list(tmp_path)
    assert exit_code == 0, stdout
    assert "No pending drafts" in stdout


def test_drafts_list_shows_evidence_draft(tmp_path: Path) -> None:
    """spine drafts list shows an evidence draft."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_evidence_add(tmp_path, "--kind", "commit", "--description", "my draft", "--draft")

    exit_code, stdout = run_drafts_list(tmp_path)
    assert exit_code == 0, stdout
    assert "evidence" in stdout.lower()
    assert "my draft" in stdout


def test_drafts_list_shows_decision_draft(tmp_path: Path) -> None:
    """spine drafts list shows a decision draft."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_decision_add(tmp_path, "--title", "My draft decision", "--why", "W", "--decision", "D", "--draft")

    exit_code, stdout = run_drafts_list(tmp_path)
    assert exit_code == 0, stdout
    assert "decision" in stdout.lower()
    assert "My draft decision" in stdout


def test_drafts_list_multiple_drafts(tmp_path: Path) -> None:
    """spine drafts list shows multiple drafts."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_evidence_add(tmp_path, "--kind", "commit", "--description", "ev draft", "--draft")
    run_decision_add(tmp_path, "--title", "dec draft", "--why", "W", "--decision", "D", "--draft")

    exit_code, stdout = run_drafts_list(tmp_path)
    assert exit_code == 0, stdout
    assert "ev draft" in stdout
    assert "dec draft" in stdout


# ---------------------------------------------------------------------------
# Drafts confirm (promotion)
# ---------------------------------------------------------------------------


def test_drafts_confirm_evidence_promotes_to_canonical(tmp_path: Path) -> None:
    """spine drafts confirm promotes evidence draft to evidence.jsonl."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_evidence_add(tmp_path, "--kind", "commit", "--description", "promote me", "--draft")

    # Get the draft_id from the draft file
    drafts_dir = tmp_path / ".spine" / "drafts"
    draft_files = list(drafts_dir.glob("evidence-*.json"))
    assert len(draft_files) == 1
    draft_id = draft_files[0].stem

    exit_code, stdout = run_drafts_confirm(tmp_path, draft_id)
    assert exit_code == 0, stdout

    # Draft file should be gone
    assert not draft_files[0].exists(), "Draft file should be deleted after confirm"

    # evidence.jsonl should contain the record
    evidence_file = tmp_path / ".spine" / "evidence.jsonl"
    lines = [l for l in evidence_file.read_text().splitlines() if l.strip()]
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["kind"] == "commit"
    assert record["description"] == "promote me"
    assert "_record_type" not in record, "_record_type must not appear in canonical record"


def test_drafts_confirm_decision_promotes_to_canonical(tmp_path: Path) -> None:
    """spine drafts confirm promotes decision draft to decisions.jsonl."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_decision_add(
        tmp_path,
        "--title", "Confirmed decision",
        "--why", "Good reason",
        "--decision", "Decided",
        "--draft",
    )

    drafts_dir = tmp_path / ".spine" / "drafts"
    draft_files = list(drafts_dir.glob("decision-*.json"))
    assert len(draft_files) == 1
    draft_id = draft_files[0].stem

    exit_code, stdout = run_drafts_confirm(tmp_path, draft_id)
    assert exit_code == 0, stdout

    # Draft file should be gone
    assert not draft_files[0].exists()

    # decisions.jsonl should contain the record
    decisions_file = tmp_path / ".spine" / "decisions.jsonl"
    lines = [l for l in decisions_file.read_text().splitlines() if l.strip()]
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["title"] == "Confirmed decision"
    assert record["why"] == "Good reason"
    assert "_record_type" not in record


def test_drafts_confirm_nonexistent_id_fails(tmp_path: Path) -> None:
    """Confirming a nonexistent draft ID exits with non-zero code."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout = run_drafts_confirm(tmp_path, "evidence-99999999T999999999999")
    assert exit_code != 0, "Should fail for nonexistent draft"
    assert "not found" in stdout.lower()


def test_drafts_confirm_removes_from_list(tmp_path: Path) -> None:
    """After confirm, the draft no longer appears in drafts list."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_evidence_add(tmp_path, "--kind", "commit", "--description", "to remove", "--draft")

    drafts_dir = tmp_path / ".spine" / "drafts"
    draft_id = list(drafts_dir.glob("evidence-*.json"))[0].stem

    run_drafts_confirm(tmp_path, draft_id)

    exit_code, stdout = run_drafts_list(tmp_path)
    assert exit_code == 0
    assert "No pending drafts" in stdout


# ---------------------------------------------------------------------------
# Default exclusion from canonical surfaces
# ---------------------------------------------------------------------------


def test_draft_excluded_from_evidence_jsonl(tmp_path: Path) -> None:
    """A draft evidence record never appears in evidence.jsonl."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    # Add one canonical and one draft
    run_evidence_add(tmp_path, "--kind", "commit", "--description", "canonical")
    run_evidence_add(tmp_path, "--kind", "pr", "--description", "draft only", "--draft")

    evidence_file = tmp_path / ".spine" / "evidence.jsonl"
    lines = [l for l in evidence_file.read_text().splitlines() if l.strip()]
    assert len(lines) == 1, "Only canonical record should be in evidence.jsonl"
    assert json.loads(lines[0])["description"] == "canonical"


def test_draft_excluded_from_decisions_jsonl(tmp_path: Path) -> None:
    """A draft decision record never appears in decisions.jsonl."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_decision_add(tmp_path, "--title", "Canonical", "--why", "W", "--decision", "D")
    run_decision_add(tmp_path, "--title", "Draft only", "--why", "W", "--decision", "D", "--draft")

    decisions_file = tmp_path / ".spine" / "decisions.jsonl"
    lines = [l for l in decisions_file.read_text().splitlines() if l.strip()]
    assert len(lines) == 1
    assert json.loads(lines[0])["title"] == "Canonical"


# ---------------------------------------------------------------------------
# --cwd support
# ---------------------------------------------------------------------------


def test_evidence_draft_with_cwd(tmp_path: Path) -> None:
    """evidence add --draft respects --cwd."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    result = runner.invoke(app, [
        "evidence", "add",
        "--cwd", str(tmp_path),
        "--kind", "commit",
        "--description", "cwd draft",
        "--draft",
    ])
    assert result.exit_code == 0, result.output

    drafts_dir = tmp_path / ".spine" / "drafts"
    assert any(drafts_dir.glob("evidence-*.json"))


def test_decision_draft_with_cwd(tmp_path: Path) -> None:
    """decision add --draft respects --cwd."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    result = runner.invoke(app, [
        "decision", "add",
        "--cwd", str(tmp_path),
        "--title", "CWD draft",
        "--why", "W",
        "--decision", "D",
        "--draft",
    ])
    assert result.exit_code == 0, result.output

    drafts_dir = tmp_path / ".spine" / "drafts"
    assert any(drafts_dir.glob("decision-*.json"))


def test_drafts_confirm_with_cwd(tmp_path: Path) -> None:
    """drafts confirm --cwd promotes correctly."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    runner.invoke(app, [
        "evidence", "add",
        "--cwd", str(tmp_path),
        "--kind", "commit",
        "--description", "cwd confirm test",
        "--draft",
    ])

    drafts_dir = tmp_path / ".spine" / "drafts"
    draft_id = list(drafts_dir.glob("evidence-*.json"))[0].stem

    result = runner.invoke(app, [
        "drafts", "confirm", draft_id,
        "--cwd", str(tmp_path),
    ])
    assert result.exit_code == 0, result.output

    evidence_file = tmp_path / ".spine" / "evidence.jsonl"
    lines = [l for l in evidence_file.read_text().splitlines() if l.strip()]
    assert len(lines) == 1
    assert json.loads(lines[0])["description"] == "cwd confirm test"


# ---------------------------------------------------------------------------
# Multiple drafts — no interference
# ---------------------------------------------------------------------------


def test_multiple_evidence_drafts_stored_separately(tmp_path: Path) -> None:
    """Multiple evidence drafts each get their own file."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    for i in range(3):
        run_evidence_add(tmp_path, "--kind", "commit", "--description", f"draft {i}", "--draft")

    drafts_dir = tmp_path / ".spine" / "drafts"
    files = list(drafts_dir.glob("evidence-*.json"))
    assert len(files) == 3


def test_confirm_one_draft_leaves_others(tmp_path: Path) -> None:
    """Confirming one draft does not affect other drafts."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    for i in range(2):
        run_evidence_add(tmp_path, "--kind", "commit", "--description", f"draft {i}", "--draft")

    drafts_dir = tmp_path / ".spine" / "drafts"
    files = sorted(drafts_dir.glob("evidence-*.json"))
    assert len(files) == 2

    # Confirm only the first
    first_id = files[0].stem
    run_drafts_confirm(tmp_path, first_id)

    remaining = list(drafts_dir.glob("evidence-*.json"))
    assert len(remaining) == 1
    assert remaining[0] != files[0], "The other draft should remain"

    evidence_file = tmp_path / ".spine" / "evidence.jsonl"
    lines = [l for l in evidence_file.read_text().splitlines() if l.strip()]
    assert len(lines) == 1
