"""spine decision add command — spec-compliant nesting."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from spine.cli.app import app, resolve_roots, EXIT_VALIDATION, EXIT_CONTEXT
from spine.services.decision_service import DecisionService, DecisionValidationError

console = Console()

# ---------------------------------------------------------------------------
# Decision command group (spine decision <action>)
# ---------------------------------------------------------------------------
decision_app = typer.Typer()
app.add_typer(decision_app, name="decision", help="Manage decision records.")


@decision_app.command("add", help="Add a decision record to .spine/decisions.jsonl.")
def decision_add(
    cwd: Path | None = typer.Option(
        None,
        "--cwd",
        help="Target repository path. Overrides SPINE_ROOT. Precedence: --cwd > SPINE_ROOT > cwd.",
    ),
    title: str = typer.Option(..., "--title", "-t", help="Decision title (required)"),
    why: str = typer.Option(..., "--why", "-w", help="Why this decision was made (required)"),
    decision: str = typer.Option(..., "--decision", "-d", help="What was decided (required)"),
    alternatives: str | None = typer.Option(None, "--alternatives", help="Comma-separated alternative options considered"),
) -> None:
    """
    Add a decision record to .spine/decisions.jsonl.

    Requires: title, why, decision. All are required.
    Optional: alternatives (comma-separated list).
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

    service = DecisionService(repo_root, spine_root=spine_root)
    try:
        decision_record = service.add(
            title=title,
            why=why,
            decision=decision,
            alternatives=parse_list(alternatives),
        )
        console.print(f"[bold green]Decision added:[/bold green] {decision_record.title}")
        console.print(f"  Why: {decision_record.why}")
        console.print(f"  Decision: {decision_record.decision}")
        if decision_record.alternatives:
            console.print(f"  Alternatives: {', '.join(decision_record.alternatives)}")
        console.print(f"  Created at: {decision_record.created_at}")
    except DecisionValidationError as exc:
        console.print(f"[bold red]Validation error:[/bold red] {exc}")
        raise typer.Exit(EXIT_VALIDATION)
