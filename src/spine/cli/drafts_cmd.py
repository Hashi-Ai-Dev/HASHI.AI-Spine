"""spine drafts commands — list and confirm draft governance records. [Beta]

Drafts are provisional records stored under .spine/drafts/.
They are excluded from all normal governance surfaces (review, brief, doctor scans)
until explicitly confirmed/promoted.

Usage:
  spine drafts list               — show all pending drafts
  spine drafts confirm <draft_id> — promote a draft to canonical state
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from spine.cli.app import app, resolve_roots, EXIT_VALIDATION, EXIT_CONTEXT
from spine.services.draft_service import DraftService, DraftNotFoundError, DraftError

console = Console()

# ---------------------------------------------------------------------------
# Drafts command group (spine drafts <action>)
# ---------------------------------------------------------------------------
drafts_app = typer.Typer()
app.add_typer(drafts_app, name="drafts", help="[Beta] List and confirm draft governance records.")


@drafts_app.command("list", help="List all pending draft governance records.")
def drafts_list(
    cwd: Path | None = typer.Option(
        None,
        "--cwd",
        help="Target repository path. Overrides SPINE_ROOT. Precedence: --cwd > SPINE_ROOT > cwd.",
    ),
) -> None:
    """
    List all pending draft governance records in .spine/drafts/.

    Drafts are provisional records not yet promoted to canonical state.
    Use 'spine drafts confirm <draft_id>' to promote a draft.
    """
    try:
        repo_root, spine_root = resolve_roots(cwd)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(EXIT_CONTEXT)

    service = DraftService(repo_root, spine_root=spine_root)
    drafts = service.list_drafts()

    if not drafts:
        console.print("[dim]No pending drafts.[/dim]")
        return

    console.print(f"[bold]Pending drafts ({len(drafts)}):[/bold]")
    for entry in drafts:
        draft_id = entry["draft_id"]
        record_type = entry.get("_record_type", "?")
        if record_type == "evidence":
            kind = entry.get("kind", "?")
            desc = entry.get("description", "")
            console.print(f"  [yellow]{draft_id}[/yellow]  [evidence/{kind}] {desc or '(no description)'}")
        elif record_type == "decision":
            title = entry.get("title", "?")
            console.print(f"  [yellow]{draft_id}[/yellow]  [decision] {title}")
        else:
            console.print(f"  [yellow]{draft_id}[/yellow]  [{record_type}]")
        console.print(f"    Promote with: spine drafts confirm {draft_id}")


@drafts_app.command("confirm", help="Promote a draft record to canonical state.")
def drafts_confirm(
    draft_id: str = typer.Argument(..., help="Draft ID to promote (from 'spine drafts list')"),
    cwd: Path | None = typer.Option(
        None,
        "--cwd",
        help="Target repository path. Overrides SPINE_ROOT. Precedence: --cwd > SPINE_ROOT > cwd.",
    ),
) -> None:
    """
    Promote a draft record to canonical state.

    Reads the draft from .spine/drafts/<draft_id>.json, appends it to the
    appropriate canonical JSONL file (evidence.jsonl or decisions.jsonl),
    then removes the draft file.

    This is an explicit operator action. Promotion is never silent or automatic.
    """
    try:
        repo_root, spine_root = resolve_roots(cwd)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(EXIT_CONTEXT)

    service = DraftService(repo_root, spine_root=spine_root)
    try:
        record = service.confirm(draft_id)
        record_type = "evidence" if "kind" in record else "decision"
        if record_type == "evidence":
            console.print(f"[bold green]Draft confirmed:[/bold green] [{record.get('kind', '?')}] {record.get('description', '') or '(no description)'}")
        else:
            console.print(f"[bold green]Draft confirmed:[/bold green] {record.get('title', '?')}")
        console.print(f"  Promoted from draft: {draft_id}")
        console.print(f"  Added to canonical: .spine/{'evidence.jsonl' if record_type == 'evidence' else 'decisions.jsonl'}")
    except DraftNotFoundError as exc:
        console.print(f"[bold red]Draft not found:[/bold red] {exc}")
        raise typer.Exit(EXIT_VALIDATION)
    except DraftError as exc:
        console.print(f"[bold red]Draft error:[/bold red] {exc}")
        raise typer.Exit(EXIT_VALIDATION)
