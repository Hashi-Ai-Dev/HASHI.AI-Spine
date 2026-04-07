"""Tests for spine review-weekly command (Phase 2)."""

from __future__ import annotations

from pathlib import Path

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


def run_review_weekly(tmp_path: Path, *extra_args: str) -> tuple[int, str, str]:
    result = runner.invoke(app, ["review", "weekly", "--cwd", str(tmp_path), *extra_args])
    return result.exit_code, result.output, ""


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_review_weekly_creates_dated_file(tmp_path: Path) -> None:
    """review-weekly creates a file in .spine/reviews/YYYY-MM-DD.md."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_review_weekly(tmp_path)
    assert exit_code == 0, stdout

    reviews_dir = tmp_path / ".spine" / "reviews"
    assert reviews_dir.is_dir()

    # Find the dated review file (today's UTC date - matches service)
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    dated_file = reviews_dir / f"{today}.md"
    assert dated_file.exists(), f"Expected {dated_file} to exist, files: {list(reviews_dir.iterdir())}"


def test_review_weekly_creates_latest_symlink(tmp_path: Path) -> None:
    """review-weekly also creates/updates .spine/reviews/latest.md."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_review_weekly(tmp_path)
    assert exit_code == 0, stdout

    latest = tmp_path / ".spine" / "reviews" / "latest.md"
    assert latest.exists()


def test_review_weekly_contains_mission_state(tmp_path: Path) -> None:
    """Review contains a Mission State section with mission details."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_review_weekly(tmp_path)
    assert exit_code == 0, stdout

    latest = tmp_path / ".spine" / "reviews" / "latest.md"
    content = latest.read_text()

    assert "## Mission State" in content
    assert "**Title:**" in content or "Title:" in content
    assert "**Status:**" in content or "Status:" in content


def test_review_weekly_contains_evidence_section(tmp_path: Path) -> None:
    """Review contains an Evidence section (empty if none)."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_review_weekly(tmp_path)
    assert exit_code == 0, stdout

    latest = tmp_path / ".spine" / "reviews" / "latest.md"
    content = latest.read_text()

    assert "## Evidence" in content
    # Empty evidence shows placeholder text
    assert "No evidence" in content or "No evidence" in content


def test_review_weekly_contains_decisions_section(tmp_path: Path) -> None:
    """Review contains a Decisions section (empty if none)."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_review_weekly(tmp_path)
    assert exit_code == 0, stdout

    latest = tmp_path / ".spine" / "reviews" / "latest.md"
    content = latest.read_text()

    assert "## Decisions" in content
    # Empty decisions shows placeholder text
    assert "No decisions" in content or "No decisions" in content


def test_review_weekly_contains_drift_section(tmp_path: Path) -> None:
    """Review contains a Drift section (empty if none)."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_review_weekly(tmp_path)
    assert exit_code == 0, stdout

    latest = tmp_path / ".spine" / "reviews" / "latest.md"
    content = latest.read_text()

    assert "## Drift" in content
    # Empty drift shows placeholder text
    assert "No drift" in content or "No drift" in content


def test_review_weekly_days_parameter(tmp_path: Path) -> None:
    """--days parameter controls aggregation window."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_review_weekly(tmp_path, "--days", "14")
    assert exit_code == 0, stdout

    latest = tmp_path / ".spine" / "reviews" / "latest.md"
    content = latest.read_text()

    # The review should mention the period
    assert "Last 14 days" in content


def test_review_weekly_recommendation_continue(tmp_path: Path) -> None:
    """--recommendation accepts 'continue'."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_review_weekly(tmp_path, "--recommendation", "continue")
    assert exit_code == 0, stdout

    latest = tmp_path / ".spine" / "reviews" / "latest.md"
    content = latest.read_text()
    assert "**CONTINUE**" in content or "**continue**" in content


def test_review_weekly_recommendation_narrow(tmp_path: Path) -> None:
    """--recommendation accepts 'narrow'."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_review_weekly(tmp_path, "--recommendation", "narrow")
    assert exit_code == 0, stdout

    latest = tmp_path / ".spine" / "reviews" / "latest.md"
    content = latest.read_text()
    assert "**NARROW**" in content or "**narrow**" in content


def test_review_weekly_recommendation_pivot(tmp_path: Path) -> None:
    """--recommendation accepts 'pivot'."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_review_weekly(tmp_path, "--recommendation", "pivot")
    assert exit_code == 0, stdout

    latest = tmp_path / ".spine" / "reviews" / "latest.md"
    content = latest.read_text()
    assert "**PIVOT**" in content or "**pivot**" in content


def test_review_weekly_recommendation_kill(tmp_path: Path) -> None:
    """--recommendation accepts 'kill'."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_review_weekly(tmp_path, "--recommendation", "kill")
    assert exit_code == 0, stdout

    latest = tmp_path / ".spine" / "reviews" / "latest.md"
    content = latest.read_text()
    assert "**KILL**" in content or "**kill**" in content


def test_review_weekly_recommendation_ship_as_is(tmp_path: Path) -> None:
    """--recommendation accepts 'ship_as_is'."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_review_weekly(tmp_path, "--recommendation", "ship_as_is")
    assert exit_code == 0, stdout

    latest = tmp_path / ".spine" / "reviews" / "latest.md"
    content = latest.read_text()
    assert "**SHIP_AS_IS**" in content or "**ship_as_is**" in content


def test_review_weekly_invalid_recommendation_rejected(tmp_path: Path) -> None:
    """Invalid recommendation value is rejected with exit code 1."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, stdout, _ = run_review_weekly(tmp_path, "--recommendation", "invalid_value")
    assert exit_code == 1, f"Expected exit code 1, got {exit_code}. Output: {stdout}"
    assert "recommendation" in stdout.lower() or "must be one of" in stdout.lower()
