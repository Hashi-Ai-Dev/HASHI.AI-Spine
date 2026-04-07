"""spine brief command."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import typer
from rich.console import Console

from spine.cli.app import app, resolve_roots, EXIT_VALIDATION, EXIT_CONTEXT
from spine.services.brief_service import BriefService
from spine.services.mission_service import MissionService, MissionNotFoundError
from spine.utils.paths import get_current_branch, get_default_branch, format_context_line

console = Console()


@app.command("brief")
def brief_cmd(
    cwd: Path | None = typer.Option(
        None,
        "--cwd",
        help="Target repository path. Overrides SPINE_ROOT. Precedence: --cwd > SPINE_ROOT > cwd.",
    ),
    target: str = typer.Option(
        ...,
        "--target",
        "-t",
        help="Target agent: claude or codex",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output result as JSON (machine-readable). Exit codes still apply.",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress context line and alias update message. Prints canonical path only.",
    ),
) -> None:
    """
    Generate a mission brief for a specific agent target.

    Generates a markdown brief in .spine/briefs/{target}/ based on mission.yaml.
    Also updates .spine/briefs/{target}/latest.md as a symlink replacement.

    Exit codes:
      0  Brief generated successfully
      1  Validation failure — invalid --target value
      2  Context failure   — repo not found or mission.yaml missing
    """
    if target not in ("claude", "codex"):
        msg = f"target must be 'claude' or 'codex', got '{target}'"
        if json_output:
            print(json.dumps({"error": msg, "exit_code": EXIT_VALIDATION}, indent=2))
        else:
            console.print(f"[bold red]Error:[/bold red] {msg}")
        raise typer.Exit(EXIT_VALIDATION)

    try:
        repo_root, spine_root = resolve_roots(cwd)
    except Exception as exc:
        if json_output:
            print(json.dumps({"error": str(exc), "exit_code": EXIT_CONTEXT}, indent=2))
        else:
            console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(EXIT_CONTEXT)

    # Get mission
    mission_service = MissionService(repo_root, spine_root=spine_root)
    try:
        mission_result = mission_service.show()
    except MissionNotFoundError as exc:
        if json_output:
            print(json.dumps({"error": str(exc), "exit_code": EXIT_CONTEXT}, indent=2))
        else:
            console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(EXIT_CONTEXT)

    brief_service = BriefService(repo_root, spine_root=spine_root)
    if target == "claude":
        canonical, latest = brief_service.generate_claude(mission_result.mission)
    else:
        canonical, latest = brief_service.generate_codex(mission_result.mission)

    if json_output:
        data = {
            "target": target,
            "canonical_path": str(canonical),
            "latest_path": str(latest),
            "mission_title": mission_result.mission.title,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        print(json.dumps(data, indent=2))
        return

    if not quiet:
        branch = get_current_branch(repo_root)
        default_branch = get_default_branch(repo_root)
        context_line = format_context_line(repo_root, branch, default_branch)
        console.print(f"[dim]{context_line}[/dim]")

    console.print(f"[bold green]Brief generated:[/bold green] {canonical}")
    if not quiet:
        console.print(f"[dim]Latest alias updated:[/dim]  {latest}")
