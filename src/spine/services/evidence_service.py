"""EvidenceService — append validated evidence records to evidence.jsonl."""

from __future__ import annotations

from pathlib import Path

from spine import constants as C
from spine.models import EvidenceModel, EVIDENCE_KINDS
from spine.utils.jsonl import append_jsonl


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
