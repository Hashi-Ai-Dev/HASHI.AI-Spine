"""spine mission show/set/refine/confirm/drafts commands."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from spine.cli.app import app, resolve_roots, EXIT_VALIDATION, EXIT_CONTEXT
from spine.services.mission_service import (
    MissionService,
    MissionValidationError,
    MissionNotFoundError,
    MissionDraftNotFoundError,
)
from spine.utils.paths import get_current_branch, get_default_branch, format_context_line

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
        help="Target repository path. Overrides SPINE_ROOT. Precedence: --cwd > SPINE_ROOT > cwd.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output mission as JSON (machine-readable). Exit codes still apply.",
    ),
) -> None:
    """
    Display the current mission from .spine/mission.yaml.

    Exit codes:
      0  Success
      2  Context failure — repo not found or mission.yaml missing
    """
    try:
        repo_root, spine_root = resolve_roots(cwd)
    except Exception as exc:
        if json_output:
            print(json.dumps({"error": str(exc), "exit_code": EXIT_CONTEXT}, indent=2))
        else:
            console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(EXIT_CONTEXT)

    service = MissionService(repo_root, spine_root=spine_root)
    try:
        result = service.show()
    except MissionNotFoundError as exc:
        if json_output:
            print(json.dumps({"error": str(exc), "exit_code": EXIT_CONTEXT}, indent=2))
        else:
            console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(EXIT_CONTEXT)

    mission = result.mission

    if json_output:
        data = mission.model_dump(mode="python")
        print(json.dumps(data, indent=2, default=str))
        return

    branch = get_current_branch(repo_root)
    default_branch = get_default_branch(repo_root)
    context_line = format_context_line(repo_root, branch, default_branch)
    console.print(f"[dim]{context_line}[/dim]")

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
        help="Target repository path. Overrides SPINE_ROOT. Precedence: --cwd > SPINE_ROOT > cwd.",
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

    Exit codes:
      0  Success
      1  Validation failure — invalid field value (e.g. bad --status)
      2  Context failure   — repo not found or mission.yaml missing
    """
    try:
        repo_root, spine_root = resolve_roots(cwd)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(EXIT_CONTEXT)

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
        raise typer.Exit(EXIT_CONTEXT)
    except MissionValidationError as exc:
        console.print(f"[bold red]Validation error:[/bold red] {exc}")
        raise typer.Exit(EXIT_VALIDATION)


