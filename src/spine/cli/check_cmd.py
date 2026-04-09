"""spine check before-pr — preflight checkpoint command."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from spine.cli.app import app, resolve_roots, EXIT_OK, EXIT_VALIDATION, EXIT_CONTEXT
from spine.services.check_service import CheckService, BeforePrResult, BeforeWorkResult
from spine.utils.paths import get_current_branch, get_default_branch, format_context_line

console = Console()

# ---------------------------------------------------------------------------
# Check command group (spine check <action>)
# ---------------------------------------------------------------------------

check_app = typer.Typer(help="Preflight governance checkpoints.")
app.add_typer(check_app, name="check", help="Preflight governance checkpoints.")


@check_app.command(
    "before-pr",
    help=(
        "Run a preflight governance checkpoint before opening a PR.\n\n"
        "Checks:\n"
        "  - .spine/ directory present\n"
        "  - mission.yaml present and readable\n"
        "  - repo health (doctor-style: no errors)\n"
        "  - open drift in drift.jsonl\n"
        "  - evidence presence\n"
        "  - decision presence\n\n"
        "Exit codes:\n"
        "  0  All checks passed — clear to proceed\n"
        "  1  Review recommended — one or more checks need attention\n"
        "  2  Context failure   — cannot resolve repo or .spine/ root"
    ),
)
def check_before_pr(
    cwd: Path | None = typer.Option(
        None,
        "--cwd",
        help="Target repository path. Overrides SPINE_ROOT. Precedence: --cwd > SPINE_ROOT > cwd.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON (machine-readable). Exit codes still apply.",
    ),
) -> None:
    """
    Run a preflight governance checkpoint before opening a PR.

    Evaluates mission, repo health, drift status, evidence, and decisions.
    Reports what passed and what needs review. Does NOT mutate state.

    Exit codes:
      0  All checks passed
      1  Review recommended — one or more checks need attention
      2  Context failure   — cannot resolve repo or .spine/ root
    """
    try:
        repo_root, spine_root = resolve_roots(cwd)
    except Exception as exc:
        if json_output:
            print(json.dumps({"error": str(exc), "exit_code": EXIT_CONTEXT}, indent=2))
        else:
            console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(EXIT_CONTEXT)

    branch = get_current_branch(repo_root)
    default_branch = get_default_branch(repo_root)

    service = CheckService(repo_root, spine_root=spine_root)
    result = service.run_before_pr(branch=branch)

    if json_output:
        _output_json(result, branch, default_branch)
    else:
        _output_human(result, branch, default_branch)

    if result.passed:
        raise typer.Exit(EXIT_OK)
    else:
        raise typer.Exit(EXIT_VALIDATION)


@check_app.command(
    "before-work",
    help=(
        "Run a start-session governance checkpoint before beginning work.\n\n"
        "Checks:\n"
        "  - .spine/ directory present\n"
        "  - mission.yaml present and readable\n"
        "  - repo health (doctor-style: no errors)\n"
        "  - branch/repo context (informational)\n"
        "  - recent brief orientation context (advisory — no brief is not a blocker)\n\n"
        "Exit codes:\n"
        "  0  Clear to begin work — no hard failures (advisory warnings may appear)\n"
        "  1  Blocked — a critical check failed (missing .spine/, bad mission.yaml, doctor errors)\n"
        "  2  Context failure   — cannot resolve repo or .spine/ root"
    ),
)
def check_before_work(
    cwd: Path | None = typer.Option(
        None,
        "--cwd",
        help="Target repository path. Overrides SPINE_ROOT. Precedence: --cwd > SPINE_ROOT > cwd.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON (machine-readable). Exit codes still apply.",
    ),
) -> None:
    """
    Run a start-session governance checkpoint before beginning work.

    Evaluates mission, repo health, branch context, and brief orientation.
    Reports what passed and what needs review. Does NOT mutate state.

    Advisory warnings (e.g. no brief yet) surface guidance but do not block —
    they exit 0.  Only hard failures (missing .spine/, bad mission.yaml, doctor
    errors) produce exit 1.

    Exit codes:
      0  Clear to begin work — no hard failures
      1  Blocked — a critical check failed
      2  Context failure   — cannot resolve repo or .spine/ root
    """
    try:
        repo_root, spine_root = resolve_roots(cwd)
    except Exception as exc:
        if json_output:
            print(json.dumps({"error": str(exc), "exit_code": EXIT_CONTEXT}, indent=2))
        else:
            console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(EXIT_CONTEXT)

    branch = get_current_branch(repo_root)
    default_branch = get_default_branch(repo_root)

    service = CheckService(repo_root, spine_root=spine_root)
    result = service.run_before_work(branch=branch)

    if json_output:
        _output_before_work_json(result, branch, default_branch)
    else:
        _output_before_work_human(result, branch, default_branch)

    if result.passed:
        raise typer.Exit(EXIT_OK)
    else:
        raise typer.Exit(EXIT_VALIDATION)


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------


def _output_json(result: BeforePrResult, branch: str, default_branch: str | None) -> None:
    def _serialise_item(item) -> dict:
        d: dict = {
            "name": item.name,
            "status": item.status,
            "message": item.message,
            "category": item.category,
        }
        if item.detail is not None:
            d["detail"] = item.detail
        return d

    data = {
        "result": result.result,
        "passed": result.passed,
        "repo": result.repo,
        "branch": branch,
        "default_branch": default_branch,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "checks": [_serialise_item(item) for item in result.items],
    }
    print(json.dumps(data, indent=2))


def _output_human(result: BeforePrResult, branch: str, default_branch: str | None) -> None:
    context_line = format_context_line(result.repo, branch, default_branch)
    console.print(f"[dim]{context_line}[/dim]")
    console.print()

    table = Table(title="spine check before-pr", box=None, show_header=True)
    table.add_column("Check", style="bold")
    table.add_column("Status")
    table.add_column("Detail")

    status_styles = {
        "pass": "[bold green]PASS[/bold green]",
        "warn": "[bold yellow]WARN[/bold yellow]",
        "fail": "[bold red]FAIL[/bold red]",
    }

    for item in result.items:
        status_display = status_styles.get(item.status, item.status.upper())
        table.add_row(item.name, status_display, item.message)

    console.print(table)
    console.print()

    if result.passed:
        console.print("[bold green]Result: PASS[/bold green] — all checks passed. Clear to proceed.")
    else:
        console.print(
            "[bold yellow]Result: REVIEW RECOMMENDED[/bold yellow] — "
            "one or more checks need attention before opening a PR."
        )


def _output_before_work_json(
    result: BeforeWorkResult, branch: str, default_branch: str | None
) -> None:
    data = {
        "result": result.result,
        "passed": result.passed,
        "repo": result.repo,
        "branch": branch,
        "default_branch": default_branch,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "checks": [
            {"name": item.name, "status": item.status, "message": item.message}
            for item in result.items
        ],
    }
    print(json.dumps(data, indent=2))


def _output_before_work_human(
    result: BeforeWorkResult, branch: str, default_branch: str | None
) -> None:
    context_line = format_context_line(result.repo, branch, default_branch)
    console.print(f"[dim]{context_line}[/dim]")
    console.print()

    table = Table(title="spine check before-work", box=None, show_header=True)
    table.add_column("Check", style="bold")
    table.add_column("Status")
    table.add_column("Detail")

    status_styles = {
        "pass": "[bold green]PASS[/bold green]",
        "warn": "[bold yellow]WARN[/bold yellow]",
        "fail": "[bold red]FAIL[/bold red]",
    }

    for item in result.items:
        status_display = status_styles.get(item.status, item.status.upper())
        table.add_row(item.name, status_display, item.message)

    console.print(table)
    console.print()

    if result.passed:
        console.print(
            "[bold green]Result: PASS[/bold green] — all checks passed. Clear to begin work."
        )
    else:
        console.print(
            "[bold yellow]Result: REVIEW RECOMMENDED[/bold yellow] — "
            "one or more checks need attention before starting work."
        )
