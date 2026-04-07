"""spine doctor command."""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

import typer
from rich.console import Console
from rich.table import Table

from spine.cli.app import app, resolve_roots
from spine.services.doctor_service import DoctorService
from spine.utils.paths import get_current_branch, get_default_branch, format_context_line

console = Console()


@app.command("doctor")
def doctor_cmd(
    cwd: Path | None = typer.Option(
        None,
        "--cwd",
        help="Target repository path. Overrides SPINE_ROOT. Precedence: --cwd > SPINE_ROOT > cwd.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON (machine-readable).",
    ),
) -> None:
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
        repo_root, spine_root = resolve_roots(cwd)
    except Exception as exc:
        if json_output:
            print(json.dumps({"error": str(exc)}, indent=2))
        else:
            console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(1)

    branch = get_current_branch(repo_root)
    default_branch = get_default_branch(repo_root)
    service = DoctorService(repo_root, spine_root=spine_root)
    result = service.check()

    if json_output:
        data = {
            "passed": result.passed,
            "repo": str(repo_root),
            "branch": branch,
            "default_branch": default_branch,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "error_count": sum(1 for i in result.issues if i.severity == "error"),
            "warning_count": sum(1 for i in result.issues if i.severity == "warning"),
            "issues": [
                {"severity": i.severity, "file": i.file, "message": i.message}
                for i in result.issues
            ],
        }
        print(json.dumps(data, indent=2))
        if not result.passed:
            raise typer.Exit(1)
        return

    # Human-readable output
    context_line = format_context_line(repo_root, branch, default_branch)
    console.print(f"[dim]{context_line}[/dim]")
    if default_branch is None:
        console.print(
            "[bold yellow]Warning:[/bold yellow] [dim]default branch unresolved — "
            "no remote origin/HEAD, no main/master found[/dim]"
        )

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
