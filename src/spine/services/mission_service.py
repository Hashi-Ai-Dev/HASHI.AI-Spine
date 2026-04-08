"""MissionService — read and update .spine/mission.yaml."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from spine import constants as C
from spine.models import MissionModel
from spine.utils.io import write_file_safe


class MissionValidationError(Exception):
    """Raised when mission input validation fails."""


class MissionNotFoundError(Exception):
    """Raised when mission.yaml does not exist."""


class MissionDraftNotFoundError(Exception):
    """Raised when a requested mission draft does not exist."""


@dataclass
class MissionShowResult:
    """Structured result for mission show."""
    mission: MissionModel
    file_path: Path


@dataclass
class MissionDraftResult:
    """Structured result for mission refine (draft creation)."""
    draft_id: str
    draft_path: Path
    mission: MissionModel


class MissionService:
    """Service for reading and updating mission state."""

    def __init__(self, repo_root: Path, *, spine_root: Path | None = None) -> None:
        self.repo_root = repo_root
        # spine_root overrides where .spine/ files live (for --cwd / SPINE_ROOT use cases)
        self._spine_root = spine_root or repo_root / C.SPINE_DIR
        self.mission_path = self._spine_root / C.MISSION_FILE
        self._mission_drafts_dir = self._spine_root / C.MISSION_DRAFTS_DIR

    def _mission_not_found_error(self) -> MissionNotFoundError:
        """Return an actionable error for a missing mission.yaml."""
        spine_dir = self.mission_path.parent
        if not spine_dir.exists():
            return MissionNotFoundError(
                ".spine/ not found — run 'uv run spine init' to bootstrap governance state"
            )
        try:
            rel = self.mission_path.relative_to(self.repo_root).as_posix()
        except ValueError:
            rel = str(self.mission_path)
        return MissionNotFoundError(
            f"{rel} not found — run 'uv run spine init' to create it, "
            "or restore it from version control"
        )

    def show(self) -> MissionShowResult:
        """Read and validate mission.yaml."""
        if not self.mission_path.exists():
            raise self._mission_not_found_error()
        raw = self.mission_path.read_text(encoding="utf-8")
        mission = MissionModel.from_yaml(raw)
        return MissionShowResult(mission=mission, file_path=self.mission_path)

    def set(
        self,
        title: str | None = None,
        status: str | None = None,
        target_user: str | None = None,
        user_problem: str | None = None,
        one_sentence_promise: str | None = None,
        success_metric_type: str | None = None,
        success_metric_value: str | None = None,
        allowed_scope: list[str] | None = None,
        forbidden_expansions: list[str] | None = None,
        proof_requirements: list[str] | None = None,
        kill_conditions: list[str] | None = None,
    ) -> MissionModel:
        """
        Update mission.yaml with validated fields.
        Refreshes updated_at timestamp.
        Raises MissionValidationError on invalid input.
        """
        if not self.mission_path.exists():
            raise self._mission_not_found_error()

        raw = self.mission_path.read_text(encoding="utf-8")
        mission = MissionModel.from_yaml(raw)

        mission = self._apply_fields(
            mission,
            title=title,
            status=status,
            target_user=target_user,
            user_problem=user_problem,
            one_sentence_promise=one_sentence_promise,
            success_metric_type=success_metric_type,
            success_metric_value=success_metric_value,
            allowed_scope=allowed_scope,
            forbidden_expansions=forbidden_expansions,
            proof_requirements=proof_requirements,
            kill_conditions=kill_conditions,
        )

        # Always refresh updated_at
        mission.updated_at = datetime.now(timezone.utc).isoformat()

        # Write back
        content = mission.to_yaml()
        write_file_safe(self.mission_path, content, force=True)

        return mission

    # ------------------------------------------------------------------
    # Mission draft — refine / confirm / list
    # ------------------------------------------------------------------

    def refine(
        self,
        title: str | None = None,
        status: str | None = None,
        target_user: str | None = None,
        user_problem: str | None = None,
        one_sentence_promise: str | None = None,
        success_metric_type: str | None = None,
        success_metric_value: str | None = None,
        allowed_scope: list[str] | None = None,
        forbidden_expansions: list[str] | None = None,
        proof_requirements: list[str] | None = None,
        kill_conditions: list[str] | None = None,
    ) -> MissionDraftResult:
        """
        Create a draft mission refinement under .spine/drafts/missions/.

        Reads the current canonical mission.yaml as the base, applies the
        provided field overrides, and writes the result to a timestamped
        draft file.  Does NOT mutate mission.yaml.

        The draft is clearly labeled non-canonical via YAML comments.
        Returns a MissionDraftResult with the draft_id and path.

        Raises MissionNotFoundError if canonical mission.yaml does not exist.
        Raises MissionValidationError on invalid field values.
        """
        if not self.mission_path.exists():
            raise self._mission_not_found_error()

        raw = self.mission_path.read_text(encoding="utf-8")
        mission = MissionModel.from_yaml(raw)

        mission = self._apply_fields(
            mission,
            title=title,
            status=status,
            target_user=target_user,
            user_problem=user_problem,
            one_sentence_promise=one_sentence_promise,
            success_metric_type=success_metric_type,
            success_metric_value=success_metric_value,
            allowed_scope=allowed_scope,
            forbidden_expansions=forbidden_expansions,
            proof_requirements=proof_requirements,
            kill_conditions=kill_conditions,
        )

        # Refresh updated_at for the draft
        mission.updated_at = datetime.now(timezone.utc).isoformat()

        draft_id = self._generate_draft_id()
        draft_path = self._mission_drafts_dir / f"{draft_id}.yaml"

        # Build draft content with non-canonical header comments
        yaml_body = mission.to_yaml()
        header = (
            f"# SPINE MISSION DRAFT — non-canonical\n"
            f"# Draft ID: {draft_id}\n"
            f"# Promote with: uv run spine mission confirm {draft_id}\n"
            f"# Source canonical: .spine/mission.yaml\n"
            f"#\n"
        )
        draft_content = header + yaml_body

        self._mission_drafts_dir.mkdir(parents=True, exist_ok=True)
        draft_path.write_text(draft_content, encoding="utf-8")

        return MissionDraftResult(
            draft_id=draft_id,
            draft_path=draft_path,
            mission=mission,
        )

    def confirm_draft(self, draft_id: str) -> MissionModel:
        """
        Promote a mission draft to canonical mission.yaml.

        Reads the draft from .spine/drafts/missions/<draft_id>.yaml,
        validates it as a MissionModel, writes it to canonical mission.yaml,
        then removes the draft file.

        This is an explicit operator-only action.  Promotion is never silent
        or automatic.

        Raises MissionDraftNotFoundError if draft_id does not exist.
        Raises MissionValidationError if the draft is malformed.
        """
        draft_path = self._mission_drafts_dir / f"{draft_id}.yaml"
        if not draft_path.exists():
            raise MissionDraftNotFoundError(
                f"Mission draft not found: {draft_id}\n"
                f"  Expected: {draft_path}\n"
                f"  Use 'spine mission drafts' to see available mission drafts."
            )

        raw = draft_path.read_text(encoding="utf-8")
        try:
            mission = MissionModel.from_yaml(raw)
        except Exception as exc:
            raise MissionValidationError(
                f"Draft '{draft_id}' is malformed and cannot be promoted: {exc}"
            ) from exc

        # Write to canonical mission.yaml
        content = mission.to_yaml()
        write_file_safe(self.mission_path, content, force=True)

        # Remove draft file
        draft_path.unlink()

        return mission

    def list_mission_drafts(self) -> list[dict]:
        """
        Return all pending mission drafts, sorted by filename (creation time).

        Each entry contains: draft_id, draft_path, title, status.
        Returns an empty list if no drafts exist.
        """
        if not self._mission_drafts_dir.exists():
            return []

        entries = []
        for path in sorted(self._mission_drafts_dir.glob("mission-*.yaml")):
            try:
                raw = path.read_text(encoding="utf-8")
                mission = MissionModel.from_yaml(raw)
                entries.append({
                    "draft_id": path.stem,
                    "draft_path": path,
                    "title": mission.title,
                    "status": mission.status,
                })
            except Exception:
                # Skip malformed draft files rather than crashing
                entries.append({
                    "draft_id": path.stem,
                    "draft_path": path,
                    "title": "(malformed draft)",
                    "status": "?",
                })
        return entries

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _generate_draft_id(self) -> str:
        """Generate a deterministic, filename-safe mission draft ID."""
        ts = datetime.now(timezone.utc)
        return f"mission-{ts.strftime('%Y%m%dT%H%M%S%f')}"

    def _apply_fields(
        self,
        mission: MissionModel,
        *,
        title: str | None,
        status: str | None,
        target_user: str | None,
        user_problem: str | None,
        one_sentence_promise: str | None,
        success_metric_type: str | None,
        success_metric_value: str | None,
        allowed_scope: list[str] | None,
        forbidden_expansions: list[str] | None,
        proof_requirements: list[str] | None,
        kill_conditions: list[str] | None,
    ) -> MissionModel:
        """Apply validated field overrides to a MissionModel in-place."""
        if status is not None:
            valid_statuses = {"active", "paused", "complete", "killed"}
            if status not in valid_statuses:
                raise MissionValidationError(
                    f"Invalid status '{status}'. Must be one of: {valid_statuses}"
                )
            # Validate transitions
            if mission.status == "complete" and status != "complete":
                if status == "killed":
                    pass  # allowed
                elif status == "active":
                    pass  # reactivation allowed
                else:
                    raise MissionValidationError(
                        f"Cannot transition from '{mission.status}' to '{status}'. "
                        "A 'complete' mission can only be reactivated or killed."
                    )
            if mission.status == "killed" and status != "killed":
                raise MissionValidationError(
                    f"Cannot transition from 'killed' to '{status}'. "
                    "A killed mission cannot be revived."
                )
            mission.status = status  # type: ignore[assignment]

        if title is not None:
            mission.title = title
        if target_user is not None:
            mission.target_user = target_user
        if user_problem is not None:
            mission.user_problem = user_problem
        if one_sentence_promise is not None:
            mission.one_sentence_promise = one_sentence_promise

        if success_metric_type is not None:
            valid_types = {"milestone", "metric", "user_signal"}
            if success_metric_type not in valid_types:
                raise MissionValidationError(
                    f"Invalid success_metric.type '{success_metric_type}'. "
                    f"Must be one of: {valid_types}"
                )
            mission.success_metric.type = success_metric_type  # type: ignore[assignment]
        if success_metric_value is not None:
            mission.success_metric.value = success_metric_value

        if allowed_scope is not None:
            mission.allowed_scope = allowed_scope
        if forbidden_expansions is not None:
            mission.forbidden_expansions = forbidden_expansions
        if proof_requirements is not None:
            mission.proof_requirements = proof_requirements
        if kill_conditions is not None:
            mission.kill_conditions = kill_conditions

        return mission
