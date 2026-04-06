"""Pydantic v2 model for drift records in .spine/drift.jsonl."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


DRIFT_SEVERITY = Literal["low", "medium", "high"]
DRIFT_CATEGORY = Literal[
    "forbidden_expansion",
    "scope_sprawl",
    "dependency_bloat",
    "service_creep",
    "test_gap",
]


class DriftEventModel(BaseModel):
    """A single drift event appended to drift.jsonl."""

    severity: DRIFT_SEVERITY
    category: DRIFT_CATEGORY
    description: str
    file_path: str = ""
    diff_hunk: str = ""
    created_at: str = Field(default_factory=_now_iso)

    model_config = {"extra": "forbid"}

    def to_json(self) -> dict:
        return self.model_dump(mode="json")
