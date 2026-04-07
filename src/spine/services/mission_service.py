"""MissionService — read and update .spine/mission.yaml."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from spine import constants as C
from spine.models import MissionModel
from spine.utils.io import write_file_safe


class MissionValidationError(Exception):
    """Raised when mission input validation fails."""


class MissionNotFoundError(Exception):
    """Raised when mission.yaml does not exist."""


@dataclass
class MissionShowResult:
    """Structured result for mission show."""
    mission: MissionModel
    file_path: Path


class MissionService:
    """Service for reading and updating mission state."""

    def __init__(self, repo_root: Path, *, spine_root: Path | None = None) -> None:
        self.repo_root = repo_root
        # spine_root overrides where .spine/ files live (for --cwd / SPINE_ROOT use cases)
        self._spine_root = spine_root or repo_root / C.SPINE_DIR
        self.mission_path = self._spine_root / C.MISSION_FILE

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

        # Apply valid status transitions
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

        # Always refresh updated_at
        from datetime import datetime, timezone
        mission.updated_at = datetime.now(timezone.utc).isoformat()

        # Write back
        content = mission.to_yaml()
        write_file_safe(self.mission_path, content, force=True)

        return mission
