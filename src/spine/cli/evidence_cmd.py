"""spine evidence add command — spec-compliant nesting."""

from __future__ import annotations

import typer
from rich.console import Console

from spine.cli.app import app, resolve_roots
from spine.models.evidence import EVIDENCE_KINDS
from spine.services.evidence_service import EvidenceService, EvidenceValidationError

console = Console()

# ---------------------------------------------------------------------------
# Evidence command group (spine evidence <action>)
# ---------------------------------------------------------------------------
evidence_app = typer.Typer()
app.add_typer(evidence_app, name="evidence", help="Manage evidence records.")


@evidence_app.command("add", help="Add an evidence record to .spine/evidence.jsonl.")
def evidence_add(
    kind: EVIDENCE_KINDS = typer.Option(..., "--kind", "-k", help="Evidence kind"),
    description: str = typer.Option("", "--description", "-d", help="Description of the evidence"),
    url: str = typer.Option("", "--url", help="URL or reference for the evidence"),
) -> None:
    """
    Add an evidence record to .spine/evidence.jsonl.

    Allowed kinds: brief_generated, commit, pr, test_pass, review_done,
                   demo, user_feedback, payment, kill, narrow
    """
    try:
        repo_root, spine_root = resolve_roots()
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(1)

    service = EvidenceService(repo_root, spine_root=spine_root)
    try:
        evidence = service.add(kind=kind, description=description, evidence_url=url)
        console.print(f"[bold green]Evidence added:[/bold green] [{evidence.kind}] {evidence.description or '(no description)'}")
        console.print(f"  Created at: {evidence.created_at}")
    except EvidenceValidationError as exc:
        console.print(f"[bold red]Validation error:[/bold red] {exc}")
        raise typer.Exit(1)
