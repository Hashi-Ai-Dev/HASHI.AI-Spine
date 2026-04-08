"""DraftService — save and promote draft governance records.

Drafts are stored under .spine/drafts/ as individual JSON files.
They are excluded from all canonical governance surfaces until explicitly confirmed.

Storage:
  .spine/drafts/evidence-<timestamp>.json
  .spine/drafts/decision-<timestamp>.json

Each draft file includes a ``_record_type`` field ("evidence" or "decision")
so the confirm command knows which canonical JSONL to promote into.

Promotion is always explicit — no silent auto-confirm.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from spine import constants as C
from spine.models import EvidenceModel, DecisionModel
from spine.utils.jsonl import append_jsonl


class DraftNotFoundError(Exception):
    """Raised when a requested draft ID does not exist."""


class DraftError(Exception):
    """Raised for other draft operation errors."""


class DraftService:
    """Service for managing draft governance records."""

    def __init__(self, repo_root: Path, *, spine_root: Path | None = None) -> None:
        self.repo_root = repo_root
        self._spine_root = spine_root or repo_root / C.SPINE_DIR
        self.drafts_dir = self._spine_root / C.DRAFTS_DIR

    # ------------------------------------------------------------------
    # Draft creation
    # ------------------------------------------------------------------

    def save_evidence_draft(self, evidence: EvidenceModel) -> str:
        """
        Save an evidence record as a draft.
        Returns the draft_id (stem of the draft file).
        """
        draft_id = self._generate_id("evidence")
        draft_data = {"_record_type": "evidence", **evidence.to_json()}
        self._write_draft(draft_id, draft_data)
        return draft_id

    def save_decision_draft(self, decision: DecisionModel) -> str:
        """
        Save a decision record as a draft.
        Returns the draft_id (stem of the draft file).
        """
        draft_id = self._generate_id("decision")
        draft_data = {"_record_type": "decision", **decision.to_json()}
        self._write_draft(draft_id, draft_data)
        return draft_id

    # ------------------------------------------------------------------
    # Confirmation / promotion
    # ------------------------------------------------------------------

    def confirm(self, draft_id: str) -> dict:
        """
        Promote a draft into canonical storage.

        Reads the draft, appends the record to the appropriate canonical
        JSONL file, then deletes the draft file.

        Raises DraftNotFoundError if the draft_id does not exist.
        Raises DraftError if the draft has an unrecognized record type.

        Returns the promoted record dict (without _record_type).
        """
        draft_path = self.drafts_dir / f"{draft_id}.json"
        if not draft_path.exists():
            raise DraftNotFoundError(
                f"Draft not found: {draft_id}\n"
                f"  Expected: {draft_path}\n"
                f"  Use 'spine drafts list' to see available drafts."
            )

        raw = draft_path.read_text(encoding="utf-8")
        draft_data = json.loads(raw)

        record_type = draft_data.pop("_record_type", None)
        if record_type == "evidence":
            target = self._spine_root / C.EVIDENCE_FILE
        elif record_type == "decision":
            target = self._spine_root / C.DECISIONS_FILE
        else:
            raise DraftError(
                f"Unknown or missing _record_type in draft '{draft_id}': {record_type!r}"
            )

        append_jsonl(target, draft_data)
        draft_path.unlink()
        return draft_data

    # ------------------------------------------------------------------
    # Listing
    # ------------------------------------------------------------------

    def list_drafts(self) -> list[dict]:
        """
        Return a list of all pending drafts, sorted by filename (creation time).

        Each entry includes the draft_id and the full record data.
        Returns an empty list if no drafts exist.
        """
        if not self.drafts_dir.exists():
            return []
        entries = []
        for path in sorted(self.drafts_dir.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                entries.append({"draft_id": path.stem, **data})
            except Exception:
                # Skip malformed draft files rather than crashing
                continue
        return entries

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _generate_id(self, record_type: str) -> str:
        """Generate a deterministic, filename-safe draft ID."""
        ts = datetime.now(timezone.utc)
        return f"{record_type}-{ts.strftime('%Y%m%dT%H%M%S%f')}"

    def _write_draft(self, draft_id: str, data: dict) -> None:
        """Write draft data to .spine/drafts/<draft_id>.json."""
        self.drafts_dir.mkdir(parents=True, exist_ok=True)
        path = self.drafts_dir / f"{draft_id}.json"
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=True),
            encoding="utf-8",
        )
