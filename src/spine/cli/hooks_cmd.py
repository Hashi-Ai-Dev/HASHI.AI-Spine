"""spine hooks — local, explicit, opt-in git hook management (Issue #34)."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from spine.cli.app import app, resolve_roots, EXIT_OK, EXIT_VALIDATION, EXIT_CONTEXT
from spine.services.hooks_service import HooksService, SUPPORTED_HOOKS, DEFAULT_HOOK_NAME

console = Console()

# ---------------------------------------------------------------------------
# Hooks command group
# ---------------------------------------------------------------------------

hooks_app = typer.Typer(
    help=(
        "Manage local SPINE git hooks (opt-in).\n\n"
        "Hooks are installed into .git/hooks/ and are local-only — "
        "they are never committed and are fully visible and removable by the operator.\n\n"
        "The installed hook runs 'spine check before-pr' before each push.\n\n"
        "Commands:\n"
        "  install    Install a SPINE hook into .git/hooks/\n"
        "  list       List installed SPINE hooks\n"
        "  uninstall  Remove an installed SPINE hook"
    )
)
app.add_typer(hooks_app, name="hooks", help="Manage local SPINE git hooks (opt-in).")


# ---------------------------------------------------------------------------
# install
# ---------------------------------------------------------------------------


@hooks_app.command(
    "install",
    help=(
        "Install a SPINE hook into .git/hooks/.\n\n"
        "The hook runs 'spine check before-pr' before each git push.\n\n"
        "SPINE will not overwrite a pre-existing non-SPINE hook. Remove or "
        "rename the existing hook first if you want SPINE to manage it.\n\n"
        "Hook types supported: pre-push (default)\n\n"
        "Exit codes:\n"
        "  0  Hook installed or updated successfully\n"
        "  1  Install refused (conflicting hook or unsupported type)\n"
        "  2  Context failure (no git repo)"
    ),
)
def hooks_install(
    hook: str = typer.Option(
        DEFAULT_HOOK_NAME,
        "--hook",
        help=f"Git hook name to install into. Supported: {', '.join(SUPPORTED_HOOKS)}",
    ),
    ignore_failure: bool = typer.Option(
        False,
        "--ignore-failure",
        help=(
            "Install hook in non-blocking mode: the hook always exits 0, "
            "even when 'spine check before-pr' reports issues. "
            "The checkpoint result is still printed — only the exit code is suppressed."
        ),
    ),
    cwd: Path | None = typer.Option(
        None,
        "--cwd",
        help="Target repository path. Overrides SPINE_ROOT.",
    ),
) -> None:
    """Install a SPINE-managed hook into .git/hooks/."""
    try:
        repo_root, _spine_root = resolve_roots(cwd)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(EXIT_CONTEXT)

    service = HooksService(repo_root)
    result = service.install(hook_name=hook, ignore_failure=ignore_failure)

    if result.ok:
        console.print(f"[bold green]OK[/bold green]  {result.message}")
        raise typer.Exit(EXIT_OK)
    else:
        console.print(f"[bold red]Error:[/bold red] {result.message}")
        raise typer.Exit(EXIT_VALIDATION)


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------


@hooks_app.command(
    "list",
    help=(
        "List SPINE-managed hooks installed in .git/hooks/.\n\n"
        "Only shows hooks that were installed by 'spine hooks install'.\n\n"
        "Exit codes:\n"
        "  0  Always (even if no hooks are installed)"
    ),
)
def hooks_list(
    cwd: Path | None = typer.Option(
        None,
        "--cwd",
        help="Target repository path. Overrides SPINE_ROOT.",
    ),
) -> None:
    """List installed SPINE-managed hooks."""
    try:
        repo_root, _spine_root = resolve_roots(cwd)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(EXIT_CONTEXT)

    service = HooksService(repo_root)
    result = service.list_hooks()

    if not result.any_installed:
        console.print("[dim]No SPINE hooks installed.[/dim]")
        console.print("[dim]Run 'spine hooks install' to add one.[/dim]")
        raise typer.Exit(EXIT_OK)

    table = Table(title="SPINE hooks", box=None, show_header=True)
    table.add_column("Hook", style="bold")
    table.add_column("Mode")
    table.add_column("Path")

    for hook in result.hooks:
        mode = "non-blocking (--ignore-failure)" if hook.ignore_failure else "blocking"
        table.add_row(hook.hook_name, mode, str(hook.hook_path))

    console.print(table)
    raise typer.Exit(EXIT_OK)


# ---------------------------------------------------------------------------
# uninstall
# ---------------------------------------------------------------------------


@hooks_app.command(
    "uninstall",
    help=(
        "Remove a SPINE-managed hook from .git/hooks/.\n\n"
        "Only removes hooks that were installed by 'spine hooks install'. "
        "SPINE will not remove third-party hooks.\n\n"
        "Exit codes:\n"
        "  0  Hook removed successfully\n"
        "  1  Removal refused (not a SPINE hook, or hook not found)\n"
        "  2  Context failure (no git repo)"
    ),
)
def hooks_uninstall(
    hook: str = typer.Option(
        DEFAULT_HOOK_NAME,
        "--hook",
        help=f"Git hook name to remove. Supported: {', '.join(SUPPORTED_HOOKS)}",
    ),
    cwd: Path | None = typer.Option(
        None,
        "--cwd",
        help="Target repository path. Overrides SPINE_ROOT.",
    ),
) -> None:
    """Remove a SPINE-managed hook from .git/hooks/."""
    try:
        repo_root, _spine_root = resolve_roots(cwd)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(EXIT_CONTEXT)

    service = HooksService(repo_root)
    result = service.uninstall(hook_name=hook)

    if result.ok:
        console.print(f"[bold green]OK[/bold green]  {result.message}")
        raise typer.Exit(EXIT_OK)
    else:
        console.print(f"[bold red]Error:[/bold red] {result.message}")
        raise typer.Exit(EXIT_VALIDATION)
