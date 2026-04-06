"""Pydantic v2 model for evidence records in .spine/evidence.jsonl."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


EVIDENCE_KINDS = Literal[
    "brief_generated",
    "commit",
    "pr",
    "test_pass",
    "review_done",
    "demo",
    "user_feedback",
    "payment",
    "kill",
    "narrow",
]


class EvidenceModel(BaseModel):
    """A single evidence record appended to evidence.jsonl."""

    kind: EVIDENCE_KINDS
    description: str = ""
    evidence_url: str = ""
    created_at: str = Field(default_factory=_now_iso)

    model_config = {"extra": "forbid"}

    def to_json(self) -> dict:
        return self.model_dump(mode="json")
