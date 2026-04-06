"""spine drift scan command — spec-compliant nesting."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from spine.cli.app import app, resolve_roots
from spine.services.drift_service import DriftService

console = Console()
err_console = Console(stderr=True)

# ---------------------------------------------------------------------------
# Drift command group (spine drift <action>)
# ---------------------------------------------------------------------------
drift_app = typer.Typer()
app.add_typer(drift_app, name="drift", help="Detect and log scope drift.")


@drift_app.command("scan", help="Scan for git-native scope drift.")
def drift_scan(
    against_branch: str | None = typer.Option(
        None,
        "--against",
        "-b",
        help="Branch to diff against (default: uncommitted changes)",
    ),
) -> None:
    """
    Scan for git-native scope drift.

    Uses git status and git diff to detect:
    - Forbidden expansions (UI, auth, billing)
    - Scope sprawl (new top-level modules)
    - Dependency bloat
    - Service additions without tests

    Appends detected drift events to .spine/drift.jsonl.
    """
    try:
        repo_root, spine_root = resolve_roots()
    except Exception as exc:
        err_console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(1)

    service = DriftService(repo_root, spine_root=spine_root)
    result = service.scan(against_branch=against_branch)

    if not result.events:
        console.print("[bold green]No drift detected.[/bold green]")
        return

    summary = result.severity_summary
    console.print("[bold]Drift scan results:[/bold]")
    if summary["high"] > 0:
        console.print(f"  [bold red]HIGH:[/bold red] {summary['high']}")
    if summary["medium"] > 0:
        console.print(f"  [bold yellow]MEDIUM:[/bold yellow] {summary['medium']}")
    if summary["low"] > 0:
        console.print(f"  [bold dim]LOW:[/bold dim] {summary['low']}")

    table = Table(title="Drift Events", box=None)
    table.add_column("Severity", style="bold")
    table.add_column("Category")
    table.add_column("Description")
    table.add_column("File", style="dim")

    for event in result.events:
        severity_style = {
            "high": "bold red",
            "medium": "bold yellow",
            "low": "dim",
        }.get(event.severity, "")
        table.add_row(
            f"[{severity_style}]{event.severity.upper()}[/{severity_style}]",
            event.category,
            event.description[:60],
            event.file_path,
        )

    console.print(table)
    console.print(f"\n[dim]{len(result.events)} drift event(s) appended to .spine/drift.jsonl[/dim]")
