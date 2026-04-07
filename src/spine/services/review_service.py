"""ReviewService — generate weekly review documents."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Literal

from spine import constants as C
from spine.models import MissionModel
from spine.utils.io import write_file_safe
from spine.utils.jsonl import read_jsonl


RECOMMENDATION = Literal["continue", "narrow", "pivot", "kill", "ship_as_is"]


@dataclass
class ReviewResult:
    """Structured result for review generation — carries paths and period stats."""
    canonical: Path
    latest: Path
    recommendation: str
    period_days: int
    mission_title: str
    mission_status: str
    evidence_count: int
    decisions_count: int
    drift_count: int
    generated_at: str


class ReviewService:
    """Service for generating weekly review documents."""

    def __init__(self, repo_root: Path, *, spine_root: Path | None = None) -> None:
        self.repo_root = repo_root
        self._spine_root = spine_root or repo_root / C.SPINE_DIR
        self.reviews_dir = self._spine_root / C.REVIEWS_DIR
        self.mission_path = self._spine_root / C.MISSION_FILE
        self.evidence_path = self._spine_root / C.EVIDENCE_FILE
        self.decisions_path = self._spine_root / C.DECISIONS_FILE
        self.drift_path = self._spine_root / C.DRIFT_FILE

    def generate_weekly(
        self,
        days: int = 7,
        recommendation: RECOMMENDATION = "continue",
        notes: str = "",
    ) -> ReviewResult:
        """
        Aggregate last `days` of evidence, decisions, drift, and mission state.
        Write markdown review to .spine/reviews/YYYY-MM-DD.md and update latest.md.

        Returns a ReviewResult with paths and period stats.
        Same-day regeneration always overwrites the dated file so it stays fresh.
        """
        self.reviews_dir.mkdir(parents=True, exist_ok=True)
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        generated_at = datetime.now(timezone.utc).isoformat()
        filename = f"{today}.md"
        path = self.reviews_dir / filename

        # Read mission
        mission = None
        mission_title = "(no mission)"
        mission_status = "(none)"
        if self.mission_path.exists():
            raw = self.mission_path.read_text(encoding="utf-8")
            import yaml
            mission = MissionModel.from_yaml(raw)
            mission_title = mission.title
            mission_status = mission.status

        # Read and filter evidence (last `days` days)
        evidence = self._filter_recent(read_jsonl(self.evidence_path), days)
        # Read and filter decisions
        decisions = self._filter_recent(read_jsonl(self.decisions_path), days)
        # Read and filter drift
        drift = self._filter_recent(read_jsonl(self.drift_path), days)

        content = self._build_review(mission, evidence, decisions, drift, recommendation, notes, today, days)
        # force=True: same-day re-runs always refresh the dated file to match latest.md
        write_file_safe(path, content, force=True)

        # Always update latest.md alias
        latest = self.reviews_dir / "latest.md"
        write_file_safe(latest, content, force=True)

        return ReviewResult(
            canonical=path,
            latest=latest,
            recommendation=recommendation,
            period_days=days,
            mission_title=mission_title,
            mission_status=mission_status,
            evidence_count=len(evidence),
            decisions_count=len(decisions),
            drift_count=len(drift),
            generated_at=generated_at,
        )

    def _filter_recent(self, records: list[dict], days: int) -> list[dict]:
        """Filter records to those created within the last `days` days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        cutoff_iso = cutoff.isoformat()
        return [r for r in records if r.get("created_at", "") >= cutoff_iso]

    def _build_review(
        self,
        mission: MissionModel | None,
        evidence: list[dict],
        decisions: list[dict],
        drift: list[dict],
        recommendation: RECOMMENDATION,
        notes: str,
        date: str,
        days: int,
    ) -> str:
        """Build the weekly review markdown."""
        lines = [
            f"# Weekly Review — {date}",
            "",
            f"**Period:** Last {days} days",
            "",
        ]

        # Mission state
        lines.extend([
            "## Mission State",
            "",
        ])
        if mission:
            lines.extend([
                f"- **Title:** {mission.title}",
                f"- **Status:** {mission.status}",
                f"- **Success Metric:** {mission.success_metric.type} / {mission.success_metric.value}",
            ])
        else:
            lines.append("_No mission defined._")

        # Evidence
        lines.extend([
            "",
            f"## Evidence ({len(evidence)} events)",
            "",
        ])
        if evidence:
            for e in evidence:
                kind = e.get("kind", "?")
                desc = e.get("description", "")
                ts = e.get("created_at", "")
                lines.append(f"- [{kind}] {desc} _{ts}_")
        else:
            lines.append("_No evidence recorded in this period._")

        # Decisions
        lines.extend([
            "",
            f"## Decisions ({len(decisions)} events)",
            "",
        ])
        if decisions:
            for d in decisions:
                title = d.get("title", "?")
                why = d.get("why", "")
                decision = d.get("decision", "")
                ts = d.get("created_at", "")
                lines.append(f"- **{title}** — {decision} _{ts}_")
                if why:
                    lines.append(f"  - _Why:_ {why}")
        else:
            lines.append("_No decisions recorded in this period._")

        # Drift
        lines.extend([
            "",
            f"## Drift ({len(drift)} events)",
            "",
        ])
        if drift:
            high = [d for d in drift if d.get("severity") == "high"]
            medium = [d for d in drift if d.get("severity") == "medium"]
            low = [d for d in drift if d.get("severity") == "low"]
            if high:
                lines.append(f"### HIGH severity ({len(high)})")
                for d in high:
                    lines.append(f"- {d.get('description', '?')} ({d.get('file_path', '')})")
            if medium:
                lines.append(f"### MEDIUM severity ({len(medium)})")
                for d in medium:
                    lines.append(f"- {d.get('description', '?')} ({d.get('file_path', '')})")
            if low:
                lines.append(f"### LOW severity ({len(low)})")
                for d in low:
                    lines.append(f"- {d.get('description', '?')} ({d.get('file_path', '')})")
        else:
            lines.append("_No drift detected in this period._")

        # Recommendation
        lines.extend([
            "",
            "## Recommendation",
            "",
            f"**{recommendation.upper()}**",
            "",
        ])
        if notes:
            lines.append(notes)
        else:
            lines.append("_No additional notes._")

        lines.extend([
            "",
            "---",
            f"_Generated by SPINE v{C.SPINE_VERSION}_",
        ])

        return "\n".join(lines)
