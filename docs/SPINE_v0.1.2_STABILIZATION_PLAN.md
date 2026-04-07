# SPINE v0.1.2 Stabilization Plan

**Branch**: `claude/stabilize-v0.1.2-cwd-Rc4CD`  
**Date**: 2026-04-07  
**Status**: Executed

---

## Problem Statement

Phase 2 commands were not usable for external-repo governance without either:
- `cd`-ing into the target repo, or
- Setting `SPINE_ROOT` as an environment variable (process-global, requires shell setup)

This made external-repo usage unnecessarily painful, as documented in GitHub Issue #5.

`spine init` and `spine review weekly` already had `--cwd` support. The other 8 Phase 2 command surfaces had no equivalent.

---

## Scope

**In scope**:
- Add `--cwd PATH` to all Phase 2 commands that lacked it
- Unhide `--cwd` on `spine review weekly` (was `hidden=True`, "for testing")
- Update help text for new `--cwd` options
- Add focused `--cwd` tests
- README quickstart note (partial Issue #9 cleanup)

**Out of scope**:
- Phase 3A implementation
- Global `--cwd` at the app callback level (adds surface area, breaks backward-compat)
- Redesigning SPINE_ROOT semantics
- Dashboard, cloud, MCP expansion

---

## Implementation Approach

**Minimal, consistent, explicit.** Each command receives a new option:

```python
cwd: Path | None = typer.Option(
    None,
    "--cwd",
    help="Target repository path (for external-repo usage without cd or SPINE_ROOT).",
)
```

This is passed directly to the existing `resolve_roots(cwd)` function, which already handles `None` (falls back to `Path.cwd()`) and `SPINE_ROOT` env var.

No changes to `resolve_roots()`, no changes to services, no behavior changes for existing invocations.

---

## Commands Updated

| Command | Before | After |
|---------|--------|-------|
| `spine mission show` | no `--cwd` | `--cwd` added |
| `spine mission set` | no `--cwd` | `--cwd` added |
| `spine evidence add` | no `--cwd` | `--cwd` added |
| `spine decision add` | no `--cwd` | `--cwd` added |
| `spine opportunity score` | no `--cwd` | `--cwd` added |
| `spine drift scan` | no `--cwd` | `--cwd` added |
| `spine brief` | no `--cwd` | `--cwd` added |
| `spine doctor` | no `--cwd` | `--cwd` added |
| `spine mcp serve` | no `--cwd` | `--cwd` added |
| `spine review weekly` | `--cwd` hidden, "for testing" | unhidden, help text updated |

---

## Tests

New test file: `tests/test_cwd_support.py`  
13 tests covering:
- `doctor --cwd` (human + JSON output)
- `mission show --cwd` (human + JSON output)
- `mission set --cwd` with persistence check
- `evidence add --cwd` with JSONL verification
- `decision add --cwd` with JSONL verification
- `opportunity score --cwd` with JSONL verification
- `drift scan --cwd`
- `brief --cwd`
- `review weekly --cwd` (human + JSON output)
- Two-repo isolation test (side-by-side repos targeted correctly)

---

## Risk Assessment

**Low risk.** Changes are:
- Additive (new optional parameter, default `None`)
- No changes to services, models, or utilities
- Backward-compatible (omitting `--cwd` behaves identically to before)
- All existing 123 tests continue to pass
