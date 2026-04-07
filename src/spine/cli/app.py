"""Top-level Typer application factory."""

from __future__ import annotations

import os
from pathlib import Path

import typer
from rich.console import Console

console = Console()
err_console = Console(stderr=True)

# ---------------------------------------------------------------------------
# Stable exit codes — contract for all SPINE commands
# ---------------------------------------------------------------------------
EXIT_OK = 0          # Success
EXIT_VALIDATION = 1  # Validation failure: invalid input, bad enum, malformed state
EXIT_CONTEXT = 2     # Context failure: no git repo, missing .spine/, missing state


def resolve_roots(cwd: Path | None = None) -> tuple[Path, Path]:
    """
    Resolve the git repository root and SPINE project root.

    Target resolution precedence (highest to lowest):
    1. ``--cwd <path>``  — if explicitly provided, overrides SPINE_ROOT
    2. ``SPINE_ROOT``    — environment variable, if set
    3. current working directory — fallback default

    Commands that require a git repo fail fast with a clear message when the
    resolved target is not a git repository.  Errors always state:
    - the resolved target path
    - which source produced it (--cwd, SPINE_ROOT, or cwd)
    - what the operator should do to fix it

    Returns (git_root, spine_root).
    """
    from spine.utils.paths import find_git_root, GitRepoNotFoundError

    if cwd is not None:
        # --cwd explicitly provided: highest precedence, overrides SPINE_ROOT.
        target = cwd.resolve()
        source = f"--cwd {cwd}"
        try:
            git_root = find_git_root(target)
        except GitRepoNotFoundError:
            raise GitRepoNotFoundError(
                f"No git repository found at or above: {target}\n"
                f"  Target source: {source}\n"
                f"  Point --cwd at a valid git repository, or run 'git init' first."
            ) from None
        return git_root, git_root / ".spine"

    spine_root_env = os.environ.get("SPINE_ROOT")
    if spine_root_env:
        # SPINE_ROOT is the authoritative repo root for both git and state.
        # No --cwd was supplied, so SPINE_ROOT governs.
        repo_root = Path(spine_root_env).resolve()
        if not repo_root.exists():
            raise FileNotFoundError(
                f"SPINE_ROOT path does not exist: {repo_root}\n"
                f"  SPINE_ROOT={spine_root_env}\n"
                f"  Update SPINE_ROOT to point to a valid repository path."
            )
        return repo_root, repo_root / ".spine"

    # Default: walk up from the current working directory.
    cwd_resolved = Path.cwd()
    try:
        git_root = find_git_root(cwd_resolved)
    except GitRepoNotFoundError:
        raise GitRepoNotFoundError(
            f"No git repository found at or above: {cwd_resolved}\n"
            f"  Target source: current working directory\n"
            f"  Use '--cwd <path>' to target a specific repo, or set SPINE_ROOT, "
            f"or run 'git init'."
        ) from None
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
