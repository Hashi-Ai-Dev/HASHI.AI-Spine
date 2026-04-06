"""OpportunityService — deterministic weighted opportunity scoring."""

from __future__ import annotations

from pathlib import Path

from spine import constants as C
from spine.models import OpportunityModel, OpportunityScoreModel
from spine.utils.jsonl import append_jsonl


class OpportunityValidationError(Exception):
    """Raised when opportunity input validation fails."""


class OpportunityService:
    """Service for scoring and appending opportunities to opportunities.jsonl."""

    def __init__(self, repo_root: Path, *, spine_root: Path | None = None) -> None:
        self.repo_root = repo_root
        self._spine_root = spine_root or repo_root / C.SPINE_DIR
        self.jsonl_path = self._spine_root / C.OPPORTUNITIES_FILE

    def score(
        self,
        title: str,
        description: str = "",
        pain: int = 3,
        founder_fit: int = 3,
        time_to_proof: int = 3,
        monetization: int = 3,
        sprawl_risk: int = 3,
        maintenance_burden: int = 3,
    ) -> OpportunityModel:
        """
        Score an opportunity using deterministic weighted factors.
        Appends the record to opportunities.jsonl.
        """
        if not title.strip():
            raise OpportunityValidationError("title cannot be empty")

        # Validate scores are in 1-5 range
        for name, val in [
            ("pain", pain),
            ("founder_fit", founder_fit),
            ("time_to_proof", time_to_proof),
            ("monetization", monetization),
            ("sprawl_risk", sprawl_risk),
            ("maintenance_burden", maintenance_burden),
        ]:
            if not 1 <= val <= 5:
                raise OpportunityValidationError(
                    f"{name} must be between 1 and 5, got {val}"
                )

        score_model = OpportunityScoreModel(
            pain=pain,
            founder_fit=founder_fit,
            time_to_proof=time_to_proof,
            monetization=monetization,
            sprawl_risk=sprawl_risk,
            maintenance_burden=maintenance_burden,
        )
        total_score = score_model.weighted_score()

        opportunity = OpportunityModel(
            title=title.strip(),
            description=description.strip(),
            scores=score_model,
            total_score=total_score,
        )

        append_jsonl(self.jsonl_path, opportunity.to_json())
        return opportunity
