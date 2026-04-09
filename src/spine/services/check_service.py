"""CheckService — preflight checkpoints for before-work and before-PR governance."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from spine import constants as C
from spine.services.doctor_service import DoctorService
from spine.utils.jsonl import read_jsonl

CheckResult = Literal["pass", "review_recommended"]


@dataclass
class CheckItem:
    """A single result from a preflight check."""

    name: str
    status: Literal["pass", "warn", "fail"]
    message: str
    category: str = ""
    detail: list[dict] | None = field(default=None)


@dataclass
class BeforePrResult:
    """Aggregated result of the before-pr preflight checks."""

    repo: str
    branch: str
    items: list[CheckItem] = field(default_factory=list)

    @property
    def result(self) -> CheckResult:
        """Return overall result: pass if no fails or warns, else review_recommended."""
        for item in self.items:
            if item.status in ("warn", "fail"):
                return "review_recommended"
        return "pass"

    @property
    def passed(self) -> bool:
        return self.result == "pass"


@dataclass
class BeforeWorkResult:
    """Aggregated result of the before-work start-session preflight checks."""

    repo: str
    branch: str
    items: list[CheckItem] = field(default_factory=list)

    @property
    def result(self) -> CheckResult:
        """Return overall result: pass if no fails or warns, else review_recommended."""
        for item in self.items:
            if item.status in ("warn", "fail"):
                return "review_recommended"
        return "pass"

    @property
    def passed(self) -> bool:
        return self.result == "pass"


class CheckService:
    """
    Preflight checkpoint service for `spine check before-pr`.

    Composes existing DoctorService and reads drift/evidence/decision state.
    Does NOT mutate any state, make network calls, or install hooks.
    """

    def __init__(self, repo_root: Path, *, spine_root: Path | None = None) -> None:
        self.repo_root = repo_root
        self._spine_root = spine_root or repo_root / C.SPINE_DIR

    def run_before_work(self, branch: str) -> BeforeWorkResult:
        """
        Run all before-work start-session preflight checks.

        Checks (in order):
        1. Mission presence/readability
        2. Doctor-style repo health (no errors)
        3. Branch/repo context (always passes — informational)
        4. Recent brief orientation context

        Focus: "is this repo in a state I can responsibly begin work in?"
        Does NOT require evidence/decisions (those accumulate during work).
        Does NOT block on drift (you may be starting work to fix it).

        Returns a BeforeWorkResult with all individual check items and
        the final aggregated result (pass | review_recommended).
        """
        result = BeforeWorkResult(repo=str(self.repo_root), branch=branch)

        result.items.append(self._check_spine_dir())
        if result.items[-1].status == "fail":
            # Cannot proceed with further checks — .spine/ is missing
            return result

        result.items.append(self._check_mission())
        result.items.extend(self._check_doctor_health())
        result.items.append(self._check_branch_context(branch))
        result.items.append(self._check_recent_brief())

        return result

    def run_before_pr(self, branch: str) -> BeforePrResult:
        """
        Run all before-pr preflight checks.

        Checks (in order):
        1. Mission presence/readability
        2. Doctor-style repo health (no errors)
        3. Open drift in drift.jsonl
        4. Evidence presence (lightweight)
        5. Decision presence (lightweight)

        Returns a BeforePrResult with all individual check items and
        the final aggregated result (pass | review_recommended).
        """
        result = BeforePrResult(repo=str(self.repo_root), branch=branch)

        result.items.append(self._check_spine_dir())
        if result.items[-1].status == "fail":
            # Cannot proceed with further checks — .spine/ is missing
            return result

        result.items.append(self._check_mission())
        result.items.extend(self._check_doctor_health())
        result.items.append(self._check_open_drift())
        result.items.append(self._check_evidence_presence())
        result.items.append(self._check_decision_presence())

        return result

    # ------------------------------------------------------------------
    # Individual checks
    # ------------------------------------------------------------------

    def _check_spine_dir(self) -> CheckItem:
        """Check that .spine/ directory exists."""
        if not self._spine_root.exists():
            return CheckItem(
                name="spine_dir",
                status="fail",
                message=".spine/ not found — run 'spine init' to bootstrap governance state",
                category="structure",
            )
        return CheckItem(
            name="spine_dir",
            status="pass",
            message=".spine/ found",
            category="structure",
        )

    def _check_mission(self) -> CheckItem:
        """Check mission.yaml is present and readable."""
        mission_path = self._spine_root / C.MISSION_FILE
        if not mission_path.exists():
            return CheckItem(
                name="mission",
                status="fail",
                message="mission.yaml not found",
                category="config",
            )
        try:
            from spine.models import MissionModel
            raw = mission_path.read_text(encoding="utf-8")
            MissionModel.from_yaml(raw)
        except Exception as exc:
            return CheckItem(
                name="mission",
                status="fail",
                message=f"mission.yaml unreadable: {exc}",
                category="config",
            )
        return CheckItem(
            name="mission",
            status="pass",
            message="mission.yaml present and readable",
            category="config",
        )

    def _check_doctor_health(self) -> list[CheckItem]:
        """Run doctor checks and surface errors as blocking failures.

        Doctor *warnings* (e.g. missing optional subdirectories on a fresh or
        cloned repo) are advisory only — they do not force review_recommended.
        Only doctor *errors* block the check.
        """
        service = DoctorService(self.repo_root, spine_root=self._spine_root)
        doctor_result = service.check()

        items: list[CheckItem] = []
        errors = [i for i in doctor_result.issues if i.severity == "error"]
        warnings = [i for i in doctor_result.issues if i.severity == "warning"]

        # Build structured detail for all issues (errors + warnings)
        detail: list[dict] | None = None
        if doctor_result.issues:
            detail = [
                {"severity": i.severity, "file": i.file, "message": i.message}
                for i in doctor_result.issues
            ]

        if errors:
            # Errors are genuine repo-health failures — block the check
            msg = "; ".join(f"{i.file}: {i.message}" for i in errors[:3])
            if len(errors) > 3:
                msg += f" (and {len(errors) - 3} more)"
            items.append(CheckItem(
                name="doctor",
                status="fail",
                message=f"{len(errors)} doctor error(s): {msg}",
                category="health",
                detail=detail,
            ))
        else:
            # No errors.  Warnings are benign/advisory (e.g. missing optional
            # subdirectories on a freshly cloned repo) — show them but pass.
            if warnings:
                msg = "; ".join(f"{i.file}: {i.message}" for i in warnings[:3])
                if len(warnings) > 3:
                    msg += f" (and {len(warnings) - 3} more)"
                items.append(CheckItem(
                    name="doctor",
                    status="pass",
                    message=f"repo health OK ({len(warnings)} advisory warning(s): {msg})",
                    category="health",
                    detail=detail,
                ))
            else:
                items.append(CheckItem(
                    name="doctor",
                    status="pass",
                    message="repo health OK",
                    category="health",
                ))

        return items

    def _check_open_drift(self) -> CheckItem:
        """Check whether any drift events are recorded in drift.jsonl."""
        drift_path = self._spine_root / C.DRIFT_FILE
        if not drift_path.exists():
            return CheckItem(
                name="drift",
                status="pass",
                message="no drift log found (clean)",
                category="history",
            )
        try:
            records = read_jsonl(drift_path)
        except Exception:
            return CheckItem(
                name="drift",
                status="warn",
                message="drift.jsonl unreadable — verify manually",
                category="history",
            )
        if records:
            high = sum(1 for r in records if r.get("severity") == "high")
            medium = sum(1 for r in records if r.get("severity") == "medium")
            low = sum(1 for r in records if r.get("severity") == "low")
            parts = []
            if high:
                parts.append(f"{high} high")
            if medium:
                parts.append(f"{medium} medium")
            if low:
                parts.append(f"{low} low")
            severity_str = ", ".join(parts) if parts else str(len(records))
            return CheckItem(
                name="drift",
                status="warn",
                message=f"{len(records)} drift event(s) logged ({severity_str}) — review before PR",
                category="history",
            )
        return CheckItem(
            name="drift",
            status="pass",
            message="no drift events logged",
            category="history",
        )

    def _check_evidence_presence(self) -> CheckItem:
        """Check whether any evidence records exist (lightweight — presence only)."""
        evidence_path = self._spine_root / C.EVIDENCE_FILE
        if not evidence_path.exists():
            return CheckItem(
                name="evidence",
                status="warn",
                message="evidence.jsonl not found — consider logging evidence before PR",
                category="history",
            )
        try:
            records = read_jsonl(evidence_path)
        except Exception:
            return CheckItem(
                name="evidence",
                status="warn",
                message="evidence.jsonl unreadable",
                category="history",
            )
        if not records:
            return CheckItem(
                name="evidence",
                status="warn",
                message="no evidence recorded — consider 'spine evidence add' before PR",
                category="history",
            )
        return CheckItem(
            name="evidence",
            status="pass",
            message=f"{len(records)} evidence record(s) present",
            category="history",
        )

    def _check_branch_context(self, branch: str) -> CheckItem:
        """Report current branch context — always passes (informational)."""
        return CheckItem(
            name="branch_context",
            status="pass",
            message=f"on branch: {branch}",
            category="context",
        )

    def _check_recent_brief(self) -> CheckItem:
        """Check whether a recent brief exists for orientation context.

        Looks for any brief files under .spine/briefs/. If none are found,
        suggests running 'spine brief' for orientation context.
        """
        briefs_dir = self._spine_root / C.BRIEFS_DIR
        if not briefs_dir.exists():
            return CheckItem(
                name="recent_brief",
                status="warn",
                message=(
                    "no briefs found — run 'spine brief' to generate orientation context, "
                    "or proceed if starting a fresh session"
                ),
                category="context",
            )
        # Look for any latest.md or timestamped brief files across subdirs
        brief_files = list(briefs_dir.rglob("*.md"))
        if not brief_files:
            return CheckItem(
                name="recent_brief",
                status="warn",
                message=(
                    "no briefs found — run 'spine brief' to generate orientation context, "
                    "or proceed if starting a fresh session"
                ),
                category="context",
            )
        # Use the most recently modified brief file as orientation signal
        latest = max(brief_files, key=lambda p: p.stat().st_mtime)
        return CheckItem(
            name="recent_brief",
            status="pass",
            message=f"{len(brief_files)} brief file(s) available — most recent: {latest.name}",
            category="context",
        )

    def _check_decision_presence(self) -> CheckItem:
        """Check whether any decision records exist (lightweight — presence only)."""
        decisions_path = self._spine_root / C.DECISIONS_FILE
        if not decisions_path.exists():
            return CheckItem(
                name="decisions",
                status="warn",
                message="decisions.jsonl not found — consider logging decisions before PR",
                category="history",
            )
        try:
            records = read_jsonl(decisions_path)
        except Exception:
            return CheckItem(
                name="decisions",
                status="warn",
                message="decisions.jsonl unreadable",
                category="history",
            )
        if not records:
            return CheckItem(
                name="decisions",
                status="warn",
                message="no decisions recorded — consider 'spine decision add' before PR",
                category="history",
            )
        return CheckItem(
            name="decisions",
            status="pass",
            message=f"{len(records)} decision record(s) present",
            category="history",
        )
