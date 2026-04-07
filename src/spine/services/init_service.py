"""
InitService: pure business logic for spine init.

No Rich output here. Returns a structured result that the CLI renders.
This makes the service independently testable without mocking terminal I/O.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from spine import constants as C
from spine.models import MissionModel, ConstraintsModel
from spine.utils.io import write_file_safe, ensure_dir, touch_file
from spine.utils.jsonl import ensure_jsonl
from spine.utils.paths import find_git_root, GitRepoNotFoundError


@dataclass
class InitResult:
    """Structured result returned by InitService.run()."""
    created: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    repo_root: Path | None = None


class ConflictError(Exception):
    """Raised when existing files block init and --force was not given."""
    def __init__(self, conflicts: list[str]) -> None:
        self.conflicts = conflicts
        super().__init__(f"Conflicting files: {conflicts}")


class InitService:
    def __init__(
        self,
        *,
        force: bool = False,
        allow_no_git: bool = False,
        cwd: Path | None = None,
        explicit_cwd: bool = False,
    ) -> None:
        self.force = force
        self.allow_no_git = allow_no_git
        self.cwd = cwd or Path.cwd()
        self._explicit_cwd = explicit_cwd

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self) -> InitResult:
        result = InitResult()

        # Step 1: Resolve repo root (for git-awareness and conflict detection)
        try:
            repo_root = find_git_root(self.cwd)
        except GitRepoNotFoundError:
            if self.allow_no_git:
                repo_root = self.cwd.resolve()
            else:
                raise  # CLI maps to exit code 2

        result.repo_root = repo_root

        # Step 2: Use cwd as the SPINE root when explicitly provided.
        # This lets `spine init --cwd <subdir>` initialize SPINE governance
        # inside a subdirectory of a git repo (treats subdir as its own project root).
        # When cwd is the same as Path.cwd() (no --cwd was passed), use repo_root.
        spine_root = self.cwd if self._explicit_cwd else repo_root
        spine = spine_root / C.SPINE_DIR

        # Step 2: Dry-run conflict detection (before touching anything).
        # Collect ALL conflicts first so the user sees the full list.
        conflicts = self._detect_conflicts(repo_root, spine)
        if conflicts and not self.force:
            result.conflicts = conflicts
            raise ConflictError(conflicts)

        # Step 3: Create .spine/ directory
        ensure_dir(spine)

        # Step 4: YAML files under .spine/
        self._create_or_skip(result, spine / C.MISSION_FILE, MissionModel().to_yaml(), base=spine_root)
        self._create_or_skip(result, spine / C.CONSTRAINTS_FILE, ConstraintsModel().to_yaml(), base=spine_root)

        # Step 5: JSONL append logs under .spine/
        for fname in [
            C.OPPORTUNITIES_FILE,
            C.NOT_NOW_FILE,
            C.EVIDENCE_FILE,
            C.DECISIONS_FILE,
            C.DRIFT_FILE,
            C.RUNS_FILE,
        ]:
            path = spine / fname
            created = ensure_jsonl(path, force=self.force)
            (result.created if created else result.skipped).append(
                path.relative_to(spine_root).as_posix()
            )

        # Step 6: state.db placeholder under .spine/ (empty file, never written as SQLite)
        db_path = spine / C.STATE_DB_FILE
        created = touch_file(db_path, force=self.force)
        (result.created if created else result.skipped).append(
            db_path.relative_to(spine_root).as_posix()
        )

        # Step 7: Subdirectories under .spine/
        for dname in [C.REVIEWS_DIR, C.BRIEFS_DIR, C.SKILLS_DIR, C.CHECKS_DIR]:
            d = spine / dname
            already_existed = d.exists()
            ensure_dir(d)
            rel = d.relative_to(spine_root).as_posix() + "/"
            (result.skipped if already_existed else result.created).append(rel)

        # Step 8: Repo-root governance and tool config files (always go to repo_root)
        self._create_or_skip(result, repo_root / C.AGENTS_MD, _AGENTS_MD_CONTENT, base=repo_root)
        self._create_or_skip(result, repo_root / C.CLAUDE_MD, _CLAUDE_MD_CONTENT, base=repo_root)
        self._create_or_skip(
            result, repo_root / C.CLAUDE_SETTINGS_PATH, _CLAUDE_SETTINGS_CONTENT, base=repo_root
        )
        self._create_or_skip(
            result, repo_root / C.CODEX_CONFIG_PATH, _CODEX_CONFIG_CONTENT, base=repo_root
        )

        return result

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _create_or_skip(
        self, result: InitResult, path: Path, content: str, *, base: Path | None = None
    ) -> None:
        """Write a file if it doesn't exist (or overwrite with --force)."""
        repo_root = base or result.repo_root
        assert repo_root is not None
        created = write_file_safe(path, content, force=self.force)
        rel = path.relative_to(repo_root).as_posix()
        (result.created if created else result.skipped).append(rel)

    def _detect_conflicts(self, repo_root: Path, spine: Path) -> list[str]:
        """
        Return list of relative paths that exist and would be overwritten.
        Only YAML/Markdown/config files are checked — JSONL logs and state.db
        are silently skipped because they are append-only and safe to re-init.
        """
        if self.force:
            return []
        candidates = [
            spine / C.MISSION_FILE,
            spine / C.CONSTRAINTS_FILE,
            repo_root / C.AGENTS_MD,
            repo_root / C.CLAUDE_MD,
            repo_root / C.CLAUDE_SETTINGS_PATH,
            repo_root / C.CODEX_CONFIG_PATH,
        ]
        return [
            p.relative_to(repo_root).as_posix()
            for p in candidates
            if p.exists()
        ]


