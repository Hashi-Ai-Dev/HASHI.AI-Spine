"""spine opportunity score command — spec-compliant nesting."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from spine.cli.app import app, resolve_roots, EXIT_VALIDATION, EXIT_CONTEXT
from spine.services.opportunity_service import OpportunityService, OpportunityValidationError

console = Console()

# ---------------------------------------------------------------------------
# Opportunity command group (spine opportunity <action>)
# ---------------------------------------------------------------------------
opportunity_app = typer.Typer()
app.add_typer(opportunity_app, name="opportunity", help="Score and log opportunities.")


@opportunity_app.command("score", help="Score an opportunity using deterministic weighted factors.")
def opportunity_score(
    title: str = typer.Argument(..., help="Opportunity title"),
    cwd: Path | None = typer.Option(
        None,
        "--cwd",
        help="Target repository path. Overrides SPINE_ROOT. Precedence: --cwd > SPINE_ROOT > cwd.",
    ),
    description: str = typer.Option("", "--description", "-d", help="Description of the opportunity"),
    pain: int = typer.Option(3, "--pain", help="Pain score 1-5"),
    founder_fit: int = typer.Option(3, "--founder-fit", help="Founder fit score 1-5"),
    time_to_proof: int = typer.Option(3, "--time-to-proof", help="Time to proof 1-5 (1=fastest)"),
    monetization: int = typer.Option(3, "--monetization", help="Monetization potential 1-5"),
    sprawl_risk: int = typer.Option(3, "--sprawl-risk", help="Sprawl risk 1-5 (1=risky)"),
    maintenance: int = typer.Option(3, "--maintenance", help="Maintenance burden 1-5 (1=heavy)"),
) -> None:
    """
    Score an opportunity using deterministic weighted factors.

    Scores: pain, founder_fit, time_to_proof, monetization, sprawl_risk, maintenance.
    All scores are 1-5. Results are appended to .spine/opportunities.jsonl.
    No model call is made — all scoring is deterministic.
    """
    try:
        repo_root, spine_root = resolve_roots(cwd)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(EXIT_CONTEXT)

    service = OpportunityService(repo_root, spine_root=spine_root)
    try:
        opportunity = service.score(
            title=title,
            description=description,
            pain=pain,
            founder_fit=founder_fit,
            time_to_proof=time_to_proof,
            monetization=monetization,
            sprawl_risk=sprawl_risk,
            maintenance_burden=maintenance,
        )
        console.print(f"[bold green]Opportunity scored:[/bold green] {opportunity.title}")
        console.print(f"Total score: {opportunity.total_score}")
        console.print(f"  pain={opportunity.scores.pain}, founder_fit={opportunity.scores.founder_fit}, "
                     f"time_to_proof={opportunity.scores.time_to_proof}")
        console.print(f"  monetization={opportunity.scores.monetization}, "
                     f"sprawl_risk={opportunity.scores.sprawl_risk}, "
                     f"maintenance={opportunity.scores.maintenance_burden}")
    except OpportunityValidationError as exc:
        console.print(f"[bold red]Validation error:[/bold red] {exc}")
        raise typer.Exit(EXIT_VALIDATION)
