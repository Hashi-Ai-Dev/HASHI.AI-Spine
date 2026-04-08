"""DecisionService — append validated decision records to decisions.jsonl."""

from __future__ import annotations

from pathlib import Path

from spine import constants as C
from spine.models import DecisionModel
from spine.utils.jsonl import append_jsonl


class DecisionValidationError(Exception):
    """Raised when decision input validation fails."""


class DecisionService:
    """Service for appending decision records."""

    def __init__(self, repo_root: Path, *, spine_root: Path | None = None) -> None:
        self.repo_root = repo_root
        self._spine_root = spine_root or repo_root / C.SPINE_DIR
        self.jsonl_path = self._spine_root / C.DECISIONS_FILE

    def add(
        self,
        title: str,
        why: str,
        decision: str,
        alternatives: list[str] | None = None,
    ) -> DecisionModel:
        """
        Append a validated decision record to decisions.jsonl.
        Requires title, why, and decision. Alternatives is optional.
        """
        if not title.strip():
            raise DecisionValidationError("title cannot be empty")
        if not why.strip():
            raise DecisionValidationError("why cannot be empty")
        if not decision.strip():
            raise DecisionValidationError("decision cannot be empty")

        decision_record = DecisionModel(
            title=title.strip(),
            why=why.strip(),
            decision=decision.strip(),
            alternatives=alternatives or [],
        )
        append_jsonl(self.jsonl_path, decision_record.to_json())
        return decision_record

    def add_draft(
        self,
        title: str,
        why: str,
        decision: str,
        alternatives: list[str] | None = None,
    ) -> tuple[DecisionModel, str]:
        """
        Save a draft decision record to .spine/drafts/.

        The record is NOT appended to decisions.jsonl.
        Use 'spine drafts confirm <draft_id>' to promote it later.

        Returns (DecisionModel, draft_id).
        """
        if not title.strip():
            raise DecisionValidationError("title cannot be empty")
        if not why.strip():
            raise DecisionValidationError("why cannot be empty")
        if not decision.strip():
            raise DecisionValidationError("decision cannot be empty")

        from spine.services.draft_service import DraftService

        decision_record = DecisionModel(
            title=title.strip(),
            why=why.strip(),
            decision=decision.strip(),
            alternatives=alternatives or [],
        )
        draft_svc = DraftService(self.repo_root, spine_root=self._spine_root)
        draft_id = draft_svc.save_decision_draft(decision_record)
        return decision_record, draft_id
