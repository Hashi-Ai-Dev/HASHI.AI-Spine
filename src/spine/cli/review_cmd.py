"""spine review weekly command — spec-compliant nesting."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from spine.cli.app import app, resolve_roots
from spine.services.review_service import ReviewService

console = Console()

RECOMMENDATION_CHOICES = ["continue", "narrow", "pivot", "kill", "ship_as_is"]

# ---------------------------------------------------------------------------
# Review command group (spine review <action>)
# ---------------------------------------------------------------------------
review_app = typer.Typer()
app.add_typer(review_app, name="review", help="Generate review documents.")


@review_app.command("weekly", help="Generate a weekly review document.")
def review_weekly(
    cwd: Path = typer.Option(
        None,
        "--cwd",
        help="Override working directory (for testing).",
        hidden=True,
    ),
    days: int = typer.Option(7, "--days", "-d", help="Number of days to aggregate"),
    recommendation: str = typer.Option(
        "continue",
        "--recommendation",
        "-r",
        help=f"Recommendation: {RECOMMENDATION_CHOICES}",
    ),
    notes: str = typer.Option("", "--notes", "-n", help="Additional notes for the review"),
) -> None:
    """
    Generate a weekly review document.

    Aggregates last N days of evidence, decisions, drift, and mission state.
    Writes markdown to .spine/reviews/YYYY-MM-DD.md.
    Also updates .spine/reviews/latest.md.

    Allowed recommendations: continue, narrow, pivot, kill, ship_as_is
    """
    if recommendation not in RECOMMENDATION_CHOICES:
        console.print(
            f"[bold red]Error:[/bold red] recommendation must be one of: {RECOMMENDATION_CHOICES}"
        )
        raise typer.Exit(1)

    effective_cwd = cwd or Path.cwd()
    try:
        repo_root, spine_root = resolve_roots(effective_cwd)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(1)

    service = ReviewService(repo_root, spine_root=spine_root)
    path = service.generate_weekly(
        days=days,
        recommendation=recommendation,  # type: ignore[arg-type]
        notes=notes,
    )
    console.print(f"[bold green]Weekly review generated:[/bold green] {path}")
