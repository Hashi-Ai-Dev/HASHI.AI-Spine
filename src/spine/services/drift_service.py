"""DriftService — git-native deterministic drift scanning."""

from __future__ import annotations

import subprocess
import re
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path

from spine import constants as C
from spine.models import DriftEventModel, DRIFT_SEVERITY, DRIFT_CATEGORY
from spine.utils.jsonl import append_jsonl, read_jsonl


@dataclass
class DriftScanResult:
    """Result of a drift scan."""
    events: list[DriftEventModel]
    severity_summary: dict[DRIFT_SEVERITY, int]


class DriftService:
    """
    Git-native drift scanner.

    Uses only: git status, git diff --name-only, git diff.
    Does NOT do full recursive semantic repo scanning.
    """

    # Patterns that indicate forbidden expansions
    FORBIDDEN_PATTERNS: list[tuple[str, DRIFT_SEVERITY, re.Pattern]] = [
        # UI/dashboard additions when likely forbidden
        ("forbidden_expansion", "high", re.compile(r"(?i)^(?:ui|dashboard|frontend|web|www|static)/")),
        ("forbidden_expansion", "high", re.compile(r"(?i)^(?:pages/|components/|views?/)")),
        # Auth/billing additions
        # Anchored to path separators to avoid false positives on partial word matches
        ("forbidden_expansion", "high", re.compile(r"(?:^|/)(?:authentication|authorization|auth)(?:/|$)", re.IGNORECASE)),
        ("forbidden_expansion", "high", re.compile(r"(?:^|/)(?:billing|subscription|payment)(?:/|$)", re.IGNORECASE)),
        # Service creep
        ("service_creep", "medium", re.compile(r"(?i)server\.py$|api\.py$|endpoint")),
        # Test gaps: service files without tests
        ("test_gap", "low", re.compile(r"(?i)^(?:services?|api|server)/")),
    ]

    def __init__(self, repo_root: Path, *, spine_root: Path | None = None) -> None:
        self.repo_root = repo_root
        self._spine_root = spine_root or repo_root / C.SPINE_DIR

    def scan(
        self,
        against_branch: str | None = None,
    ) -> DriftScanResult:
        """
        Run git-native drift scan.

        Detection modes:
        - Mode A (working tree): git diff --name-only HEAD — uncommitted/staged changes
        - Mode B (branch drift): git diff --name-only <default_branch>...HEAD — committed
          changes on current branch not yet in the default branch

        If against_branch is provided explicitly, uses it for Mode B comparison.
        Otherwise, auto-detects default branch and runs both Mode A and Mode B.
        """
        events: list[DriftEventModel] = []

        # Collect changed files from all applicable modes
        changed_files: set[str] = set()

        if against_branch:
            # Explicit branch comparison — use three-dot diff
            files = self._get_changed_files(against_branch)
            diff_content = self._get_diff(against_branch)
            changed_files.update(files)
        else:
            # Auto-detect default branch and run both detection modes
            default_branch = self._get_default_branch()

            # Mode A: working tree / uncommitted changes
            wt_files = self._get_working_tree_files()
            wt_diff = self._get_working_tree_diff()
            changed_files.update(wt_files)

            # Mode B: committed branch drift vs default branch
            if default_branch:
                branch_files = self._get_branch_files(default_branch)
                branch_diff = self._get_branch_diff(default_branch)
                changed_files.update(branch_files)
                # Merge branch diff content for pattern checks
                diff_content = wt_diff + "\n" + branch_diff
            else:
                # No default branch detected — working tree only
                diff_content = wt_diff

        # Check each changed file path against patterns
        for file_path in changed_files:
            file_events = self._check_file_path(file_path)
            events.extend(file_events)

        # Check diff content for forbidden patterns
        diff_events = self._check_diff_content(diff_content, list(changed_files))
        events.extend(diff_events)

        # Deduplicate by description
        seen: set[str] = set()
        unique_events: list[DriftEventModel] = []
        for event in events:
            key = f"{event.severity}:{event.category}:{event.description}"
            if key not in seen:
                seen.add(key)
                unique_events.append(event)

        # Append events to drift.jsonl
        if unique_events:
            drift_path = self._spine_root / C.DRIFT_FILE
            for event in unique_events:
                append_jsonl(drift_path, event.to_json())

        # Build severity summary
        summary: dict[DRIFT_SEVERITY, int] = {"low": 0, "medium": 0, "high": 0}
        for event in unique_events:
            summary[event.severity] += 1

        return DriftScanResult(events=unique_events, severity_summary=summary)

    def _get_default_branch(self) -> str | None:
        """
        Detect the repository's default branch name.

        Tries in order:
        1. git symbolic-ref refs/remotes/origin/HEAD (remote origin default)
        2. git rev-parse --verify main (if main branch exists locally)
        3. git rev-parse --verify master (if master branch exists locally)

        Returns None if no default branch can be determined safely.
        """
        # First try remote origin HEAD (only works if origin exists)
        try:
            result = subprocess.run(
                ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
                capture_output=True,
                text=True,
                cwd=str(self.repo_root),
                timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                branch = result.stdout.strip()
                if branch.startswith("refs/remotes/origin/"):
                    branch = branch[len("refs/remotes/origin/"):]
                return branch
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Fallback to common local branch names — verify they actually exist
        for name in ["main", "master"]:
            try:
                result = subprocess.run(
                    ["git", "rev-parse", "--verify", name],
                    capture_output=True,
                    text=True,
                    cwd=str(self.repo_root),
                    timeout=10,
                )
                if result.returncode == 0:
                    return name
            except (FileNotFoundError, subprocess.TimeoutExpired):
                break

        return None

    def _get_branch_files(self, default_branch: str) -> list[str]:
        """
        Get all files changed on the current branch relative to default_branch.
        Uses three-dot diff: default_branch...HEAD
        This captures all commits on HEAD not in the merge base with default_branch.
        """
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", f"{default_branch}...HEAD"],
                capture_output=True,
                text=True,
                cwd=str(self.repo_root),
                timeout=30,
            )
            if result.returncode != 0:
                return []
            return [line.strip() for line in result.stdout.splitlines() if line.strip()]
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return []

    def _get_branch_diff(self, default_branch: str) -> str:
        """Get full diff content for branch drift vs default branch."""
        try:
            result = subprocess.run(
                ["git", "diff", f"{default_branch}...HEAD"],
                capture_output=True,
                text=True,
                cwd=str(self.repo_root),
                timeout=30,
            )
            if result.returncode != 0:
                return ""
            return result.stdout
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return ""

    def _get_working_tree_files(self) -> list[str]:
        """Get changed files in working tree (uncommitted/staged) vs HEAD."""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                capture_output=True,
                text=True,
                cwd=str(self.repo_root),
                timeout=30,
            )
            if result.returncode != 0:
                return []
            return [line.strip() for line in result.stdout.splitlines() if line.strip()]
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return []

    def _get_working_tree_diff(self) -> str:
        """Get diff content for working tree changes vs HEAD."""
        try:
            result = subprocess.run(
                ["git", "diff", "HEAD"],
                capture_output=True,
                text=True,
                cwd=str(self.repo_root),
                timeout=30,
            )
            if result.returncode != 0:
                return ""
            return result.stdout
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return ""

    def _get_changed_files(self, against_branch: str | None) -> list[str]:
        """Get list of changed file paths from git."""
        try:
            if against_branch:
                result = subprocess.run(
                    ["git", "diff", "--name-only", f"{against_branch}...HEAD"],
                    capture_output=True,
                    text=True,
                    cwd=str(self.repo_root),
                    timeout=30,
                )
            else:
                result = subprocess.run(
                    ["git", "diff", "--name-only", "HEAD"],
                    capture_output=True,
                    text=True,
                    cwd=str(self.repo_root),
                    timeout=30,
                )
            if result.returncode != 0:
                return []
            return [line.strip() for line in result.stdout.splitlines() if line.strip()]
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return []

    def _get_diff(self, against_branch: str | None) -> str:
        """Get diff content from git."""
        try:
            if against_branch:
                result = subprocess.run(
                    ["git", "diff", f"{against_branch}...HEAD"],
                    capture_output=True,
                    text=True,
                    cwd=str(self.repo_root),
                    timeout=30,
                )
            else:
                result = subprocess.run(
                    ["git", "diff", "HEAD"],
                    capture_output=True,
                    text=True,
                    cwd=str(self.repo_root),
                    timeout=30,
                )
            if result.returncode != 0:
                return ""
            return result.stdout
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return ""

    def _check_file_path(self, file_path: str) -> list[DriftEventModel]:
        """Check a single file path for drift patterns."""
        events = []
        for category, severity, pattern in self.FORBIDDEN_PATTERNS:
            if pattern.search(file_path):
                events.append(DriftEventModel(
                    severity=severity,
                    category=category,  # type: ignore[arg-type]
                    description=f"File path matches drift pattern: {file_path}",
                    file_path=file_path,
                ))
        return events

    def _check_diff_content(self, diff_content: str, changed_files: list[str]) -> list[DriftEventModel]:
        """Check diff content for forbidden patterns."""
        events = []

        # Check for dependency bloat in pyproject.toml, package.json, requirements.txt
        dep_files = [f for f in changed_files if any(
            f.endswith(ext) for ext in ["pyproject.toml", "package.json", "requirements.txt", "Pipfile", "poetry.lock"]
        )]
        for dep_file in dep_files:
            # If a dep file changed, flag it
            events.append(DriftEventModel(
                severity="low",
                category="dependency_bloat",  # type: ignore[arg-type]
                description=f"Dependency file changed: {dep_file}",
                file_path=dep_file,
            ))

        # Check for test gaps: new service files without corresponding test files
        service_pattern = re.compile(r"(?i)^(?:services?|api|server)/(.+?)\.(py|js|ts)$")
        for file_path in changed_files:
            m = service_pattern.match(file_path)
            if m:
                base = m.group(1)
                ext = m.group(2)
                test_paths = [
                    f"tests/{base}_test.{ext}",
                    f"tests/{base}.test.{ext}",
                    f"tests/test_{base}.{ext}",
                    f"spec/{base}.spec.{ext}",
                ]
                has_test = any(tp in changed_files for tp in test_paths)
                if not has_test:
                    events.append(DriftEventModel(
                        severity="low",
                        category="test_gap",  # type: ignore[arg-type]
                        description=f"Service file added without corresponding test: {file_path}",
                        file_path=file_path,
                    ))

        return events

    def get_open_drift(self) -> list[DriftEventModel]:
        """Read all drift events from drift.jsonl."""
        drift_path = self.repo_root / C.SPINE_DIR / C.DRIFT_FILE
        records = read_jsonl(drift_path)
        return [DriftEventModel(**r) for r in records]
