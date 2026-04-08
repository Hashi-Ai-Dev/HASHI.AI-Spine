"""HandoffService — read-only governance handoff summary."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path

from spine import constants as C
from spine.models import MissionModel
from spine.utils.jsonl import read_jsonl


@dataclass
class HandoffResult:
    """Structured result of a handoff summary — read-only snapshot of governance state."""

    repo: str
    branch: str
    period_days: int
    generated_at: str

    # Mission
    mission_title: str
    mission_status: str
    mission_promise: str
    mission_metric: str

    # Recent activity
    recent_decisions: list[dict] = field(default_factory=list)
    recent_evidence: list[dict] = field(default_factory=list)

    # Drift — all recorded events (not filtered by period)
    drift_records: list[dict] = field(default_factory=list)

    # Totals for convenience
    total_decisions: int = 0
    total_evidence: int = 0
    total_drift: int = 0


class HandoffService:
    """
    Read-only service for generating handoff summaries.

    Reads local .spine/ state only.
    No network calls. No model calls. No state mutation.
    """

    def __init__(self, repo_root: Path, *, spine_root: Path | None = None) -> None:
        self.repo_root = repo_root
        self._spine_root = spine_root or repo_root / C.SPINE_DIR
        self.mission_path = self._spine_root / C.MISSION_FILE
        self.evidence_path = self._spine_root / C.EVIDENCE_FILE
        self.decisions_path = self._spine_root / C.DECISIONS_FILE
        self.drift_path = self._spine_root / C.DRIFT_FILE

    def generate(self, branch: str, days: int = 7) -> HandoffResult:
        """
        Generate a governance handoff summary.

        Reads:
        - mission.yaml  → mission state
        - evidence.jsonl  → recent evidence (last `days` days)
        - decisions.jsonl → recent decisions (last `days` days)
        - drift.jsonl     → all drift records (cumulative state)

        Returns a HandoffResult. Does NOT write any files.
        """
        generated_at = datetime.now(timezone.utc).isoformat()

        # --- Mission ---
        mission_title = "(no mission defined)"
        mission_status = "(none)"
        mission_promise = ""
        mission_metric = ""
        if self.mission_path.exists():
            try:
                raw = self.mission_path.read_text(encoding="utf-8")
                mission = MissionModel.from_yaml(raw)
                mission_title = mission.title
                mission_status = mission.status
                mission_promise = mission.one_sentence_promise
                mission_metric = (
                    f"{mission.success_metric.type} / {mission.success_metric.value}"
                    if mission.success_metric.value
                    else mission.success_metric.type
                )
            except Exception:
                mission_title = "(mission.yaml unreadable)"

        # --- Evidence (recent) ---
        all_evidence = read_jsonl(self.evidence_path) if self.evidence_path.exists() else []
        recent_evidence = self._filter_recent(all_evidence, days)

        # --- Decisions (recent) ---
        all_decisions = read_jsonl(self.decisions_path) if self.decisions_path.exists() else []
        recent_decisions = self._filter_recent(all_decisions, days)

        # --- Drift (all — cumulative state) ---
        drift_records = read_jsonl(self.drift_path) if self.drift_path.exists() else []

        return HandoffResult(
            repo=str(self.repo_root),
            branch=branch,
            period_days=days,
            generated_at=generated_at,
            mission_title=mission_title,
            mission_status=mission_status,
            mission_promise=mission_promise,
            mission_metric=mission_metric,
            recent_decisions=recent_decisions,
            recent_evidence=recent_evidence,
            drift_records=drift_records,
            total_decisions=len(all_decisions),
            total_evidence=len(all_evidence),
            total_drift=len(drift_records),
        )

    def _filter_recent(self, records: list[dict], days: int) -> list[dict]:
        """Return records created within the last `days` days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        cutoff_iso = cutoff.isoformat()
        return [r for r in records if r.get("created_at", "") >= cutoff_iso]

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------

    def format_summary(self, result: HandoffResult) -> str:
        """Render a compact, human-readable handoff summary."""
        lines: list[str] = []

        sep = "─" * 55

        lines.append(sep)
        lines.append(f"SPINE Handoff Summary — {result.generated_at[:10]}")
        lines.append(sep)
        lines.append(f"Repo:   {result.repo}")
        lines.append(f"Branch: {result.branch}")
        lines.append("")

        # --- Mission ---
        lines.append("MISSION")
        lines.append(f"  Title:   {result.mission_title}")
        lines.append(f"  Status:  {result.mission_status}")
        if result.mission_promise:
            lines.append(f"  Promise: {result.mission_promise}")
        if result.mission_metric:
            lines.append(f"  Metric:  {result.mission_metric}")
        lines.append("")

        # --- Recent Decisions ---
        period_label = f"last {result.period_days} days"
        n_dec = len(result.recent_decisions)
        lines.append(f"RECENT DECISIONS ({period_label} — {n_dec} recorded)")
        if result.recent_decisions:
            for d in result.recent_decisions:
                title = d.get("title", "?")
                decision = d.get("decision", "")
                ts = d.get("created_at", "")[:10]
                lines.append(f"  • [{ts}] {title}")
                if decision:
                    lines.append(f"    {decision}")
        else:
            lines.append("  (none in this period)")
        lines.append("")

        # --- Recent Evidence ---
        n_ev = len(result.recent_evidence)
        lines.append(f"RECENT EVIDENCE ({period_label} — {n_ev} recorded)")
        if result.recent_evidence:
            for e in result.recent_evidence:
                kind = e.get("kind", "?")
                desc = e.get("description", "")
                ts = e.get("created_at", "")[:10]
                lines.append(f"  • [{kind}] {desc} — {ts}")
        else:
            lines.append("  (none in this period)")
        lines.append("")

        # --- Drift State ---
        n_drift = len(result.drift_records)
        high = [d for d in result.drift_records if d.get("severity") == "high"]
        medium = [d for d in result.drift_records if d.get("severity") == "medium"]
        low = [d for d in result.drift_records if d.get("severity") == "low"]

        severity_parts: list[str] = []
        if high:
            severity_parts.append(f"{len(high)} high")
        if medium:
            severity_parts.append(f"{len(medium)} medium")
        if low:
            severity_parts.append(f"{len(low)} low")
        severity_str = ", ".join(severity_parts) if severity_parts else "none"

        drift_header = f"DRIFT STATE ({n_drift} total" + (f" — {severity_str}" if n_drift else "") + ")"
        lines.append(drift_header)
        if result.drift_records:
            for d in result.drift_records:
                sev = d.get("severity", "?").upper()
                desc = d.get("description", "?")
                lines.append(f"  [{sev}] {desc}")
        else:
            lines.append("  (no drift recorded)")
        lines.append("")

        lines.append(sep)
        lines.append(f"Generated by SPINE v{C.SPINE_VERSION}")
        lines.append(sep)

        return "\n".join(lines)
