"""Pydantic v2 model for opportunity records in .spine/opportunities.jsonl."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class OpportunityScoreModel(BaseModel):
    """Deterministic weighted score for an opportunity."""

    pain: int = Field(ge=1, le=5)
    founder_fit: int = Field(ge=1, le=5)
    time_to_proof: int = Field(ge=1, le=5, description="1=fastest, 5=slowest")
    monetization: int = Field(ge=1, le=5)
    sprawl_risk: int = Field(ge=1, le=5, description="1=risky/sprawl, 5=contained")
    maintenance_burden: int = Field(ge=1, le=5, description="1=heavy burden, 5=light")

    # Default weights: favor founder fit and time to proof
    weights: dict[str, float] = Field(
        default_factory=lambda: {
            "pain": 1.5,
            "founder_fit": 2.0,
            "time_to_proof": 2.0,
            "monetization": 1.0,
            "sprawl_risk": 1.0,
            "maintenance_burden": 1.0,
        }
    )

    model_config = {"extra": "forbid"}

    def weighted_score(self) -> float:
        total_weight = sum(self.weights.values())
        raw = (
            self.pain * self.weights["pain"]
            + self.founder_fit * self.weights["founder_fit"]
            + self.time_to_proof * self.weights["time_to_proof"]
            + self.monetization * self.weights["monetization"]
            + self.sprawl_risk * self.weights["sprawl_risk"]
            + self.maintenance_burden * self.weights["maintenance_burden"]
        )
        return round(raw / total_weight, 2)


class OpportunityModel(BaseModel):
    """A single opportunity record appended to opportunities.jsonl."""

    title: str = Field(min_length=1)
    description: str = ""
    scores: OpportunityScoreModel
    total_score: float = 0.0
    created_at: str = Field(default_factory=_now_iso)

    model_config = {"extra": "forbid"}

    def to_json(self) -> dict:
        data = self.model_dump(mode="json")
        # Compute total_score from scores
        scores = OpportunityScoreModel(**data["scores"])
        data["total_score"] = scores.weighted_score()
        return data
