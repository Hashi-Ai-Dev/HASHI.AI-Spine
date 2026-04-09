"""spine decision add command — spec-compliant nesting."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from spine.cli.app import app, resolve_roots, EXIT_VALIDATION, EXIT_CONTEXT
from spine.services.decision_service import DecisionService, DecisionValidationError

console = Console()

# ---------------------------------------------------------------------------
# Decision command group (spine decision <action>)
# ---------------------------------------------------------------------------
decision_app = typer.Typer()
app.add_typer(decision_app, name="decision", help="Manage decision records.")


@decision_app.command("add", help="Add a decision record to .spine/decisions.jsonl.")
def decision_add(
    cwd: Path | None = typer.Option(
        None,
        "--cwd",
        help="Target repository path. Overrides SPINE_ROOT. Precedence: --cwd > SPINE_ROOT > cwd.",
    ),
    title: str = typer.Option(..., "--title", "-t", help="Decision title (required)"),
    why: str = typer.Option(..., "--why", "-w", help="Why this decision was made (required)"),
    decision: str = typer.Option(..., "--decision", "-d", help="What was decided (required)"),
    alternatives: str | None = typer.Option(None, "--alternatives", help="Comma-separated alternative options considered"),
    draft: bool = typer.Option(
        False,
        "--draft",
        help="[Beta] Save as a draft under .spine/drafts/ instead of appending to decisions.jsonl. Use 'spine drafts confirm <id>' to promote.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output result as JSON (machine-readable). Exit codes still apply.",
    ),
) -> None:
    """
    Add a decision record to .spine/decisions.jsonl.

    Requires: title, why, decision. All are required.
    Optional: alternatives (comma-separated list).

    Use --draft to save provisionally to .spine/drafts/ without touching canonical state.

    Exit codes:
      0  Success
      1  Validation failure — empty required field
      2  Context failure   — repo not found or .spine/ missing
    """
    try:
        repo_root, spine_root = resolve_roots(cwd)
    except Exception as exc:
        if json_output:
            print(json.dumps({"error": str(exc), "exit_code": EXIT_CONTEXT}, indent=2))
        else:
            console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(EXIT_CONTEXT)

    def parse_list(s: str | None) -> list[str] | None:
        if s is None:
            return None
        return [item.strip() for item in s.split(",") if item.strip()]

    service = DecisionService(repo_root, spine_root=spine_root)
    try:
        if draft:
            decision_record, draft_id = service.add_draft(
                title=title,
                why=why,
                decision=decision,
                alternatives=parse_list(alternatives),
            )
            if json_output:
                data = {"ok": True, "draft": True, "draft_id": draft_id, **decision_record.to_json()}
                print(json.dumps(data, indent=2))
            else:
                console.print(f"[bold yellow]Decision draft saved:[/bold yellow] {decision_record.title}")
                console.print(f"  Why: {decision_record.why}")
                console.print(f"  Decision: {decision_record.decision}")
                if decision_record.alternatives:
                    console.print(f"  Alternatives: {', '.join(decision_record.alternatives)}")
                console.print(f"  Draft ID: {draft_id}")
                console.print(f"  Promote with: spine drafts confirm {draft_id}")
        else:
            decision_record = service.add(
                title=title,
                why=why,
                decision=decision,
                alternatives=parse_list(alternatives),
            )
            if json_output:
                data = {"ok": True, **decision_record.to_json()}
                print(json.dumps(data, indent=2))
            else:
                console.print(f"[bold green]Decision added:[/bold green] {decision_record.title}")
                console.print(f"  Why: {decision_record.why}")
                console.print(f"  Decision: {decision_record.decision}")
                if decision_record.alternatives:
                    console.print(f"  Alternatives: {', '.join(decision_record.alternatives)}")
                console.print(f"  Created at: {decision_record.created_at}")
    except DecisionValidationError as exc:
        if json_output:
            print(json.dumps({"error": str(exc), "exit_code": EXIT_VALIDATION}, indent=2))
        else:
            console.print(f"[bold red]Validation error:[/bold red] {exc}")
        raise typer.Exit(EXIT_VALIDATION)


@decision_app.command("list", help="List decision records from .spine/decisions.jsonl.")
def decision_list(
    cwd: Path | None = typer.Option(
        None,
        "--cwd",
        help="Target repository path. Overrides SPINE_ROOT. Precedence: --cwd > SPINE_ROOT > cwd.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output result as JSON (machine-readable).",
    ),
) -> None:
    """
    List all decision records from .spine/decisions.jsonl, sorted by created_at.

    Exit codes:
      0  Success (including empty list)
      2  Context failure — repo not found or .spine/ missing
    """
    try:
        repo_root, spine_root = resolve_roots(cwd)
    except Exception as exc:
        if json_output:
            print(json.dumps({"error": str(exc), "exit_code": EXIT_CONTEXT}, indent=2))
        else:
            console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(EXIT_CONTEXT)

    service = DecisionService(repo_root, spine_root=spine_root)
    records = service.list()

    if json_output:
        print(json.dumps({"ok": True, "count": len(records), "records": records}, indent=2))
        return

    if not records:
        console.print("[dim]No decision records found.[/dim]")
        return

    for rec in records:
        title = rec.get("title", "")
        decision = rec.get("decision", "")
        created_at = rec.get("created_at", "")[:10]  # date portion only
        alternatives = rec.get("alternatives", [])
        console.print(f"[bold green]{title}[/bold green]  [dim]{created_at}[/dim]")
        console.print(f"  Decision: {decision}")
        if alternatives:
            console.print(f"  Alternatives: {', '.join(alternatives)}")
