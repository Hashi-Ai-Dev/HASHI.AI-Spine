"""spine target command — show the resolved target repository.

This command addresses #73: SPINE_ROOT ergonomics for long-running shells
and multi-repo use.  It makes targeting state inspectable without running
a full governance command, and documents the one-shot SPINE_ROOT pattern
that avoids shell pollution in multi-repo workflows.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import typer
from rich.console import Console

from spine.cli.app import app, resolve_roots, EXIT_CONTEXT

console = Console()


@app.command("target")
def target_cmd(
    cwd: Path | None = typer.Option(
        None,
        "--cwd",
        help="Target repository path. Overrides SPINE_ROOT. Precedence: --cwd > SPINE_ROOT > cwd.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output as JSON (machine-readable).",
    ),
) -> None:
    """
    Show the currently resolved target repository.

    Uses the same resolution order as all other commands:

      1. [bold]--cwd <path>[/bold]   — if explicitly provided
      2. [bold]SPINE_ROOT[/bold]     — environment variable, if set
      3. [bold]current directory[/bold] — fallback default

    Use this command to verify which repo SPINE is targeting, especially
    in long-running shells or multi-repo workflows.

    [bold]Targeting tips:[/bold]

      [dim]# Set a session default — all commands in this shell target this repo:[/dim]
      export SPINE_ROOT=/path/to/repo

      [dim]# One-shot: target a specific repo for a single command only (no shell pollution):[/dim]
      SPINE_ROOT=/path/to/repo spine doctor
      SPINE_ROOT=/path/to/repo spine evidence add ...

      [dim]# Explicit per-command targeting (always works, takes highest precedence):[/dim]
      spine doctor --cwd /path/to/repo

    Exit codes:
      0  Target resolved successfully
      2  Context failure — cannot resolve target
    """
    # Determine source before calling resolve_roots so we can report it.
    if cwd is not None:
        source = f"--cwd {cwd}"
        source_key = "cwd_flag"
    elif os.environ.get("SPINE_ROOT"):
        source = f"SPINE_ROOT ({os.environ['SPINE_ROOT']})"
        source_key = "spine_root_env"
    else:
        source = "current directory"
        source_key = "current_directory"

    try:
        git_root, spine_root = resolve_roots(cwd)
    except Exception as exc:
        if json_output:
            print(json.dumps({"error": str(exc), "exit_code": EXIT_CONTEXT}, indent=2))
        else:
            console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(EXIT_CONTEXT)

    if json_output:
        print(json.dumps({
            "target": str(git_root),
            "spine_dir": str(spine_root),
            "source": source_key,
            "spine_root_env": os.environ.get("SPINE_ROOT"),
        }, indent=2))
        return

    console.print(f"  [bold]target:[/bold]  {git_root}")
    console.print(f"  [bold]source:[/bold]  {source}")
    console.print(f"  [bold].spine:[/bold]  {spine_root}")
