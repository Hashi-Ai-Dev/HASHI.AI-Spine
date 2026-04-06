"""spine doctor command."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from spine.cli.app import app, resolve_roots
from spine.services.doctor_service import DoctorService

console = Console()


@app.command("doctor")
def doctor_cmd() -> None:
    """
    Validate .spine/ state and repo contract.

    Checks:
    - Required repo contract files exist (AGENTS.md, CLAUDE.md, etc.)
    - .spine/ directory exists
    - mission.yaml parses and conforms
    - constraints.yaml parses and conforms
    - JSONL files parse cleanly
    - Required subdirectories exist
    """
    try:
        repo_root, spine_root = resolve_roots()
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(1)

    service = DoctorService(repo_root, spine_root=spine_root)
    result = service.check()

    if result.passed and not result.issues:
        console.print("[bold green]All checks passed.[/bold green]")
        console.print("SPINE state is valid and compliant.")
        return

    if result.issues:
        table = Table(title="Doctor Issues", box=None)
        table.add_column("Severity", style="bold")
        table.add_column("File")
        table.add_column("Message")

        for issue in result.issues:
            style = "bold red" if issue.severity == "error" else "bold yellow"
            table.add_row(
                f"[{style}]{issue.severity.upper()}[/{style}]",
                issue.file,
                issue.message,
            )
        console.print(table)

    if not result.passed:
        console.print("\n[bold red]Doctor check FAILED.[/bold red]")
        console.print("Fix the errors above before continuing.")
        raise typer.Exit(1)
    else:
        console.print("\n[bold yellow]Doctor check passed with warnings.[/bold yellow]")
