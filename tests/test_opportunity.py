"""Tests for spine opportunity-score command (Phase 2)."""

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


def run_init(tmp_path: Path, *extra_args: str) -> tuple[int, str, str]:
    result = runner.invoke(app, ["init", "--cwd", str(tmp_path), *extra_args])
    return result.exit_code, result.output, ""


def run_opportunity_score(
    tmp_path: Path,
    *extra_args: str,
) -> tuple[int, str, str]:
    original = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["opportunity", "score", *extra_args])
    finally:
        os.chdir(original)
    return result.exit_code, result.output, ""


def read_opportunities_jsonl(tmp_path: Path) -> list[dict]:
    """Read all records from .spine/opportunities.jsonl."""
    path = tmp_path / ".spine" / "opportunities.jsonl"
    if not path.exists():
        return []
    records = []
    for line in path.read_text().splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


# ---------------------------------------------------------------------------
# Tests: appending to opportunities.jsonl
# ---------------------------------------------------------------------------

def test_score_appends_to_opportunities_jsonl(tmp_path: Path) -> None:
    """opportunity-score appends a record to opportunities.jsonl."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_opportunity_score(
        tmp_path,
        "Test Opportunity",
        "--pain", "4",
    )
    assert exit_code == 0, stdout

    records = read_opportunities_jsonl(tmp_path)
    assert len(records) == 1
    assert records[0]["title"] == "Test Opportunity"


def test_score_multiple_opportunities_append(tmp_path: Path) -> None:
    """Multiple invocations of opportunity-score each append a new record."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_opportunity_score(tmp_path, "Opportunity A", "--pain", "5")
    run_opportunity_score(tmp_path, "Opportunity B", "--founder-fit", "5")

    records = read_opportunities_jsonl(tmp_path)
    assert len(records) == 2
    assert records[0]["title"] == "Opportunity A"
    assert records[1]["title"] == "Opportunity B"


# ---------------------------------------------------------------------------
# Tests: all 6 score parameters
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("param_name,param_value", [
    ("--pain", "5"),
    ("--founder-fit", "5"),
    ("--time-to-proof", "5"),
    ("--monetization", "5"),
    ("--sprawl-risk", "5"),
    ("--maintenance", "5"),
])
def test_score_all_six_parameters_accepted(
    tmp_path: Path,
    param_name: str,
    param_value: str,
) -> None:
    """All 6 score parameters (pain, founder-fit, time-to-proof, monetization, sprawl-risk, maintenance) are accepted."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_opportunity_score(
        tmp_path,
        "Test Opportunity",
        param_name, param_value,
    )
    assert exit_code == 0, stdout


def test_score_all_parameters_together(tmp_path: Path) -> None:
    """All 6 score parameters can be provided together."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_opportunity_score(
        tmp_path,
        "Full Scoring",
        "--pain", "4",
        "--founder-fit", "3",
        "--time-to-proof", "5",
        "--monetization", "2",
        "--sprawl-risk", "4",
        "--maintenance", "3",
    )
    assert exit_code == 0, stdout

    records = read_opportunities_jsonl(tmp_path)
    assert len(records) == 1
    scores = records[0]["scores"]
    assert scores["pain"] == 4
    assert scores["founder_fit"] == 3
    assert scores["time_to_proof"] == 5
    assert scores["monetization"] == 2
    assert scores["sprawl_risk"] == 4
    assert scores["maintenance_burden"] == 3


# ---------------------------------------------------------------------------
# Tests: score validation — out of range
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("param_name", [
    "--pain",
    "--founder-fit",
    "--time-to-proof",
    "--monetization",
    "--sprawl-risk",
    "--maintenance",
])
def test_score_rejects_zero(tmp_path: Path, param_name: str) -> None:
    """Score value of 0 is rejected with a validation error."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_opportunity_score(
        tmp_path,
        "Test",
        param_name, "0",
    )
    assert exit_code == 1
    assert "Validation error" in stdout


@pytest.mark.parametrize("param_name", [
    "--pain",
    "--founder-fit",
    "--time-to-proof",
    "--monetization",
    "--sprawl-risk",
    "--maintenance",
])
def test_score_rejects_six(tmp_path: Path, param_name: str) -> None:
    """Score value of 6 is rejected with a validation error."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_opportunity_score(
        tmp_path,
        "Test",
        param_name, "6",
    )
    assert exit_code == 1
    assert "Validation error" in stdout


# ---------------------------------------------------------------------------
# Tests: title validation
# ---------------------------------------------------------------------------

def test_score_rejects_empty_title(tmp_path: Path) -> None:
    """opportunity-score rejects an empty title."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_opportunity_score(tmp_path, "")
    assert exit_code == 1
    assert "Validation error" in stdout or "title" in stdout.lower()


def test_score_rejects_whitespace_only_title(tmp_path: Path) -> None:
    """opportunity-score rejects a whitespace-only title."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_opportunity_score(tmp_path, "   ")
    assert exit_code == 1


# ---------------------------------------------------------------------------
# Tests: total score deterministic computation
# ---------------------------------------------------------------------------

def test_score_total_score_is_deterministic(tmp_path: Path) -> None:
    """The total_score is computed deterministically from all 6 scores."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_opportunity_score(
        tmp_path,
        "Determinism Test",
        "--pain", "4",
        "--founder-fit", "3",
        "--time-to-proof", "5",
        "--monetization", "2",
        "--sprawl-risk", "4",
        "--maintenance", "3",
    )
    assert exit_code == 0, stdout

    records = read_opportunities_jsonl(tmp_path)
    assert len(records) == 1
    # Weights from OpportunityScoreModel:
    # pain=1.5, founder_fit=2.0, time_to_proof=2.0, monetization=1.0,
    # sprawl_risk=1.0, maintenance_burden=1.0
    # total_weight = 8.5
    # raw = 4*1.5 + 3*2.0 + 5*2.0 + 2*1.0 + 4*1.0 + 3*1.0
    #       = 6 + 6 + 10 + 2 + 4 + 3 = 31
    # total_score = round(31 / 8.5, 2) = round(3.647..., 2) = 3.65
    assert records[0]["total_score"] == 3.65


def test_score_total_score_different_values(tmp_path: Path) -> None:
    """Different score values produce a different total_score."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    run_opportunity_score(
        tmp_path,
        "All Ones",
        "--pain", "1",
        "--founder-fit", "1",
        "--time-to-proof", "1",
        "--monetization", "1",
        "--sprawl-risk", "1",
        "--maintenance", "1",
    )
    run_opportunity_score(
        tmp_path,
        "All Fives",
        "--pain", "5",
        "--founder-fit", "5",
        "--time-to-proof", "5",
        "--monetization", "5",
        "--sprawl-risk", "5",
        "--maintenance", "5",
    )

    records = read_opportunities_jsonl(tmp_path)
    # With all 1s: raw = 8.5, score = 1.0
    # With all 5s: raw = 42.5, score = 5.0
    assert records[0]["total_score"] == 1.0
    assert records[1]["total_score"] == 5.0