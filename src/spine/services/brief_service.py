"""BriefService — generate mission briefs for Claude and Codex."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from spine import constants as C
from spine.models import MissionModel
from spine.utils.io import write_file_safe


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class BriefService:
    """Service for generating mission briefs."""

    def __init__(self, repo_root: Path, *, spine_root: Path | None = None) -> None:
        self.repo_root = repo_root
        self._spine_root = spine_root or repo_root / C.SPINE_DIR
        self.briefs_dir = self._spine_root / C.BRIEFS_DIR

    def generate_claude(self, mission: MissionModel) -> tuple[Path, Path]:
        """
        Generate markdown brief for Claude context.

        Returns (canonical_path, latest_path).
        canonical_path is a timestamped file (history preserved).
        latest_path is .../claude/latest.md (always updated).
        """
        target_dir = self.briefs_dir / "claude"
        target_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md"
        path = target_dir / filename

        content = self._build_claude_brief(mission)
        write_file_safe(path, content, force=False)

        # Always update latest.md alias
        latest = target_dir / "latest.md"
        write_file_safe(latest, content, force=True)

        return path, latest

    def generate_codex(self, mission: MissionModel) -> tuple[Path, Path]:
        """
        Generate markdown brief for Codex context.

        Returns (canonical_path, latest_path).
        canonical_path is a timestamped file (history preserved).
        latest_path is .../codex/latest.md (always updated).
        """
        target_dir = self.briefs_dir / "codex"
        target_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md"
        path = target_dir / filename

        content = self._build_codex_brief(mission)
        write_file_safe(path, content, force=False)

        # Always update latest.md alias
        latest = target_dir / "latest.md"
        write_file_safe(latest, content, force=True)

        return path, latest

    def _build_claude_brief(self, mission: MissionModel) -> str:
        """Build the Claude-specific brief markdown."""
        lines = [
            f"# Mission Brief — {mission.title}",
            "",
            f"**Status:** {mission.status}",
            f"**Generated:** {_now_iso()}",
            "",
            "## Mission Summary",
            "",
            f"- **Title:** {mission.title}",
            f"- **Target User:** {mission.target_user}",
            f"- **User Problem:** {mission.user_problem}",
            f"- **One-Sentence Promise:** {mission.one_sentence_promise}",
            "",
            "## Success Metric",
            "",
            f"- **Type:** {mission.success_metric.type}",
            f"- **Value:** {mission.success_metric.value}",
            "",
            "## Allowed Scope",
            "",
        ]
        for item in mission.allowed_scope:
            lines.append(f"- {item}")
        if not mission.allowed_scope:
            lines.append("_No allowed scope defined yet._")

        lines.extend([
            "",
            "## Forbidden Expansions",
            "",
        ])
        for item in mission.forbidden_expansions:
            lines.append(f"- {item}")
        if not mission.forbidden_expansions:
            lines.append("_No explicit forbidden expansions._")

        lines.extend([
            "",
            "## Proof Requirements",
            "",
        ])
        for item in mission.proof_requirements:
            lines.append(f"- {item}")
        if not mission.proof_requirements:
            lines.append("_No proof requirements defined yet._")

        lines.extend([
            "",
            "## Acceptance Criteria",
            "",
            "Before marking any work as complete, verify:",
            "",
            "1. All evidence has been added to `.spine/evidence.jsonl`",
            "2. All significant decisions have been recorded in `.spine/decisions.jsonl`",
            "3. No scope has silently expanded beyond `allowed_scope`",
            "4. Tests pass: `uv run pytest`",
            "",
            "## Testing Expectations",
            "",
            "- Run `uv run pytest` after every change session",
            "- All tests must pass before finishing a session",
            "- New features require new tests",
            "",
            "## Evidence Requirements",
            "",
            "After completing any non-trivial change, run:",
            "",
            "```bash",
            "spine evidence add --kind commit --description '<what changed>'",
            "```",
            "",
            "## Planning Note",
            "",
            "**Plan first for non-trivial work.** Before writing code, write a brief plan",
            "as a comment or in `.spine/decisions.jsonl`. Non-trivial means:",
            "",
            "- Adds new files outside existing modules",
            "- Changes existing behavior",
            "- Introduces new dependencies",
            "- Affects mission scope boundaries",
            "",
            "---",
            f"_Generated by SPINE v{C.SPINE_VERSION}_",
        ])
        return "\n".join(lines)

    def _build_codex_brief(self, mission: MissionModel) -> str:
        """Build the Codex-specific brief markdown."""
        lines = [
            f"# Mission Brief — {mission.title}",
            "",
            f"**Status:** {mission.status}",
            f"**Generated:** {_now_iso()}",
            "",
            "## Mission Summary",
            "",
            f"- **Title:** {mission.title}",
            f"- **Target User:** {mission.target_user}",
            f"- **User Problem:** {mission.user_problem}",
            f"- **One-Sentence Promise:** {mission.one_sentence_promise}",
            "",
            "## Success Metric",
            "",
            f"- **Type:** {mission.success_metric.type}",
            f"- **Value:** {mission.success_metric.value}",
            "",
            "## Allowed Scope",
            "",
        ]
        for item in mission.allowed_scope:
            lines.append(f"- {item}")
        if not mission.allowed_scope:
            lines.append("_No allowed scope defined yet._")

        lines.extend([
            "",
            "## Forbidden Expansions",
            "",
        ])
        for item in mission.forbidden_expansions:
            lines.append(f"- {item}")
        if not mission.forbidden_expansions:
            lines.append("_No explicit forbidden expansions._")

        lines.extend([
            "",
            "## Proof Requirements",
            "",
        ])
        for item in mission.proof_requirements:
            lines.append(f"- {item}")
        if not mission.proof_requirements:
            lines.append("_No proof requirements defined yet._")

        lines.extend([
            "",
            "## Worktree Recommendation",
            "",
            "For significant new features or refactors, create a worktree:",
            "",
            "```bash",
            "git worktree add ../spine-feature-<name> -b feature/<name>",
            "```",
            "",
            "This keeps the main branch clean and provides a bounded execution context.",
            "",
            "## Repo Discipline",
            "",
            "- Read `.spine/mission.yaml` before making changes",
            "- Never expand scope beyond `allowed_scope`",
            "- Record all decisions: `spine decision add`",
            "- Record evidence after significant changes: `spine evidence add`",
            "- Run tests before finishing: `uv run pytest`",
            "",
            "## Planning Note",
            "",
            "**Plan first for non-trivial work.** Use worktrees for features.",
            "Keep branches short and focused on the mission.",
            "",
            "---",
            f"_Generated by SPINE v{C.SPINE_VERSION}_",
        ])
        return "\n".join(lines)
