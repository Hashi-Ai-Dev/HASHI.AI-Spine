"""spine mcp serve command — spec-compliant nesting with blocking stdio MCP server."""

from __future__ import annotations

import sys
import json
from pathlib import Path

import typer
from spine.cli.app import app, resolve_roots

# ---------------------------------------------------------------------------
# MCP command group (spine mcp <action>)
# ---------------------------------------------------------------------------
mcp_app = typer.Typer()
app.add_typer(mcp_app, name="mcp", help="SPINE MCP server.")


def _get_mcp_modules():
    """Lazy import to avoid hard dependency until confirmed available."""
    try:
        from mcp import Server as McpServer
        from mcp.types import Resource, Tool, TextResourceContents, TextContent
        return (McpServer, Resource, Tool, TextResourceContents, TextContent)
    except ImportError:
        return None


@mcp_app.command("serve", help="Start the SPINE MCP server (blocking stdio mode).")
def mcp_serve(
    cwd: Path | None = typer.Option(
        None,
        "--cwd",
        help="Target repository path (for external-repo usage without cd or SPINE_ROOT).",
    ),
) -> None:
    """
    Start the SPINE MCP server (blocking stdio mode).

    This is a separate blocking command. It does NOT daemonize.
    Exposes resources and tools via MCP stdio protocol.
    """
    _mcp_modules = _get_mcp_modules()
    if _mcp_modules is None:
        print("ERROR: MCP package not installed. Run: uv add mcp", file=sys.stderr)
        raise typer.Exit(1)

    McpServer, _Resource, _Tool, _TextResourceContents, TextContent = _mcp_modules

    try:
        repo_root, spine_root = resolve_roots(cwd)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise typer.Exit(1)

    from spine.services.brief_service import BriefService
    from spine.services.decision_service import DecisionService
    from spine.services.drift_service import DriftService
    from spine.services.evidence_service import EvidenceService
    from spine.services.mission_service import MissionService
    from spine.services.opportunity_service import OpportunityService
    from spine.services.review_service import ReviewService
    from spine import constants as C

    mission_service = MissionService(repo_root, spine_root=spine_root)
    brief_service = BriefService(repo_root, spine_root=spine_root)
    evidence_service = EvidenceService(repo_root, spine_root=spine_root)
    decision_service = DecisionService(repo_root, spine_root=spine_root)
    drift_service = DriftService(repo_root, spine_root=spine_root)
    review_service = ReviewService(repo_root, spine_root=spine_root)
    opportunity_service = OpportunityService(repo_root, spine_root=spine_root)

    server = McpServer(name="spine", version="0.1.0")

    @server.list_resources()
    def list_resources():
        resources = []
        try:
            mission_result = mission_service.show()
            mission = mission_result.mission
            resources.append(_mcp_modules[1](
                uri="spine://mission",
                name="Active Mission",
                description=f"Current mission: {mission.title} ({mission.status})",
                mimeType="application/x-yaml",
            ))
        except Exception:
            pass

        constraints_path = repo_root / C.SPINE_DIR / C.CONSTRAINTS_FILE
        if constraints_path.exists():
            resources.append(_mcp_modules[1](
                uri="spine://constraints",
                name="Constraints",
                description="Operational constraints and behavior rules",
                mimeType="application/x-yaml",
            ))

        evidence_path = repo_root / C.SPINE_DIR / C.EVIDENCE_FILE
        if evidence_path.exists():
            resources.append(_mcp_modules[1](
                uri="spine://evidence",
                name="Recent Evidence",
                description="Evidence records",
                mimeType="application/jsonl",
            ))

        decisions_path = repo_root / C.SPINE_DIR / C.DECISIONS_FILE
        if decisions_path.exists():
            resources.append(_mcp_modules[1](
                uri="spine://decisions",
                name="Recent Decisions",
                description="Decision records",
                mimeType="application/jsonl",
            ))

        drift_path = repo_root / C.SPINE_DIR / C.DRIFT_FILE
        if drift_path.exists():
            resources.append(_mcp_modules[1](
                uri="spine://drift",
                name="Open Drift",
                description="Drift detection events",
                mimeType="application/jsonl",
            ))

        reviews_dir = repo_root / C.SPINE_DIR / C.REVIEWS_DIR
        latest_review = reviews_dir / "latest.md" if reviews_dir.exists() else None
        if latest_review and latest_review.exists():
            resources.append(_mcp_modules[1](
                uri="spine://review/latest",
                name="Latest Review",
                description="Most recent weekly review",
                mimeType="text/markdown",
            ))

        return resources

    @server.read_resource()
    def read_resource(uri: str):
        if uri == "spine://mission":
            mission_result = mission_service.show()
            return _mcp_modules[3](
                uri=uri,
                mimeType="application/x-yaml",
                text=mission_result.mission.to_yaml(),
            )
        elif uri == "spine://constraints":
            path = repo_root / C.SPINE_DIR / C.CONSTRAINTS_FILE
            return _mcp_modules[3](
                uri=uri,
                mimeType="application/x-yaml",
                text=path.read_text(encoding="utf-8"),
            )
        elif uri == "spine://evidence":
            path = repo_root / C.SPINE_DIR / C.EVIDENCE_FILE
            return _mcp_modules[3](
                uri=uri,
                mimeType="application/jsonl",
                text=path.read_text(encoding="utf-8") if path.exists() else "",
            )
        elif uri == "spine://decisions":
            path = repo_root / C.SPINE_DIR / C.DECISIONS_FILE
            return _mcp_modules[3](
                uri=uri,
                mimeType="application/jsonl",
                text=path.read_text(encoding="utf-8") if path.exists() else "",
            )
        elif uri == "spine://drift":
            path = repo_root / C.SPINE_DIR / C.DRIFT_FILE
            return _mcp_modules[3](
                uri=uri,
                mimeType="application/jsonl",
                text=path.read_text(encoding="utf-8") if path.exists() else "",
            )
        elif uri == "spine://review/latest":
            path = repo_root / C.SPINE_DIR / C.REVIEWS_DIR / "latest.md"
            return _mcp_modules[3](
                uri=uri,
                mimeType="text/markdown",
                text=path.read_text(encoding="utf-8") if path.exists() else "",
            )
        return None

    @server.list_tools()
    def list_tools():
        return [
            _mcp_modules[2](
                name="mission_get",
                description="Get the current mission",
                inputSchema={"type": "object", "properties": {}},
            ),
            _mcp_modules[2](
                name="mission_update",
                description="Update mission fields",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "status": {"type": "string", "enum": ["active", "paused", "complete", "killed"]},
                        "allowed_scope": {"type": "array", "items": {"type": "string"}},
                        "forbidden_expansions": {"type": "array", "items": {"type": "string"}},
                    },
                },
            ),
            _mcp_modules[2](
                name="brief_generate",
                description="Generate a mission brief",
                inputSchema={
                    "type": "object",
                    "properties": {"target": {"type": "string", "enum": ["claude", "codex"]}},
                    "required": ["target"],
                },
            ),
            _mcp_modules[2](
                name="evidence_add",
                description="Add an evidence record",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "kind": {"type": "string", "enum": [
                            "brief_generated", "commit", "pr", "test_pass",
                            "review_done", "demo", "user_feedback", "payment", "kill", "narrow"
                        ]},
                        "description": {"type": "string"},
                        "evidence_url": {"type": "string"},
                    },
                    "required": ["kind"],
                },
            ),
            _mcp_modules[2](
                name="decision_add",
                description="Add a decision record",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "why": {"type": "string"},
                        "decision": {"type": "string"},
                        "alternatives": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["title", "why", "decision"],
                },
            ),
            _mcp_modules[2](
                name="drift_scan",
                description="Scan for scope drift",
                inputSchema={
                    "type": "object",
                    "properties": {"against_branch": {"type": "string"}},
                },
            ),
            _mcp_modules[2](
                name="review_generate",
                description="Generate a weekly review",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "days": {"type": "integer", "default": 7},
                        "recommendation": {"type": "string", "enum": ["continue", "narrow", "pivot", "kill", "ship_as_is"], "default": "continue"},
                        "notes": {"type": "string"},
                    },
                },
            ),
            _mcp_modules[2](
                name="opportunity_score",
                description="Score an opportunity",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "pain": {"type": "integer", "minimum": 1, "maximum": 5, "default": 3},
                        "founder_fit": {"type": "integer", "minimum": 1, "maximum": 5, "default": 3},
                        "time_to_proof": {"type": "integer", "minimum": 1, "maximum": 5, "default": 3},
                        "monetization": {"type": "integer", "minimum": 1, "maximum": 5, "default": 3},
                        "sprawl_risk": {"type": "integer", "minimum": 1, "maximum": 5, "default": 3},
                        "maintenance_burden": {"type": "integer", "minimum": 1, "maximum": 5, "default": 3},
                    },
                    "required": ["title"],
                },
            ),
        ]

    @server.call_tool()
    def call_tool(name: str, arguments: dict):
        if name == "mission_get":
            mission_result = mission_service.show()
            return [TextContent(
                type="text",
                text=json.dumps(mission_result.mission.model_dump(mode="json"), indent=2),
            )]
        elif name == "mission_update":
            mission = mission_service.set(**{k: v for k, v in arguments.items() if v is not None})
            return [TextContent(
                type="text",
                text=json.dumps(mission.model_dump(mode="json"), indent=2),
            )]
        elif name == "brief_generate":
            target = arguments.get("target", "claude")
            mission_result = mission_service.show()
            if target == "claude":
                path = brief_service.generate_claude(mission_result.mission)
            else:
                path = brief_service.generate_codex(mission_result.mission)
            return [TextContent(
                type="text",
                text=f"Brief generated at: {path}",
            )]
        elif name == "evidence_add":
            evidence = evidence_service.add(**arguments)
            return [TextContent(
                type="text",
                text=json.dumps(evidence.to_json(), indent=2),
            )]
        elif name == "decision_add":
            decision = decision_service.add(**arguments)
            return [TextContent(
                type="text",
                text=json.dumps(decision.to_json(), indent=2),
            )]
        elif name == "drift_scan":
            result = drift_service.scan(against_branch=arguments.get("against_branch"))
            return [TextContent(
                type="text",
                text=json.dumps({
                    "events": [e.to_json() for e in result.events],
                    "summary": result.severity_summary,
                }, indent=2),
            )]
        elif name == "review_generate":
            path = review_service.generate_weekly(
                days=arguments.get("days", 7),
                recommendation=arguments.get("recommendation", "continue"),
                notes=arguments.get("notes", ""),
            )
            return [TextContent(
                type="text",
                text=f"Review generated at: {path}",
            )]
        elif name == "opportunity_score":
            opp = opportunity_service.score(**arguments)
            return [TextContent(
                type="text",
                text=json.dumps(opp.to_json(), indent=2),
            )]
        return []

    import asyncio

    async def run_server():
        async with server:
            await server.run(sys.stdin, sys.stdout, server.create_initialization_options())

    asyncio.run(run_server())
