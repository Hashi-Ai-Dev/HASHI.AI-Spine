"""spine init command — CLI layer only, no business logic here."""

from __future__ import annotations

from pathlib import Path

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from spine.cli.app import app, err_console
from spine.services.init_service import ConflictError, InitService
from spine.utils.paths import GitRepoNotFoundError

console = Console()

_EXIT_GIT_NOT_FOUND = 2
_EXIT_CONFLICT = 3


@app.command("init")
def init_cmd(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing files.",
    ),
    allow_no_git: bool = typer.Option(
        False,
        "--allow-no-git",
        help="Allow init in directories that are not git repositories.",
    ),
    cwd: Path = typer.Option(
        None,
        "--cwd",
        help="Target repository path. Overrides SPINE_ROOT. Precedence: --cwd > SPINE_ROOT > cwd.",
        hidden=True,
    ),
) -> None:
    """
    Scaffold [bold].spine/[/bold] governance state in the current git repository.

    Creates mission.yaml, constraints.yaml, JSONL append-logs, agent guidance
    files (AGENTS.md, CLAUDE.md), and AI tool configuration files.

    Safe by default: existing files are never overwritten unless [bold]--force[/bold] is passed.
    """
    effective_cwd = cwd or Path.cwd()

    service = InitService(
        force=force,
        allow_no_git=allow_no_git,
        cwd=effective_cwd,
        explicit_cwd=cwd is not None,
    )

    try:
        result = service.run()
    except GitRepoNotFoundError as exc:
        err_console.print(
            f"[bold red]Error:[/bold red] {exc}\n"
            "Run inside a git repository, or pass [bold]--allow-no-git[/bold]."
        )
        raise typer.Exit(_EXIT_GIT_NOT_FOUND) from None
    except ConflictError as exc:
        err_console.print("[bold red]Error:[/bold red] The following files already exist:")
        for conflict in exc.conflicts:
            err_console.print(f"  [yellow]{conflict}[/yellow]")
        err_console.print(
            "\nPass [bold]--force[/bold] to overwrite, "
            "or remove conflicting files manually."
        )
        raise typer.Exit(_EXIT_CONFLICT) from None

    repo_root = result.repo_root
    assert repo_root is not None

    if result.created:
        table = Table(box=box.SIMPLE, show_header=True, header_style="bold green")
        table.add_column("Created")
        for f in result.created:
            table.add_row(f)
        console.print(table)

    if result.skipped:
        skip_table = Table(box=box.SIMPLE, show_header=True, header_style="bold dim")
        skip_table.add_column("Skipped (already exists)", style="dim")
        for f in result.skipped:
            skip_table.add_row(f)
        console.print(skip_table)

    console.print(
        Panel(
            "[bold green]spine init complete[/bold green]\n\n"
            "Next steps:\n"
            "  1. Edit [bold].spine/mission.yaml[/bold] — define your active mission\n"
            "  2. Edit [bold].spine/constraints.yaml[/bold] — configure work schedule and limits\n"
            "  3. Commit [bold].spine/[/bold] to version-control your governance state\n"
            "  4. Run [bold]uv run pytest[/bold] to verify everything is wired correctly",
            title="[bold]SPINE Phase 1[/bold]",
            border_style="green",
        )
    )
