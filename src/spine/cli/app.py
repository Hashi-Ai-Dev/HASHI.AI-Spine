"""Top-level Typer application factory."""

from __future__ import annotations

import os
from pathlib import Path

import typer
from rich.console import Console

console = Console()
err_console = Console(stderr=True)


def resolve_roots(cwd: Path | None = None) -> tuple[Path, Path]:
    """
    Resolve the git repository root and SPINE project root.

    Git root is found by walking up from cwd using find_git_root().
    SPINE root is determined by:
    - SPINE_ROOT env var (for subdirectory SPINE governance), else
    - git root (standard layout where .spine/ lives at repo root)

    When SPINE_ROOT is set, it is treated as the authoritative target repo
    root — both git operations and .spine/ state point to the same repo.

    Returns (git_root, spine_root).
    """
    from spine.utils.paths import find_git_root
    if os.environ.get("SPINE_ROOT"):
        # SPINE_ROOT is the authoritative repo root for both git and state.
        # Use it directly as git_root (no walking up from cwd).
        repo_root = Path(os.environ["SPINE_ROOT"]).resolve()
        return repo_root, repo_root / ".spine"
    # Normal case: walk up from cwd to find git root, .spine/ lives at it.
    git_root = find_git_root(cwd or Path.cwd())
    return git_root, git_root / ".spine"

app = typer.Typer(
    name="spine",
    help=(
        "SPINE — local-first, repo-native mission governor.\n\n"
        "Run [bold]spine init[/bold] to scaffold .spine/ governance state.\n"
        "Run [bold]spine --help[/bold] to see all commands."
    ),
    rich_markup_mode="rich",
    no_args_is_help=True,
    add_completion=False,
    invoke_without_command=True,
)


@app.callback()
def _root(ctx: typer.Context) -> None:
    """SPINE — local-first, repo-native mission governor."""
    # Callback exists to prevent Typer 0.24 from flattening the single
    # subcommand into the top-level app. Without it, `spine init` would
    # fail because Typer promotes the sole command to the root and treats
    # `init` as an unexpected extra argument.
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)
