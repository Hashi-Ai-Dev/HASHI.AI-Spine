"""spine drift scan command — spec-compliant nesting."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from spine.cli.app import app, resolve_roots, EXIT_CONTEXT
from spine.services.drift_service import DriftService
from spine.utils.paths import get_current_branch, get_default_branch, format_context_line

console = Console()
err_console = Console(stderr=True)

# ---------------------------------------------------------------------------
# Drift command group (spine drift <action>)
# ---------------------------------------------------------------------------
drift_app = typer.Typer()
app.add_typer(drift_app, name="drift", help="Detect and log scope drift.")


@drift_app.command("scan", help="Scan for git-native scope drift.")
def drift_scan(
    cwd: Path | None = typer.Option(
        None,
        "--cwd",
        help="Target repository path. Overrides SPINE_ROOT. Precedence: --cwd > SPINE_ROOT > cwd.",
    ),
    against_branch: str | None = typer.Option(
        None,
        "--against",
        "-b",
        help="Branch to diff against (default: uncommitted changes)",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON (machine-readable). Exit codes still apply.",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress context line and clean-pass message. Prints nothing on no drift.",
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

    Exit codes:
      0  Scan complete (drift may or may not be present — check output)
      2  Context failure — repo not found or git unavailable
    """
    try:
        repo_root, spine_root = resolve_roots(cwd)
    except Exception as exc:
        if json_output:
            print(json.dumps({"error": str(exc), "exit_code": EXIT_CONTEXT}, indent=2))
        else:
            err_console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(EXIT_CONTEXT)

    branch = get_current_branch(repo_root)
    default_branch = get_default_branch(repo_root) if against_branch is None else None

    service = DriftService(repo_root, spine_root=spine_root)
    result = service.scan(against_branch=against_branch)

    if json_output:
        data = {
            "clean": not result.events,
            "repo": str(repo_root),
            "branch": branch,
            "default_branch": default_branch,
            "scanned_at": datetime.now(timezone.utc).isoformat(),
            "event_count": len(result.events),
            "severity_summary": result.severity_summary,
            "events": [
                {
                    "severity": e.severity,
                    "category": e.category,
                    "description": e.description,
                    "file_path": e.file_path,
                }
                for e in result.events
            ],
        }
        print(json.dumps(data, indent=2))
        return

    if not quiet:
        context_line = format_context_line(
            repo_root, branch, default_branch, compare_target=against_branch
        )
        console.print(f"[dim]{context_line}[/dim]")
        if against_branch is None and default_branch is None:
            console.print(
                "[bold yellow]Warning:[/bold yellow] [dim]default branch unresolved — "
                "no remote origin/HEAD, no main/master found; scanning working tree only[/dim]"
            )

    if not result.events:
        if not quiet:
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
