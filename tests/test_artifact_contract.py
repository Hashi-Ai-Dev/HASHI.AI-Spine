"""Tests for Issue #23 — Artifact ergonomics contract.

Verifies:
- Deterministic naming conventions (YYYYMMDD_HHMMSS for briefs, YYYY-MM-DD for reviews)
- latest.md alias is a regular file updated on each generation
- artifact_manifest.json is created and updated on brief/review generation
- manifest has expected structure and relative paths
- JSON CLI output includes canonical_path and latest_path
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from typer.testing import CliRunner

from spine.main import app

runner = CliRunner()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_git_repo(tmp_path: Path) -> Path:
    (tmp_path / ".git").mkdir()
    return tmp_path


def run_init(tmp_path: Path) -> None:
    result = runner.invoke(app, ["init", "--cwd", str(tmp_path)])
    assert result.exit_code == 0, result.output


def run_brief(tmp_path: Path, target: str, *, json_out: bool = False) -> tuple[int, str]:
    import os
    args = ["brief", "--target", target]
    if json_out:
        args.append("--json")
    original = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, args)
    finally:
        os.chdir(original)
    return result.exit_code, result.output


def run_review(tmp_path: Path, *, json_out: bool = False) -> tuple[int, str]:
    args = ["review", "weekly", "--cwd", str(tmp_path)]
    if json_out:
        args.append("--json")
    result = runner.invoke(app, args)
    return result.exit_code, result.output


# ---------------------------------------------------------------------------
# Brief naming convention
# ---------------------------------------------------------------------------

BRIEF_TIMESTAMP_PATTERN = re.compile(r"^\d{8}_\d{6}\.md$")


def test_brief_canonical_name_matches_timestamp_pattern(tmp_path: Path) -> None:
    """Brief canonical file name must match YYYYMMDD_HHMMSS.md pattern."""
    make_git_repo(tmp_path)
    run_init(tmp_path)
    run_brief(tmp_path, "claude")

    briefs_dir = tmp_path / ".spine" / "briefs" / "claude"
    timestamped = [f for f in briefs_dir.iterdir() if f.name != "latest.md"]
    assert len(timestamped) >= 1, f"No timestamped brief files in {briefs_dir}"
    for f in timestamped:
        assert BRIEF_TIMESTAMP_PATTERN.match(f.name), (
            f"Brief file name '{f.name}' does not match YYYYMMDD_HHMMSS.md pattern"
        )


def test_brief_latest_is_regular_file(tmp_path: Path) -> None:
    """latest.md must be a regular file (not a symlink)."""
    make_git_repo(tmp_path)
    run_init(tmp_path)
    run_brief(tmp_path, "claude")

    latest = tmp_path / ".spine" / "briefs" / "claude" / "latest.md"
    assert latest.exists(), "latest.md not found"
    assert latest.is_file() and not latest.is_symlink(), (
        "latest.md must be a regular file, not a symlink"
    )


def test_brief_codex_canonical_name_matches_timestamp_pattern(tmp_path: Path) -> None:
    """Codex brief canonical file name must match YYYYMMDD_HHMMSS.md pattern."""
    make_git_repo(tmp_path)
    run_init(tmp_path)
    run_brief(tmp_path, "codex")

    briefs_dir = tmp_path / ".spine" / "briefs" / "codex"
    timestamped = [f for f in briefs_dir.iterdir() if f.name != "latest.md"]
    assert len(timestamped) >= 1
    for f in timestamped:
        assert BRIEF_TIMESTAMP_PATTERN.match(f.name), (
            f"Codex brief file name '{f.name}' does not match YYYYMMDD_HHMMSS.md pattern"
        )


# ---------------------------------------------------------------------------
# Review naming convention
# ---------------------------------------------------------------------------

REVIEW_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")


def test_review_canonical_name_matches_date_pattern(tmp_path: Path) -> None:
    """Review canonical file name must match YYYY-MM-DD.md pattern."""
    make_git_repo(tmp_path)
    run_init(tmp_path)
    run_review(tmp_path)

    reviews_dir = tmp_path / ".spine" / "reviews"
    dated = [f for f in reviews_dir.iterdir() if f.name != "latest.md"]
    assert len(dated) >= 1, f"No dated review files in {reviews_dir}"
    for f in dated:
        assert REVIEW_DATE_PATTERN.match(f.name), (
            f"Review file name '{f.name}' does not match YYYY-MM-DD.md pattern"
        )


def test_review_latest_is_regular_file(tmp_path: Path) -> None:
    """reviews/latest.md must be a regular file (not a symlink)."""
    make_git_repo(tmp_path)
    run_init(tmp_path)
    run_review(tmp_path)

    latest = tmp_path / ".spine" / "reviews" / "latest.md"
    assert latest.exists(), "latest.md not found"
    assert latest.is_file() and not latest.is_symlink(), (
        "reviews/latest.md must be a regular file, not a symlink"
    )


# ---------------------------------------------------------------------------
# Artifact manifest — briefs
# ---------------------------------------------------------------------------

def test_brief_generates_artifact_manifest(tmp_path: Path) -> None:
    """Generating a brief must create .spine/artifact_manifest.json."""
    make_git_repo(tmp_path)
    run_init(tmp_path)
    run_brief(tmp_path, "claude")

    manifest_path = tmp_path / ".spine" / "artifact_manifest.json"
    assert manifest_path.exists(), "artifact_manifest.json not found after brief generation"


def test_brief_manifest_has_expected_structure(tmp_path: Path) -> None:
    """artifact_manifest.json must be valid JSON with expected top-level keys."""
    make_git_repo(tmp_path)
    run_init(tmp_path)
    run_brief(tmp_path, "claude")

    manifest_path = tmp_path / ".spine" / "artifact_manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert data.get("contract_version") == "1", "contract_version must be '1'"
    assert "briefs" in data, "manifest must have 'briefs' section"
    assert "claude" in data["briefs"], "briefs section must have 'claude' entry"
    entry = data["briefs"]["claude"]
    assert "latest" in entry, "claude brief entry must have 'latest' path"
    assert "last_generated_at" in entry, "claude brief entry must have 'last_generated_at'"


def test_brief_manifest_latest_path_is_relative(tmp_path: Path) -> None:
    """Manifest latest path must be relative (portable across checkouts)."""
    make_git_repo(tmp_path)
    run_init(tmp_path)
    run_brief(tmp_path, "claude")

    manifest_path = tmp_path / ".spine" / "artifact_manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    latest_path = data["briefs"]["claude"]["latest"]

    # Must be relative (not absolute, not starting with /)
    assert not latest_path.startswith("/"), (
        f"Manifest latest path must be relative, got: {latest_path!r}"
    )
    # Must point to expected location
    assert "briefs" in latest_path and "claude" in latest_path and "latest.md" in latest_path


def test_brief_manifest_updated_on_codex_generation(tmp_path: Path) -> None:
    """Generating codex brief adds codex entry to manifest without removing claude."""
    make_git_repo(tmp_path)
    run_init(tmp_path)
    run_brief(tmp_path, "claude")
    run_brief(tmp_path, "codex")

    manifest_path = tmp_path / ".spine" / "artifact_manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert "claude" in data["briefs"], "claude entry must persist after codex generation"
    assert "codex" in data["briefs"], "codex entry must appear after codex generation"


def test_brief_manifest_last_generated_at_is_iso8601(tmp_path: Path) -> None:
    """Manifest last_generated_at must be an ISO 8601 timestamp string."""
    from datetime import datetime, timezone
    make_git_repo(tmp_path)
    run_init(tmp_path)
    run_brief(tmp_path, "claude")

    manifest_path = tmp_path / ".spine" / "artifact_manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    ts_str = data["briefs"]["claude"]["last_generated_at"]

    # Should parse as ISO 8601 without raising
    dt = datetime.fromisoformat(ts_str)
    assert dt.tzinfo is not None, "Timestamp must be timezone-aware"


# ---------------------------------------------------------------------------
# Artifact manifest — reviews
# ---------------------------------------------------------------------------

def test_review_generates_artifact_manifest(tmp_path: Path) -> None:
    """Generating a review must create .spine/artifact_manifest.json."""
    make_git_repo(tmp_path)
    run_init(tmp_path)
    run_review(tmp_path)

    manifest_path = tmp_path / ".spine" / "artifact_manifest.json"
    assert manifest_path.exists(), "artifact_manifest.json not found after review generation"


def test_review_manifest_has_expected_structure(tmp_path: Path) -> None:
    """Manifest reviews section must have 'weekly' entry with required fields."""
    make_git_repo(tmp_path)
    run_init(tmp_path)
    run_review(tmp_path)

    manifest_path = tmp_path / ".spine" / "artifact_manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert "reviews" in data, "manifest must have 'reviews' section"
    assert "weekly" in data["reviews"], "reviews section must have 'weekly' entry"
    entry = data["reviews"]["weekly"]
    assert "latest" in entry, "weekly review entry must have 'latest' path"
    assert "last_generated_at" in entry, "weekly review entry must have 'last_generated_at'"


def test_review_manifest_latest_path_is_relative(tmp_path: Path) -> None:
    """Review manifest latest path must be relative."""
    make_git_repo(tmp_path)
    run_init(tmp_path)
    run_review(tmp_path)

    manifest_path = tmp_path / ".spine" / "artifact_manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    latest_path = data["reviews"]["weekly"]["latest"]

    assert not latest_path.startswith("/"), (
        f"Review manifest latest path must be relative, got: {latest_path!r}"
    )
    assert "reviews" in latest_path and "latest.md" in latest_path


def test_brief_and_review_coexist_in_manifest(tmp_path: Path) -> None:
    """Manifest must accumulate entries from both brief and review generations."""
    make_git_repo(tmp_path)
    run_init(tmp_path)
    run_brief(tmp_path, "claude")
    run_review(tmp_path)

    manifest_path = tmp_path / ".spine" / "artifact_manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert "briefs" in data, "briefs section missing after brief + review generation"
    assert "reviews" in data, "reviews section missing after brief + review generation"


# ---------------------------------------------------------------------------
# JSON CLI output — canonical_path and latest_path contract
# ---------------------------------------------------------------------------

def test_brief_json_output_includes_canonical_and_latest_paths(tmp_path: Path) -> None:
    """spine brief --json must output canonical_path and latest_path."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, output = run_brief(tmp_path, "claude", json_out=True)
    assert exit_code == 0, output

    data = json.loads(output)
    assert "canonical_path" in data, "JSON output must include canonical_path"
    assert "latest_path" in data, "JSON output must include latest_path"
    assert data["canonical_path"].endswith(".md"), "canonical_path must be a .md file"
    assert data["latest_path"].endswith("latest.md"), "latest_path must end with latest.md"