# ============================================================
# Template file contents
# ============================================================

_AGENTS_MD_CONTENT = """\
# SPINE Agent Guidance

This repository uses `.spine/` as canonical governance state.

## Rules for all agents

- Read `.spine/mission.yaml` before making non-trivial changes.
- Read `.spine/constraints.yaml` to understand work schedule and budget limits.
- Never silently expand scope beyond `allowed_scope` in `mission.yaml`.
- Never add UI, auth, billing, cloud sync, or autonomous background loops unless
  they appear explicitly in `allowed_scope`.
- After any change session: run `uv run pytest` and fix all failures before finishing.

## Governance workflow (common commands)

```bash
uv run spine mission show          # view active mission
uv run spine doctor                # validate .spine/ state
uv run spine opportunity add ...   # log a candidate opportunity
uv run spine evidence add ...      # log evidence
uv run spine decision add ...      # record a decision
uv run spine drift scan            # detect scope drift
uv run spine review weekly ...     # generate weekly review
uv run spine brief generate ...    # generate agent brief
```

## Governance files

| File | Purpose |
|------|---------|
| `.spine/mission.yaml` | Active mission definition |
| `.spine/constraints.yaml` | Work schedule, budget, routing rules |
| `.spine/opportunities.jsonl` | Candidate opportunities log |
| `.spine/evidence.jsonl` | Evidence collected for review |
| `.spine/decisions.jsonl` | Decision record |
| `.spine/drift.jsonl` | Detected scope drift log |
| `.spine/runs.jsonl` | Agent run log |
| `.spine/reviews/` | Weekly review documents |
| `.spine/briefs/` | Agent brief documents |
"""

_CLAUDE_MD_CONTENT = """\
# CLAUDE.md — SPINE Governance

## Purpose

This repository uses SPINE for local-first, repo-native mission governance.
`.spine/` is the canonical source of truth for governance state.

## Rules

- Preserve `.spine/` as the canonical source of truth. Never rewrite its files
  silently.
- Read `.spine/mission.yaml` before making non-trivial changes.
- Do not silently expand scope beyond what is defined in `.spine/mission.yaml`.
- Do not add web UI, authentication, billing, or cloud sync unless explicitly
  in scope.
- Run `uv run spine doctor` to verify governance state is valid.
- Run `uv run pytest` before finishing any change session. Fix all failures.

## Quick reference

```bash
uv sync                            # install dependencies
uv run spine doctor                # validate .spine/ governance state
uv run spine mission show          # view active mission
uv run spine evidence add ...      # log evidence
uv run spine decision add ...      # record a decision
uv run spine review weekly ...     # generate weekly review
uv run pytest                      # run tests
```
"""

_CLAUDE_SETTINGS_CONTENT = """\
{
  "permissions": {
    "allow": [
      "Bash(uv:*)",
      "Bash(pytest:*)",
      "Bash(git:*)",
      "Read(*)",
      "Write(*)",
      "Edit(*)"
    ],
    "deny": []
  }
}
"""

_CODEX_CONFIG_CONTENT = """\
[sandbox]
type = "workspace-write"

[approvals]
mode = "on-request"

[worktrees]
enabled = true

[guidance]
file = "AGENTS.md"
"""
