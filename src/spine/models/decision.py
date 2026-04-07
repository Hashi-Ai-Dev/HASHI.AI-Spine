"""Pydantic v2 model for decision records in .spine/decisions.jsonl."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class DecisionModel(BaseModel):
    """A single decision record appended to decisions.jsonl."""

    title: str = Field(min_length=1)
    why: str = Field(min_length=1, description="Why this decision was made")
    decision: str = Field(min_length=1, description="What was decided")
    alternatives: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=_now_iso)

    model_config = {"extra": "forbid"}

    def to_json(self) -> dict:
        return self.model_dump(mode="json")