def test_review_json_output_includes_canonical_and_latest_paths(tmp_path: Path) -> None:
    """spine review weekly --json must output canonical_path and latest_path."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    exit_code, output = run_review(tmp_path, json_out=True)
    assert exit_code == 0, output

    data = json.loads(output)
    assert "canonical_path" in data, "JSON output must include canonical_path"
    assert "latest_path" in data, "JSON output must include latest_path"
    assert data["canonical_path"].endswith(".md"), "canonical_path must be a .md file"
    assert data["latest_path"].endswith("latest.md"), "latest_path must end with latest.md"


def test_brief_json_canonical_name_matches_timestamp_pattern(tmp_path: Path) -> None:
    """canonical_path in JSON output must end with a YYYYMMDD_HHMMSS.md filename."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    _, output = run_brief(tmp_path, "claude", json_out=True)
    data = json.loads(output)
    filename = Path(data["canonical_path"]).name
    assert BRIEF_TIMESTAMP_PATTERN.match(filename), (
        f"canonical_path filename '{filename}' does not match YYYYMMDD_HHMMSS.md pattern"
    )


def test_review_json_canonical_name_matches_date_pattern(tmp_path: Path) -> None:
    """canonical_path in JSON output must end with a YYYY-MM-DD.md filename."""
    make_git_repo(tmp_path)
    run_init(tmp_path)

    _, output = run_review(tmp_path, json_out=True)
    data = json.loads(output)
    filename = Path(data["canonical_path"]).name
    assert REVIEW_DATE_PATTERN.match(filename), (
        f"canonical_path filename '{filename}' does not match YYYY-MM-DD.md pattern"
    )
