"""EvidenceService — append validated evidence records to evidence.jsonl."""

from __future__ import annotations

from pathlib import Path

from spine import constants as C
from spine.models import EvidenceModel, EVIDENCE_KINDS
from spine.utils.jsonl import append_jsonl, read_jsonl


class EvidenceValidationError(Exception):
    """Raised when evidence input validation fails."""


class EvidenceService:
    """Service for appending evidence records."""

    def __init__(self, repo_root: Path, *, spine_root: Path | None = None) -> None:
        self.repo_root = repo_root
        self._spine_root = spine_root or repo_root / C.SPINE_DIR
        self.jsonl_path = self._spine_root / C.EVIDENCE_FILE

    def add(
        self,
        kind: EVIDENCE_KINDS,
        description: str = "",
        evidence_url: str = "",
    ) -> EvidenceModel:
        """
        Append a validated evidence record to evidence.jsonl.
        """
        evidence = EvidenceModel(
            kind=kind,
            description=description.strip(),
            evidence_url=evidence_url.strip(),
        )
        append_jsonl(self.jsonl_path, evidence.to_json())
        return evidence

    def list(self) -> list[dict]:
        """
        Return all evidence records sorted by created_at (ascending).
        """
        records = read_jsonl(self.jsonl_path)
        return sorted(records, key=lambda r: r.get("created_at", ""))

    def add_draft(
        self,
        kind: EVIDENCE_KINDS,
        description: str = "",
        evidence_url: str = "",
    ) -> tuple[EvidenceModel, str]:
        """
        Save a draft evidence record to .spine/drafts/.

        The record is NOT appended to evidence.jsonl.
        Use 'spine drafts confirm <draft_id>' to promote it later.

        Returns (EvidenceModel, draft_id).
        """
        from spine.services.draft_service import DraftService

        evidence = EvidenceModel(
            kind=kind,
            description=description.strip(),
            evidence_url=evidence_url.strip(),
        )
        draft_svc = DraftService(self.repo_root, spine_root=self._spine_root)
        draft_id = draft_svc.save_evidence_draft(evidence)
        return evidence, draft_id
