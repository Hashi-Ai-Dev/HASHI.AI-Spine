"""spine log — short-form evidence add (friction-reduction, #74).

Reduces the per-session discipline tax of the most common governance write:
logging evidence.

    Before:  spine evidence add --kind commit --description "Implemented X"
    After:   spine log commit "Implemented X"

Positional arguments replace verbose --kind / --description flags for the
common one-liner case.  The canonical record produced is identical to
`spine evidence add`.  No hidden state, no auto-logging, no silent mutations.
"""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from spine.cli.app import app, resolve_roots, EXIT_VALIDATION, EXIT_CONTEXT
from spine.models.evidence import EVIDENCE_KINDS
from spine.services.evidence_service import EvidenceService, EvidenceValidationError

console = Console()

# ---------------------------------------------------------------------------
# Log command (spine log <kind> [description])
# ---------------------------------------------------------------------------

_KINDS_HELP = (
    "brief_generated, commit, pr, test_pass, review_done, "
    "demo, user_feedback, payment, kill, narrow"
)


@app.command(
    "log",
    help=(
        "Short-form evidence add. Reduces repeated governance friction.\n\n"
        "  spine log commit 'Implemented X'\n"
        "  spine log test_pass 'All tests green'\n"
        "  spine log pr 'https://github.com/.../pull/42'\n\n"
        f"Allowed kinds: {_KINDS_HELP}\n\n"
        "Produces an identical canonical record to 'spine evidence add'.\n\n"
        "Exit codes:\n"
        "  0  Evidence record appended\n"
        "  1  Validation failure — invalid kind or field\n"
        "  2  Context failure   — repo not found or .spine/ missing"
    ),
)
def log_evidence(
    kind: EVIDENCE_KINDS = typer.Argument(
        ...,
        help=f"Evidence kind. One of: {_KINDS_HELP}",
    ),
    description: str = typer.Argument(
        "",
        help="Description of the evidence.",
    ),
    url: str = typer.Option(
        "",
        "--url",
        help="URL or reference for the evidence (e.g. PR link, commit SHA).",
    ),
    cwd: Path | None = typer.Option(
        None,
        "--cwd",
        help="Target repository path. Overrides SPINE_ROOT. Precedence: --cwd > SPINE_ROOT > cwd.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output result as JSON (machine-readable). Exit codes still apply.",
    ),
) -> None:
    """
    Short-form evidence add — reduce repeated governance friction.

    Equivalent to: spine evidence add --kind <kind> --description <description>

    Positional arguments replace verbose flags for the common one-liner case.
    The canonical record written to .spine/evidence.jsonl is identical.

    Exit codes:
      0  Evidence record appended
      1  Validation failure — invalid kind or field
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

    service = EvidenceService(repo_root, spine_root=spine_root)
    try:
        evidence = service.add(kind=kind, description=description, evidence_url=url)
        if json_output:
            data = {"ok": True, **evidence.to_json()}
            print(json.dumps(data, indent=2))
        else:
            console.print(
                f"[bold green]Evidence added:[/bold green] [{evidence.kind}] "
                f"{evidence.description or '(no description)'}"
            )
            console.print(f"  Created at: {evidence.created_at}")
    except EvidenceValidationError as exc:
        if json_output:
            print(json.dumps({"error": str(exc), "exit_code": EXIT_VALIDATION}, indent=2))
        else:
            console.print(f"[bold red]Validation error:[/bold red] {exc}")
        raise typer.Exit(EXIT_VALIDATION)
