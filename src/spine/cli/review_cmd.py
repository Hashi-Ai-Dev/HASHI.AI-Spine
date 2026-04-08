"""spine review commands — weekly review and handoff summary."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from spine.cli.app import app, resolve_roots, EXIT_VALIDATION, EXIT_CONTEXT
from spine.services.review_service import ReviewService
from spine.services.handoff_service import HandoffService
from spine.utils.paths import get_current_branch, get_default_branch, format_context_line

console = Console()

RECOMMENDATION_CHOICES = ["continue", "narrow", "pivot", "kill", "ship_as_is"]

# ---------------------------------------------------------------------------
# Review command group (spine review <action>)
# ---------------------------------------------------------------------------
review_app = typer.Typer()
app.add_typer(review_app, name="review", help="Generate review documents.")


@review_app.command("weekly", help="Generate a weekly review document.")
def review_weekly(
    cwd: Path | None = typer.Option(
        None,
        "--cwd",
        help="Target repository path. Overrides SPINE_ROOT. Precedence: --cwd > SPINE_ROOT > cwd.",
    ),
    days: int = typer.Option(7, "--days", "-d", help="Number of days to aggregate"),
    recommendation: str = typer.Option(
        "continue",
        "--recommendation",
        "-r",
        help=f"Recommendation: {RECOMMENDATION_CHOICES}",
    ),
    notes: str = typer.Option("", "--notes", "-n", help="Additional notes for the review"),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output a structured JSON summary instead of prose (artifact still written).",
    ),
) -> None:
    """
    Generate a weekly review document.

    Aggregates last N days of evidence, decisions, drift, and mission state.
    Writes markdown to .spine/reviews/YYYY-MM-DD.md.
    Also updates .spine/reviews/latest.md.

    Allowed recommendations: continue, narrow, pivot, kill, ship_as_is

    With --json: prints a structured summary to stdout; the markdown artifact
    is still written as normal.
    """
    if recommendation not in RECOMMENDATION_CHOICES:
        if json_output:
            print(json.dumps({
                "error": f"recommendation must be one of: {RECOMMENDATION_CHOICES}",
                "exit_code": EXIT_VALIDATION,
            }))
        else:
            console.print(
                f"[bold red]Error:[/bold red] recommendation must be one of: {RECOMMENDATION_CHOICES}"
            )
        raise typer.Exit(EXIT_VALIDATION)

    try:
        repo_root, spine_root = resolve_roots(cwd)
    except Exception as exc:
        if json_output:
            print(json.dumps({"error": str(exc), "exit_code": EXIT_CONTEXT}))
        else:
            console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(EXIT_CONTEXT)

    branch = get_current_branch(repo_root)
    default_branch = get_default_branch(repo_root)
    context_line = format_context_line(repo_root, branch, default_branch)

    service = ReviewService(repo_root, spine_root=spine_root)
    result = service.generate_weekly(
        days=days,
        recommendation=recommendation,  # type: ignore[arg-type]
        notes=notes,
    )

    if json_output:
        data = {
            "canonical_path": str(result.canonical),
            "latest_path": str(result.latest),
            "recommendation": result.recommendation,
            "period_days": result.period_days,
            "mission_title": result.mission_title,
            "mission_status": result.mission_status,
            "evidence_count": result.evidence_count,
            "decisions_count": result.decisions_count,
            "drift_count": result.drift_count,
            "generated_at": result.generated_at,
        }
        print(json.dumps(data, indent=2))
        return

    console.print(f"[dim]{context_line}[/dim]")
    console.print(f"[bold green]Weekly review generated:[/bold green] {result.canonical}")
    console.print(f"[dim]Latest alias updated:[/dim]   {result.latest}")


@review_app.command(
    "handoff",
    help=(
        "Generate a compact governance handoff summary.\n\n"
        "Reads local .spine/ state only — no network calls, no model calls.\n\n"
        "Includes:\n"
        "  - mission summary\n"
        "  - recent decisions (last N days)\n"
        "  - recent evidence (last N days)\n"
        "  - current drift state\n\n"
        "Useful before PRs, between agent sessions, or when returning to a repo.\n\n"
        "Exit codes:\n"
        "  0  Summary generated successfully\n"
        "  2  Context failure — repo not found or .spine/ missing"
    ),
)
def review_handoff(
    cwd: Path | None = typer.Option(
        None,
        "--cwd",
        help="Target repository path. Overrides SPINE_ROOT. Precedence: --cwd > SPINE_ROOT > cwd.",
    ),
    days: int = typer.Option(7, "--days", "-d", help="Number of days for recent activity window"),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output a structured JSON summary instead of prose.",
    ),
) -> None:
    """
    Generate a compact governance handoff summary.

    Reads local .spine/ state only.
    No network calls. No model calls. No state mutation.

    Outputs a human-readable governance snapshot to stdout:
      - mission state
      - recent decisions and evidence
      - drift state

    Exit codes:
      0  Summary generated
      2  Context failure — cannot resolve repo or .spine/ root
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

    service = HandoffService(repo_root, spine_root=spine_root)
    result = service.generate(branch=branch, days=days)

    if json_output:
        data = {
            "repo": result.repo,
            "branch": result.branch,
            "period_days": result.period_days,
            "generated_at": result.generated_at,
            "mission": {
                "title": result.mission_title,
                "status": result.mission_status,
                "promise": result.mission_promise,
                "metric": result.mission_metric,
            },
            "recent_decisions": result.recent_decisions,
            "recent_evidence": result.recent_evidence,
            "drift_records": result.drift_records,
            "totals": {
                "decisions": result.total_decisions,
                "evidence": result.total_evidence,
                "drift": result.total_drift,
            },
        }
        print(json.dumps(data, indent=2))
        return

    context_line = format_context_line(repo_root, branch, default_branch)
    console.print(f"[dim]{context_line}[/dim]")
    console.print()
    console.print(service.format_summary(result))