@mission_app.command("refine", help="Create a draft mission refinement without mutating canonical state.")
def mission_refine(
    cwd: Path | None = typer.Option(
        None,
        "--cwd",
        help="Target repository path. Overrides SPINE_ROOT. Precedence: --cwd > SPINE_ROOT > cwd.",
    ),
    title: str | None = typer.Option(None, "--title", help="Proposed mission title"),
    status: str | None = typer.Option(None, "--status", help="Proposed status: active/paused/complete/killed"),
    target_user: str | None = typer.Option(None, "--target-user", help="Proposed target user description"),
    user_problem: str | None = typer.Option(None, "--user-problem", help="Proposed user problem description"),
    one_sentence_promise: str | None = typer.Option(None, "--promise", help="Proposed one-sentence promise"),
    success_metric_type: str | None = typer.Option(None, "--metric-type", help="Proposed metric type: milestone/metric/user_signal"),
    success_metric_value: str | None = typer.Option(None, "--metric-value", help="Proposed success metric value"),
    allowed_scope: str | None = typer.Option(None, "--scope", help="Proposed comma-separated allowed scope items"),
    forbidden_expansions: str | None = typer.Option(None, "--forbid", help="Proposed comma-separated forbidden expansions"),
    proof_requirements: str | None = typer.Option(None, "--proof", help="Proposed comma-separated proof requirements"),
    kill_conditions: str | None = typer.Option(None, "--kill", help="Proposed comma-separated kill conditions"),
) -> None:
    """
    Create a draft mission refinement at .spine/drafts/missions/<timestamp>.yaml.

    Reads canonical mission.yaml as the base, applies proposed field overrides,
    and saves the result as a clearly-labeled non-canonical draft.
    Does NOT mutate .spine/mission.yaml.

    After review, promote the draft with:
      spine mission confirm <draft_id>

    Exit codes:
      0  Draft created successfully
      1  Validation failure — invalid field value
      2  Context failure   — repo not found or mission.yaml missing
    """
    try:
        repo_root, spine_root = resolve_roots(cwd)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(EXIT_CONTEXT)

    def parse_list(s: str | None) -> list[str] | None:
        if s is None:
            return None
        return [item.strip() for item in s.split(",") if item.strip()]

    service = MissionService(repo_root, spine_root=spine_root)
    try:
        result = service.refine(
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
    except MissionNotFoundError as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(EXIT_CONTEXT)
    except MissionValidationError as exc:
        console.print(f"[bold red]Validation error:[/bold red] {exc}")
        raise typer.Exit(EXIT_VALIDATION)

    try:
        rel_path = result.draft_path.relative_to(repo_root).as_posix()
    except ValueError:
        rel_path = str(result.draft_path)

    console.print(f"[bold green]Mission draft created[/bold green] (non-canonical)")
    console.print(f"  Draft ID:   [yellow]{result.draft_id}[/yellow]")
    console.print(f"  Draft file: {rel_path}")
    console.print(f"  Title:      {result.mission.title}")
    console.print()
    console.print("[dim]This draft does not affect canonical mission state.[/dim]")
    console.print("[dim]Review it, then promote with:[/dim]")
    console.print(f"  spine mission confirm {result.draft_id}")


@mission_app.command("confirm", help="Promote a mission draft to canonical mission.yaml.")
def mission_confirm(
    draft_id: str = typer.Argument(..., help="Mission draft ID to promote (from 'spine mission drafts')"),
    cwd: Path | None = typer.Option(
        None,
        "--cwd",
        help="Target repository path. Overrides SPINE_ROOT. Precedence: --cwd > SPINE_ROOT > cwd.",
    ),
) -> None:
    """
    Promote a mission draft to canonical .spine/mission.yaml.

    Reads the draft from .spine/drafts/missions/<draft_id>.yaml,
    validates it, writes it to .spine/mission.yaml, then removes the draft.

    This is an explicit operator action. Promotion is never silent or automatic.

    Exit codes:
      0  Promoted successfully
      1  Draft not found or malformed
      2  Context failure — repo not found
    """
    try:
        repo_root, spine_root = resolve_roots(cwd)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(EXIT_CONTEXT)

    service = MissionService(repo_root, spine_root=spine_root)
    try:
        mission = service.confirm_draft(draft_id)
    except MissionDraftNotFoundError as exc:
        console.print(f"[bold red]Mission draft not found:[/bold red] {exc}")
        raise typer.Exit(EXIT_VALIDATION)
    except MissionValidationError as exc:
        console.print(f"[bold red]Validation error:[/bold red] {exc}")
        raise typer.Exit(EXIT_VALIDATION)

    console.print(f"[bold green]Mission draft confirmed:[/bold green] {mission.title}")
    console.print(f"  Status:     {mission.status}")
    console.print(f"  Updated at: {mission.updated_at}")
    console.print(f"  Promoted from draft: {draft_id}")
    console.print(f"  Canonical: .spine/mission.yaml")


@mission_app.command("drafts", help="List pending mission drafts in .spine/drafts/missions/.")
def mission_drafts_list(
    cwd: Path | None = typer.Option(
        None,
        "--cwd",
        help="Target repository path. Overrides SPINE_ROOT. Precedence: --cwd > SPINE_ROOT > cwd.",
    ),
) -> None:
    """
    List pending mission drafts under .spine/drafts/missions/.

    Mission drafts are non-canonical. Use 'spine mission confirm <draft_id>'
    to promote a draft to canonical mission.yaml.

    Exit codes:
      0  Success (even if no drafts)
      2  Context failure — repo not found
    """
    try:
        repo_root, spine_root = resolve_roots(cwd)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(EXIT_CONTEXT)

    service = MissionService(repo_root, spine_root=spine_root)
    drafts = service.list_mission_drafts()

    if not drafts:
        console.print("[dim]No pending mission drafts.[/dim]")
        return

    console.print(f"[bold]Pending mission drafts ({len(drafts)}):[/bold]")
    for entry in drafts:
        draft_id = entry["draft_id"]
        title = entry["title"]
        status = entry["status"]
        console.print(f"  [yellow]{draft_id}[/yellow]  [{status}] {title}")
        console.print(f"    Promote with: spine mission confirm {draft_id}")
