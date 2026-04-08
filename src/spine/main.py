"""SPINE CLI entry point."""

from __future__ import annotations

# Import app and all commands so they register on the app object.
from spine.cli.app import app
import spine.cli.init_cmd  # noqa: F401 — registers @app.command("init")
import spine.cli.mission_cmd  # noqa: F401 — registers @app.command("mission"), "mission-set"
import spine.cli.opportunity_cmd  # noqa: F401 — registers @app.command("opportunity"), "opportunity-score"
import spine.cli.evidence_cmd  # noqa: F401 — registers @app.command("evidence"), "evidence-add"
import spine.cli.decision_cmd  # noqa: F401 — registers @app.command("decision"), "decision-add"
import spine.cli.drift_cmd  # noqa: F401 — registers @app.command("drift"), "drift-scan"
import spine.cli.brief_cmd  # noqa: F401 — registers @app.command("brief")
import spine.cli.review_cmd  # noqa: F401 — registers @app.command("review"), "review-weekly"
import spine.cli.doctor_cmd  # noqa: F401 — registers @app.command("doctor")
import spine.cli.mcp_cmd  # noqa: F401 — registers @app.command("mcp")
import spine.cli.check_cmd  # noqa: F401 — registers @app.command("check"), "check before-pr"
import spine.cli.drafts_cmd  # noqa: F401 — registers @app.command("drafts"), "drafts list", "drafts confirm"

__all__ = ["app"]
