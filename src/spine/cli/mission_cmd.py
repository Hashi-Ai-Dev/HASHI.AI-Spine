"""spine mission show/set commands — spec-compliant nesting."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from spine.cli.app import app, resolve_roots
from spine.services.mission_service import (
    MissionService,
    MissionValidationError,
    MissionNotFoundError,
)

console = Console()

# ---------------------------------------------------------------------------
# Mission command group (spine mission <action>)
# ---------------------------------------------------------------------------
mission_app = typer.Typer()
app.add_typer(mission_app, name="mission", help="Manage the active mission.")


@mission_app.command("show", help="Display the current mission.")
def mission_show(
    cwd: Path | None = typer.Option(
        None,
        "--cwd",
        help="Target repository path (for external-repo usage without cd or SPINE_ROOT).",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output mission as JSON (machine-readable).",
    ),
) -> None:
    """Display the current mission from .spine/mission.yaml."""
    try:
        repo_root, spine_root = resolve_roots(cwd)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(1)

    service = MissionService(repo_root, spine_root=spine_root)
    try:
        result = service.show()
    except MissionNotFoundError as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(1)

    mission = result.mission

    if json_output:
        data = mission.model_dump(mode="python")
        print(json.dumps(data, indent=2, default=str))
        return

    table = Table(title="Mission", box=None, show_header=False)
    table.add_column("Field", style="bold cyan")
    table.add_column("Value")

    table.add_row("id", mission.id)
    table.add_row("title", mission.title)
    table.add_row("status", mission.status)
    table.add_row("target_user", mission.target_user)
    table.add_row("user_problem", mission.user_problem)
    table.add_row("one_sentence_promise", mission.one_sentence_promise)
    table.add_row(
        "success_metric",
        f"{mission.success_metric.type}: {mission.success_metric.value}",
    )
    table.add_row("allowed_scope", ", ".join(mission.allowed_scope) or "_none_")
    table.add_row("forbidden_expansions", ", ".join(mission.forbidden_expansions) or "_none_")
    table.add_row("proof_requirements", ", ".join(mission.proof_requirements) or "_none_")
    table.add_row("kill_conditions", ", ".join(mission.kill_conditions) or "_none_")
    table.add_row("created_at", mission.created_at)
    table.add_row("updated_at", mission.updated_at)

    console.print(table)


@mission_app.command("set", help="Update mission fields in .spine/mission.yaml.")
def mission_set(
    cwd: Path | None = typer.Option(
        None,
        "--cwd",
        help="Target repository path (for external-repo usage without cd or SPINE_ROOT).",
    ),
    title: str | None = typer.Option(None, "--title", help="Mission title"),
    status: str | None = typer.Option(None, "--status", help="Status: active/paused/complete/killed"),
    target_user: str | None = typer.Option(None, "--target-user", help="Target user description"),
    user_problem: str | None = typer.Option(None, "--user-problem", help="User problem description"),
    one_sentence_promise: str | None = typer.Option(None, "--promise", help="One-sentence promise"),
    success_metric_type: str | None = typer.Option(None, "--metric-type", help="milestone/metric/user_signal"),
    success_metric_value: str | None = typer.Option(None, "--metric-value", help="Success metric value"),
    allowed_scope: str | None = typer.Option(None, "--scope", help="Comma-separated allowed scope items"),
    forbidden_expansions: str | None = typer.Option(None, "--forbid", help="Comma-separated forbidden expansions"),
    proof_requirements: str | None = typer.Option(None, "--proof", help="Comma-separated proof requirements"),
    kill_conditions: str | None = typer.Option(None, "--kill", help="Comma-separated kill conditions"),
) -> None:
    """
    Update mission fields in .spine/mission.yaml.

    All options are optional. Only provided fields are updated.
    The updated_at timestamp is always refreshed.
    """
    try:
        repo_root, spine_root = resolve_roots(cwd)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(1)

    def parse_list(s: str | None) -> list[str] | None:
        if s is None:
            return None
        return [item.strip() for item in s.split(",") if item.strip()]

    service = MissionService(repo_root, spine_root=spine_root)
    try:
        mission = service.set(
            title=title,
            status=status,
            target_user=target_user,
            user_problem=user_problem,
            one_sentence_promise=one_sentence_promise,
            success_metric_type=success_metric_type,
            success_metric_value=success_metric_value,
            allowed_scope=parse_list(allowed_scope),
            forbidden_expansions=parse_list(forbidden_expansions),
            proof_requirements=parse_list(proof_requirements),
            kill_conditions=parse_list(kill_conditions),
        )
        console.print(f"[bold green]Mission updated:[/bold green] {mission.title}")
        console.print(f"Status: {mission.status}")
        console.print(f"Updated at: {mission.updated_at}")
    except MissionNotFoundError as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(1)
    except MissionValidationError as exc:
        console.print(f"[bold red]Validation error:[/bold red] {exc}")
        raise typer.Exit(1)
