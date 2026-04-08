"""Issue #38 — Deterministic validation fixtures and contract harness.

Verifies core SPINE contracts using explicit, human-readable fixtures under
tests/fixtures/.  Every test here is:

  - deterministic: same fixtures, same repo setup, same result
  - readable: fixtures show exactly what the contract expects
  - extendable: add a fixture, add a test
  - CI-compatible: no external deps, no network, no runtime services

Contract surfaces covered:
  - mission.yaml structure (Pydantic model round-trip via fixtures)
  - artifact_manifest.json structure and required keys
  - JSON output shapes for all major --json commands
  - Exit code semantics for core command scenarios
  - --cwd external-repo targeting behavior
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from spine.main import app
from spine.models.mission import MissionModel

runner = CliRunner()

# ---------------------------------------------------------------------------
# Shared fixture directory helper
# ---------------------------------------------------------------------------

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def fixtures_dir() -> Path:
    """Return absolute path to tests/fixtures/."""
    return FIXTURES_DIR


# ---------------------------------------------------------------------------
# Shared repo helpers (same minimal pattern used across existing tests)
# ---------------------------------------------------------------------------


def make_git_repo(path: Path) -> Path:
    (path / ".git").mkdir(parents=True, exist_ok=True)
    return path


def spine_init(path: Path) -> None:
    result = runner.invoke(app, ["init", "--cwd", str(path)])
    assert result.exit_code == 0, f"spine init failed: {result.output}"


def run_cmd(args: list[str]) -> tuple[int, str]:
    result = runner.invoke(app, args)
    return result.exit_code, result.output


# ---------------------------------------------------------------------------
# 1. Fixture file integrity
# ---------------------------------------------------------------------------


class TestFixtureFileIntegrity:
    """Sanity checks: all fixture files exist and parse without error."""

    def test_mission_valid_yaml_exists_and_parses(self) -> None:
        path = fixtures_dir() / "mission_valid.yaml"
        assert path.exists(), f"Fixture missing: {path}"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict), "mission_valid.yaml must parse to a dict"

    def test_mission_minimal_yaml_exists_and_parses(self) -> None:
        path = fixtures_dir() / "mission_minimal.yaml"
        assert path.exists(), f"Fixture missing: {path}"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict), "mission_minimal.yaml must parse to a dict"

    def test_artifact_manifest_full_json_exists_and_parses(self) -> None:
        path = fixtures_dir() / "artifact_manifest_full.json"
        assert path.exists(), f"Fixture missing: {path}"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict), "artifact_manifest_full.json must parse to a dict"

    def test_artifact_manifest_minimal_json_exists_and_parses(self) -> None:
        path = fixtures_dir() / "artifact_manifest_minimal.json"
        assert path.exists(), f"Fixture missing: {path}"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict), "artifact_manifest_minimal.json must parse to a dict"

    def test_exit_codes_json_exists_and_parses(self) -> None:
        path = fixtures_dir() / "exit_codes.json"
        assert path.exists(), f"Fixture missing: {path}"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "exit_code_semantics" in data
        assert "command_scenarios" in data

    @pytest.mark.parametrize("shape_name", [
        "doctor.json",
        "check_before_pr.json",
        "mission_show.json",
        "review_handoff.json",
        "brief.json",
        "drift_scan.json",
    ])
    def test_json_shape_fixture_exists_and_valid(self, shape_name: str) -> None:
        path = fixtures_dir() / "json_shapes" / shape_name
        assert path.exists(), f"Shape fixture missing: {path}"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "required_keys" in data, f"{shape_name} must have 'required_keys'"
        assert "key_types" in data, f"{shape_name} must have 'key_types'"
        assert isinstance(data["required_keys"], list), "required_keys must be a list"
        assert isinstance(data["key_types"], dict), "key_types must be a dict"


# ---------------------------------------------------------------------------
# 2. mission.yaml structure contracts (fixture → Pydantic round-trip)
# ---------------------------------------------------------------------------


class TestMissionYamlFixtureContract:
    """Validate mission.yaml fixtures round-trip through MissionModel."""

    def test_mission_valid_fixture_passes_pydantic_validation(self) -> None:
        """mission_valid.yaml must load without Pydantic validation error."""
        raw = (fixtures_dir() / "mission_valid.yaml").read_text(encoding="utf-8")
        model = MissionModel.from_yaml(raw)
        assert model.version == 1
        assert model.status in ("active", "paused", "complete", "killed")
        assert isinstance(model.id, str) and model.id
        assert isinstance(model.title, str)

    def test_mission_minimal_fixture_passes_pydantic_validation(self) -> None:
        """mission_minimal.yaml must load without Pydantic validation error."""
        raw = (fixtures_dir() / "mission_minimal.yaml").read_text(encoding="utf-8")
        model = MissionModel.from_yaml(raw)
        assert model.version == 1
        assert model.status == "active"
        assert model.deadline_window_days == 42
        assert model.review_cadence == "weekly"

    def test_mission_valid_fixture_has_all_required_fields(self) -> None:
        """mission_valid.yaml fixture must include all fields defined in MissionModel."""
        raw = (fixtures_dir() / "mission_valid.yaml").read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
        model_fields = set(MissionModel.model_fields.keys())
        fixture_keys = set(data.keys())
        missing = model_fields - fixture_keys
        assert not missing, f"mission_valid.yaml missing fields: {missing}"

    def test_mission_valid_fixture_allowed_scope_is_list(self) -> None:
        raw = (fixtures_dir() / "mission_valid.yaml").read_text(encoding="utf-8")
        model = MissionModel.from_yaml(raw)
        assert isinstance(model.allowed_scope, list)

    def test_mission_valid_fixture_forbidden_expansions_is_list(self) -> None:
        raw = (fixtures_dir() / "mission_valid.yaml").read_text(encoding="utf-8")
        model = MissionModel.from_yaml(raw)
        assert isinstance(model.forbidden_expansions, list)
        assert len(model.forbidden_expansions) > 0, "test fixture should include forbidden expansions"

    def test_mission_valid_fixture_success_metric_has_type_and_value(self) -> None:
        raw = (fixtures_dir() / "mission_valid.yaml").read_text(encoding="utf-8")
        model = MissionModel.from_yaml(raw)
        assert hasattr(model.success_metric, "type")
        assert hasattr(model.success_metric, "value")
        assert model.success_metric.type in ("milestone", "metric", "user_signal")

    def test_mission_yaml_written_by_init_passes_pydantic(self, tmp_path: Path) -> None:
        """mission.yaml written by spine init must validate as MissionModel."""
        make_git_repo(tmp_path)
        spine_init(tmp_path)
        raw = (tmp_path / ".spine" / "mission.yaml").read_text(encoding="utf-8")
        model = MissionModel.from_yaml(raw)
        assert model.version == 1
        assert model.status == "active"


# ---------------------------------------------------------------------------
# 3. artifact_manifest.json structure contracts
# ---------------------------------------------------------------------------


class TestArtifactManifestFixtureContract:
    """Validate artifact_manifest.json fixture structure and live command output."""

    def test_manifest_full_fixture_has_contract_version(self) -> None:
        data = json.loads((fixtures_dir() / "artifact_manifest_full.json").read_text())
        assert data.get("contract_version") == "1", "contract_version must be '1'"

    def test_manifest_full_fixture_has_briefs_and_reviews(self) -> None:
        data = json.loads((fixtures_dir() / "artifact_manifest_full.json").read_text())
        assert "briefs" in data
        assert "reviews" in data

    def test_manifest_full_fixture_brief_entry_has_required_keys(self) -> None:
        data = json.loads((fixtures_dir() / "artifact_manifest_full.json").read_text())
        for target, entry in data["briefs"].items():
            assert "latest" in entry, f"briefs.{target} missing 'latest'"
            assert "last_generated_at" in entry, f"briefs.{target} missing 'last_generated_at'"

    def test_manifest_full_fixture_review_entry_has_required_keys(self) -> None:
        data = json.loads((fixtures_dir() / "artifact_manifest_full.json").read_text())
        for kind, entry in data["reviews"].items():
            assert "latest" in entry, f"reviews.{kind} missing 'latest'"
            assert "last_generated_at" in entry, f"reviews.{kind} missing 'last_generated_at'"

    def test_manifest_full_fixture_paths_are_relative(self) -> None:
        data = json.loads((fixtures_dir() / "artifact_manifest_full.json").read_text())
        for target, entry in data.get("briefs", {}).items():
            assert not entry["latest"].startswith("/"), (
                f"briefs.{target}.latest must be relative"
            )
        for kind, entry in data.get("reviews", {}).items():
            assert not entry["latest"].startswith("/"), (
                f"reviews.{kind}.latest must be relative"
            )

    def test_manifest_minimal_fixture_has_only_contract_version(self) -> None:
        data = json.loads((fixtures_dir() / "artifact_manifest_minimal.json").read_text())
        assert data.get("contract_version") == "1"
        # Minimal manifest has no briefs or reviews section yet
        assert "briefs" not in data
        assert "reviews" not in data

    def test_live_brief_manifest_matches_fixture_shape(self, tmp_path: Path) -> None:
        """Manifest produced by spine brief must match artifact_manifest_full.json shape."""
        make_git_repo(tmp_path)
        spine_init(tmp_path)
        runner.invoke(app, ["brief", "--target", "claude", "--cwd", str(tmp_path)])

        live_data = json.loads((tmp_path / ".spine" / "artifact_manifest.json").read_text())
        fixture_data = json.loads((fixtures_dir() / "artifact_manifest_full.json").read_text())

        # Live manifest must have same top-level structure as fixture
        assert "contract_version" in live_data
        assert live_data["contract_version"] == fixture_data["contract_version"]
        assert "briefs" in live_data
        assert "claude" in live_data["briefs"]
        assert "latest" in live_data["briefs"]["claude"]
        assert "last_generated_at" in live_data["briefs"]["claude"]

    def test_live_review_manifest_matches_fixture_shape(self, tmp_path: Path) -> None:
        """Manifest produced by spine review must match reviews section shape."""
        make_git_repo(tmp_path)
        spine_init(tmp_path)
        runner.invoke(app, ["review", "weekly", "--cwd", str(tmp_path)])

        live_data = json.loads((tmp_path / ".spine" / "artifact_manifest.json").read_text())
        assert "reviews" in live_data
        assert "weekly" in live_data["reviews"]
        assert "latest" in live_data["reviews"]["weekly"]
        assert "last_generated_at" in live_data["reviews"]["weekly"]


# ---------------------------------------------------------------------------
# 4. JSON output shape contracts (fixture-driven)
# ---------------------------------------------------------------------------


def _load_shape(shape_name: str) -> dict:
    path = fixtures_dir() / "json_shapes" / shape_name
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_shape(actual: dict, shape: dict, command_label: str) -> None:
    """Assert actual JSON output has all required keys with correct types."""
    type_map = {"bool": bool, "int": int, "str": str, "list": list, "dict": dict}
    for key in shape["required_keys"]:
        assert key in actual, f"{command_label}: output missing required key '{key}'"
    for key, type_name in shape["key_types"].items():
        if key in actual:
            expected_type = type_map[type_name]
            assert isinstance(actual[key], expected_type), (
                f"{command_label}: '{key}' must be {type_name}, got {type(actual[key]).__name__}"
            )


class TestJsonOutputShapeContracts:
    """Run commands with --json and validate output matches shape fixtures."""

    def test_doctor_json_output_matches_fixture_shape(self, tmp_path: Path) -> None:
        make_git_repo(tmp_path)
        spine_init(tmp_path)
        code, out = run_cmd(["doctor", "--cwd", str(tmp_path), "--json"])
        assert code in (0, 1), f"doctor exited {code}: {out}"
        data = json.loads(out)
        _validate_shape(data, _load_shape("doctor.json"), "spine doctor --json")

    def test_check_before_pr_json_output_matches_fixture_shape(self, tmp_path: Path) -> None:
        make_git_repo(tmp_path)
        spine_init(tmp_path)
        code, out = run_cmd(["check", "before-pr", "--cwd", str(tmp_path), "--json"])
        assert code in (0, 1), f"check before-pr exited {code}: {out}"
        data = json.loads(out)
        shape = _load_shape("check_before_pr.json")
        _validate_shape(data, shape, "spine check before-pr --json")
        assert data["result"] in shape["result_values"], (
            f"result must be one of {shape['result_values']}, got {data['result']!r}"
        )

    def test_check_before_pr_checks_items_have_required_keys(self, tmp_path: Path) -> None:
        make_git_repo(tmp_path)
        spine_init(tmp_path)
        code, out = run_cmd(["check", "before-pr", "--cwd", str(tmp_path), "--json"])
        assert code in (0, 1)
        data = json.loads(out)
        shape = _load_shape("check_before_pr.json")
        for item in data["checks"]:
            for key in shape["checks_item_keys"]:
                assert key in item, f"check item missing key '{key}': {item}"

    def test_mission_show_json_output_matches_fixture_shape(self, tmp_path: Path) -> None:
        make_git_repo(tmp_path)
        spine_init(tmp_path)
        code, out = run_cmd(["mission", "show", "--cwd", str(tmp_path), "--json"])
        assert code == 0, f"mission show exited {code}: {out}"
        data = json.loads(out)
        shape = _load_shape("mission_show.json")
        _validate_shape(data, shape, "spine mission show --json")
        assert data["status"] in shape["status_values"], (
            f"status must be one of {shape['status_values']}, got {data['status']!r}"
        )

    def test_review_handoff_json_output_matches_fixture_shape(self, tmp_path: Path) -> None:
        make_git_repo(tmp_path)
        spine_init(tmp_path)
        code, out = run_cmd(["review", "handoff", "--cwd", str(tmp_path), "--json"])
        assert code == 0, f"review handoff exited {code}: {out}"
        data = json.loads(out)
        shape = _load_shape("review_handoff.json")
        _validate_shape(data, shape, "spine review handoff --json")
        totals = data["totals"]
        for key in shape["totals_keys"]:
            assert key in totals, f"totals missing key '{key}'"

    def test_brief_json_output_matches_fixture_shape(self, tmp_path: Path) -> None:
        make_git_repo(tmp_path)
        spine_init(tmp_path)
        code, out = run_cmd(["brief", "--target", "claude", "--cwd", str(tmp_path), "--json"])
        assert code == 0, f"brief exited {code}: {out}"
        data = json.loads(out)
        shape = _load_shape("brief.json")
        _validate_shape(data, shape, "spine brief --json")
        assert data["latest_path"].endswith("latest.md"), (
            f"latest_path must end with latest.md: {data['latest_path']!r}"
        )

    def test_drift_scan_json_output_matches_fixture_shape(self, tmp_path: Path) -> None:
        make_git_repo(tmp_path)
        spine_init(tmp_path)
        code, out = run_cmd(["drift", "scan", "--cwd", str(tmp_path), "--json"])
        assert code == 0, f"drift scan exited {code}: {out}"
        data = json.loads(out)
        _validate_shape(data, _load_shape("drift_scan.json"), "spine drift scan --json")


# ---------------------------------------------------------------------------
# 5. Exit code contracts (fixture-documented scenarios)
# ---------------------------------------------------------------------------


class TestExitCodeContracts:
    """Validate exit code contracts documented in fixtures/exit_codes.json."""

    def test_init_new_repo_exits_0(self, tmp_path: Path) -> None:
        make_git_repo(tmp_path)
        code, out = run_cmd(["init", "--cwd", str(tmp_path)])
        assert code == 0, f"Expected 0 for new init, got {code}: {out}"

    def test_init_already_initialized_exits_3(self, tmp_path: Path) -> None:
        make_git_repo(tmp_path)
        spine_init(tmp_path)
        code, out = run_cmd(["init", "--cwd", str(tmp_path)])
        assert code == 3, f"Expected 3 (conflict) for re-init without --force, got {code}: {out}"

    def test_init_force_already_initialized_exits_0(self, tmp_path: Path) -> None:
        make_git_repo(tmp_path)
        spine_init(tmp_path)
        code, out = run_cmd(["init", "--force", "--cwd", str(tmp_path)])
        assert code == 0, f"Expected 0 for --force re-init, got {code}: {out}"

    def test_init_no_git_exits_2(self, tmp_path: Path) -> None:
        code, out = run_cmd(["init", "--cwd", str(tmp_path)])
        assert code == 2, f"Expected 2 (context failure) for no git repo, got {code}: {out}"

    def test_mission_show_valid_repo_exits_0(self, tmp_path: Path) -> None:
        make_git_repo(tmp_path)
        spine_init(tmp_path)
        code, out = run_cmd(["mission", "show", "--cwd", str(tmp_path)])
        assert code == 0, f"Expected 0 for valid repo, got {code}: {out}"

    def test_mission_show_missing_spine_exits_2(self, tmp_path: Path) -> None:
        make_git_repo(tmp_path)
        code, out = run_cmd(["mission", "show", "--cwd", str(tmp_path)])
        assert code == 2, f"Expected 2 (context failure) for missing .spine/, got {code}: {out}"

    def test_mission_set_invalid_status_exits_1(self, tmp_path: Path) -> None:
        make_git_repo(tmp_path)
        spine_init(tmp_path)
        code, out = run_cmd(
            ["mission", "set", "--cwd", str(tmp_path), "--status", "not_a_valid_status"]
        )
        assert code == 1, f"Expected 1 (validation failure) for invalid status, got {code}: {out}"

    def test_doctor_valid_repo_exits_0_or_1(self, tmp_path: Path) -> None:
        make_git_repo(tmp_path)
        spine_init(tmp_path)
        code, out = run_cmd(["doctor", "--cwd", str(tmp_path)])
        assert code in (0, 1), f"doctor must exit 0 or 1, got {code}: {out}"

    def test_doctor_git_no_spine_exits_1(self, tmp_path: Path) -> None:
        """doctor on a git repo without .spine/ runs checks and exits 1 (reports errors).

        Unlike mission show or brief, doctor does not exit 2 when .spine/ is absent —
        it runs and reports the missing .spine/ as an ERROR, then exits 1.
        """
        make_git_repo(tmp_path)
        code, out = run_cmd(["doctor", "--cwd", str(tmp_path)])
        assert code == 1, f"Expected 1 (validation — errors found) for no .spine/, got {code}: {out}"

    def test_check_before_pr_with_evidence_and_decisions_exits_0(self, tmp_path: Path) -> None:
        """check before-pr exits 0 (pass) when .spine/ is present with evidence and decisions."""
        make_git_repo(tmp_path)
        spine_init(tmp_path)
        # Populate evidence and decisions so all checks pass
        evidence_path = tmp_path / ".spine" / "evidence.jsonl"
        decisions_path = tmp_path / ".spine" / "decisions.jsonl"
        import json as _json
        evidence_path.write_text(
            _json.dumps({"kind": "test_pass", "description": "fixture contract tests pass",
                         "evidence_url": None, "created_at": "2026-04-08T00:00:00+00:00"}) + "\n"
        )
        decisions_path.write_text(
            _json.dumps({"title": "Fixture harness", "why": "deterministic contracts",
                         "decision": "add tests/fixtures/", "alternatives": [],
                         "created_at": "2026-04-08T00:00:00+00:00"}) + "\n"
        )
        code, out = run_cmd(["check", "before-pr", "--cwd", str(tmp_path)])
        assert code == 0, f"Expected 0 (pass) with evidence+decisions, got {code}: {out}"

    def test_check_before_pr_no_spine_exits_1(self, tmp_path: Path) -> None:
        """check before-pr exits 1 on a git repo without .spine/.

        It runs and reports spine_dir FAIL (review_recommended exit 1), not exit 2.
        Exit 2 is reserved for commands that cannot function without context at all.
        """
        make_git_repo(tmp_path)
        code, out = run_cmd(["check", "before-pr", "--cwd", str(tmp_path)])
        assert code == 1, f"Expected 1 (review_recommended) for no .spine/, got {code}: {out}"

    def test_brief_valid_target_exits_0(self, tmp_path: Path) -> None:
        make_git_repo(tmp_path)
        spine_init(tmp_path)
        code, out = run_cmd(["brief", "--target", "claude", "--cwd", str(tmp_path)])
        assert code == 0, f"Expected 0 for valid brief, got {code}: {out}"

    def test_brief_invalid_target_exits_1(self, tmp_path: Path) -> None:
        make_git_repo(tmp_path)
        spine_init(tmp_path)
        code, out = run_cmd(["brief", "--target", "not_a_valid_agent", "--cwd", str(tmp_path)])
        assert code == 1, f"Expected 1 (validation failure) for invalid target, got {code}: {out}"

    def test_brief_missing_spine_exits_2(self, tmp_path: Path) -> None:
        make_git_repo(tmp_path)
        code, out = run_cmd(["brief", "--target", "claude", "--cwd", str(tmp_path)])
        assert code == 2, f"Expected 2 (context failure) for missing .spine/, got {code}: {out}"

    def test_review_weekly_valid_repo_exits_0(self, tmp_path: Path) -> None:
        make_git_repo(tmp_path)
        spine_init(tmp_path)
        code, out = run_cmd(["review", "weekly", "--cwd", str(tmp_path)])
        assert code == 0, f"Expected 0 for valid review, got {code}: {out}"

    def test_review_weekly_no_git_exits_2(self, tmp_path: Path) -> None:
        """review weekly exits 2 on a non-git directory."""
        code, out = run_cmd(["review", "weekly", "--cwd", str(tmp_path)])
        assert code == 2, f"Expected 2 (context failure) for no git repo, got {code}: {out}"

    def test_drift_scan_valid_repo_exits_0(self, tmp_path: Path) -> None:
        make_git_repo(tmp_path)
        spine_init(tmp_path)
        code, out = run_cmd(["drift", "scan", "--cwd", str(tmp_path)])
        assert code == 0, f"Expected 0 for valid drift scan, got {code}: {out}"

    def test_drift_scan_no_git_exits_2(self, tmp_path: Path) -> None:
        """drift scan exits 2 on a non-git directory."""
        code, out = run_cmd(["drift", "scan", "--cwd", str(tmp_path)])
        assert code == 2, f"Expected 2 (context failure) for no git repo, got {code}: {out}"

    def test_evidence_add_valid_exits_0(self, tmp_path: Path) -> None:
        make_git_repo(tmp_path)
        spine_init(tmp_path)
        code, out = run_cmd([
            "evidence", "add",
            "--cwd", str(tmp_path),
            "--kind", "test_pass",
            "--description", "Fixture contract harness validated",
        ])
        assert code == 0, f"Expected 0 for valid evidence add, got {code}: {out}"

    def test_decision_add_valid_exits_0(self, tmp_path: Path) -> None:
        make_git_repo(tmp_path)
        spine_init(tmp_path)
        code, out = run_cmd([
            "decision", "add",
            "--cwd", str(tmp_path),
            "--title", "Use fixture-based contract validation",
            "--why", "Deterministic, readable, CI-compatible",
            "--decision", "Add tests/fixtures/ layer for Issue #38",
        ])
        assert code == 0, f"Expected 0 for valid decision add, got {code}: {out}"


# ---------------------------------------------------------------------------
# 6. --cwd external-repo targeting contracts
# ---------------------------------------------------------------------------


class TestCwdTargetingContracts:
    """Validate --cwd targeting behavior: explicit path overrides cwd fallback."""

    def test_cwd_points_to_valid_repo_succeeds(self, tmp_path: Path) -> None:
        """--cwd to a valid initialized repo succeeds even if cwd is elsewhere."""
        repo = tmp_path / "my_project"
        repo.mkdir()
        make_git_repo(repo)
        spine_init(repo)

        # Run from a different directory — --cwd must take precedence
        original = os.getcwd()
        try:
            os.chdir(tmp_path)
            code, out = run_cmd(["mission", "show", "--cwd", str(repo)])
        finally:
            os.chdir(original)

        assert code == 0, f"Expected 0 when --cwd points to valid repo, got {code}: {out}"

    def test_cwd_points_to_uninitialized_repo_exits_2(self, tmp_path: Path) -> None:
        """--cwd to a git repo without .spine/ must exit 2."""
        repo = tmp_path / "bare_git"
        repo.mkdir()
        make_git_repo(repo)
        # No spine init — .spine/ does not exist

        code, out = run_cmd(["mission", "show", "--cwd", str(repo)])
        assert code == 2, (
            f"Expected 2 (context failure) for no .spine/, got {code}: {out}"
        )

    def test_cwd_to_non_git_dir_exits_2(self, tmp_path: Path) -> None:
        """--cwd to a directory with no git repo must exit 2."""
        plain_dir = tmp_path / "plain"
        plain_dir.mkdir()

        code, out = run_cmd(["doctor", "--cwd", str(plain_dir)])
        assert code == 2, f"Expected 2 for non-git dir, got {code}: {out}"

    def test_cwd_isolates_repos(self, tmp_path: Path) -> None:
        """Two separate repos initialized with --cwd stay independent."""
        repo_a = tmp_path / "repo_a"
        repo_b = tmp_path / "repo_b"
        repo_a.mkdir()
        repo_b.mkdir()
        make_git_repo(repo_a)
        make_git_repo(repo_b)
        spine_init(repo_a)
        spine_init(repo_b)

        # Set different titles in each repo
        run_cmd(["mission", "set", "--cwd", str(repo_a), "--title", "Repo A mission"])
        run_cmd(["mission", "set", "--cwd", str(repo_b), "--title", "Repo B mission"])

        _, out_a = run_cmd(["mission", "show", "--cwd", str(repo_a), "--json"])
        _, out_b = run_cmd(["mission", "show", "--cwd", str(repo_b), "--json"])

        data_a = json.loads(out_a)
        data_b = json.loads(out_b)

        assert data_a["title"] == "Repo A mission", f"Repo A title wrong: {data_a['title']!r}"
        assert data_b["title"] == "Repo B mission", f"Repo B title wrong: {data_b['title']!r}"
        assert data_a["title"] != data_b["title"], "--cwd must isolate repos"

    def test_cwd_all_core_commands_accept_flag(self, tmp_path: Path) -> None:
        """All major commands accept --cwd and succeed on a valid repo with data."""
        make_git_repo(tmp_path)
        spine_init(tmp_path)
        # Populate evidence and decisions so check before-pr passes cleanly
        import json as _json
        (tmp_path / ".spine" / "evidence.jsonl").write_text(
            _json.dumps({"kind": "test_pass", "description": "cwd test evidence",
                         "evidence_url": None, "created_at": "2026-04-08T00:00:00+00:00"}) + "\n"
        )
        (tmp_path / ".spine" / "decisions.jsonl").write_text(
            _json.dumps({"title": "Use --cwd", "why": "external repo targeting",
                         "decision": "test --cwd contract", "alternatives": [],
                         "created_at": "2026-04-08T00:00:00+00:00"}) + "\n"
        )

        commands = [
            ["mission", "show", "--cwd", str(tmp_path)],
            ["doctor", "--cwd", str(tmp_path)],
            ["check", "before-pr", "--cwd", str(tmp_path)],
            ["brief", "--target", "claude", "--cwd", str(tmp_path)],
            ["review", "weekly", "--cwd", str(tmp_path)],
            ["review", "handoff", "--cwd", str(tmp_path)],
            ["drift", "scan", "--cwd", str(tmp_path)],
        ]
        for args in commands:
            code, out = run_cmd(args)
            assert code == 0, f"Command {args[0]} {args[1]} --cwd failed ({code}): {out}"
