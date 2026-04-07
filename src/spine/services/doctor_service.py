"""DoctorService — validate .spine/ state and repo contract."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import yaml

from spine import constants as C
from spine.models import MissionModel, ConstraintsModel
from spine.utils.jsonl import parse_jsonl_lines


@dataclass
class DoctorIssue:
    """A single issue found during doctor validation."""
    severity: Literal["error", "warning"]
    file: str
    message: str


@dataclass
class DoctorResult:
    """Result of doctor validation."""
    passed: bool
    issues: list[DoctorIssue]


class DoctorService:
    """Service for validating .spine/ state and repo contract."""

    def __init__(self, repo_root: Path, *, spine_root: Path | None = None) -> None:
        self.repo_root = repo_root
        self._spine_root = spine_root or repo_root / C.SPINE_DIR
        self.spine_dir = self._spine_root

    def check(self) -> DoctorResult:
        """
        Run all doctor checks.
        Returns DoctorResult with passed=True if all checks pass.
        """
        issues: list[DoctorIssue] = []

        # Check repo contract files
        issues.extend(self._check_repo_contract())

        # Check .spine/ directory exists
        if not self.spine_dir.exists():
            issues.append(DoctorIssue(
                severity="error",
                file=".spine/",
                message=".spine/ not found — run 'uv run spine init' to bootstrap governance state",
            ))
            return DoctorResult(passed=False, issues=issues)

        # Check YAML files parse and conform
        issues.extend(self._check_mission_yaml())
        issues.extend(self._check_constraints_yaml())

        # Check JSONL files parse cleanly
        issues.extend(self._check_jsonl_files())

        # Check subdirectories exist
        issues.extend(self._check_subdirectories())

        return DoctorResult(
            passed=len([i for i in issues if i.severity == "error"]) == 0,
            issues=issues,
        )

    def _check_repo_contract(self) -> list[DoctorIssue]:
        """Check that required repo contract files exist."""
        issues = []
        for fname in [C.AGENTS_MD, C.CLAUDE_MD, C.CLAUDE_SETTINGS_PATH, C.CODEX_CONFIG_PATH]:
            path = self.repo_root / fname
            if not path.exists():
                issues.append(DoctorIssue(
                    severity="error",
                    file=fname,
                    message="Missing repo contract file — run 'spine init' to create it",
                ))
        return issues

    def _check_mission_yaml(self) -> list[DoctorIssue]:
        """Check mission.yaml parses and conforms."""
        issues = []
        path = self.spine_dir / C.MISSION_FILE
        if not path.exists():
            issues.append(DoctorIssue(
                severity="error",
                file=path.relative_to(self.repo_root).as_posix(),
                message="mission.yaml does not exist",
            ))
            return issues

        try:
            raw = path.read_text(encoding="utf-8")
            MissionModel.from_yaml(raw)
        except yaml.YAMLError as exc:
            issues.append(DoctorIssue(
                severity="error",
                file=path.relative_to(self.repo_root).as_posix(),
                message=f"YAML parse error: {exc}",
            ))
        except Exception as exc:
            issues.append(DoctorIssue(
                severity="error",
                file=path.relative_to(self.repo_root).as_posix(),
                message=f"Model validation error: {exc}",
            ))
        return issues

    def _check_constraints_yaml(self) -> list[DoctorIssue]:
        """Check constraints.yaml parses and conforms."""
        issues = []
        path = self.spine_dir / C.CONSTRAINTS_FILE
        if not path.exists():
            issues.append(DoctorIssue(
                severity="error",
                file=path.relative_to(self.repo_root).as_posix(),
                message="constraints.yaml does not exist",
            ))
            return issues

        try:
            raw = path.read_text(encoding="utf-8")
            ConstraintsModel.from_yaml(raw)
        except yaml.YAMLError as exc:
            issues.append(DoctorIssue(
                severity="error",
                file=path.relative_to(self.repo_root).as_posix(),
                message=f"YAML parse error: {exc}",
            ))
        except Exception as exc:
            issues.append(DoctorIssue(
                severity="error",
                file=path.relative_to(self.repo_root).as_posix(),
                message=f"Model validation error: {exc}",
            ))
        return issues

    def _check_jsonl_files(self) -> list[DoctorIssue]:
        """Check that all JSONL files have valid JSON on each line."""
        issues = []
        for fname in [
            C.OPPORTUNITIES_FILE,
            C.NOT_NOW_FILE,
            C.EVIDENCE_FILE,
            C.DECISIONS_FILE,
            C.DRIFT_FILE,
            C.RUNS_FILE,
        ]:
            path = self.spine_dir / fname
            if not path.exists():
                # JSONL files are created empty by init, so missing is an issue
                issues.append(DoctorIssue(
                    severity="warning",
                    file=path.relative_to(self.repo_root).as_posix(),
                    message="JSONL file does not exist (will be created on first append)",
                ))
                continue

            try:
                raw = path.read_text(encoding="utf-8")
                if raw.strip():  # Only validate if not empty
                    parse_jsonl_lines(raw)
            except Exception as exc:
                issues.append(DoctorIssue(
                    severity="error",
                    file=path.relative_to(self.repo_root).as_posix(),
                    message=f"JSONL parse error: {exc}",
                ))
        return issues

    def _check_subdirectories(self) -> list[DoctorIssue]:
        """Check that required subdirectories exist."""
        issues = []
        for dname in [C.REVIEWS_DIR, C.BRIEFS_DIR, C.SKILLS_DIR, C.CHECKS_DIR]:
            path = self.spine_dir / dname
            if not path.exists():
                issues.append(DoctorIssue(
                    severity="warning",
                    file=path.relative_to(self.repo_root).as_posix(),
                    message="Subdirectory does not exist (will be created as needed)",
                ))
        return issues
