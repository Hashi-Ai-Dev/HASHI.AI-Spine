"""spine brief command."""

from __future__ import annotations

import typer
from rich.console import Console

from spine.cli.app import app, resolve_roots
from spine.services.brief_service import BriefService
from spine.services.mission_service import MissionService, MissionNotFoundError

console = Console()


@app.command("brief")
def brief_cmd(
    target: str = typer.Option(
        ...,
        "--target",
        "-t",
        help="Target agent: claude or codex",
    ),
) -> None:
    """
    Generate a mission brief for a specific agent target.

    Generates a markdown brief in .spine/briefs/{target}/ based on mission.yaml.
    Also updates .spine/briefs/{target}/latest.md as a symlink replacement.
    """
    if target not in ("claude", "codex"):
        console.print(f"[bold red]Error:[/bold red] target must be 'claude' or 'codex', got '{target}'")
        raise typer.Exit(1)

    try:
        repo_root, spine_root = resolve_roots()
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(1)

    # Get mission
    mission_service = MissionService(repo_root, spine_root=spine_root)
    try:
        mission_result = mission_service.show()
    except MissionNotFoundError as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(1)

    brief_service = BriefService(repo_root, spine_root=spine_root)
    if target == "claude":
        canonical, latest = brief_service.generate_claude(mission_result.mission)
    else:
        canonical, latest = brief_service.generate_codex(mission_result.mission)

    console.print(f"[bold green]Brief generated:[/bold green] {canonical}")
    console.print(f"[dim]Latest alias updated:[/dim]  {latest}")
