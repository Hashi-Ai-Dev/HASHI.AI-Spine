# SPINE v0.1.1 Self-Dogfood Cleanup Report

**Date:** 2026-04-06
**Validator:** SPINE Core v0.1 running on its own repo
**Branch:** `dogfood/spine-v0.1-self-validation`

---

## What Worked Well

### Mission governance loop
Setting the mission via CLI felt natural. `spine mission show` renders cleanly in the Rich table format. Mission state persisted correctly in `mission.yaml` and was read back accurately by the brief and review services.

### Opportunity scoring
Deterministic scoring correctly identified v0.1.1 cleanup as the highest-value move (3.59 vs ≤1.6 for all alternatives). The rubric is honest — it doesn't flatter expansion impulses.

### Brief generation
Both Claude and Codex briefs are well-structured with all required sections (mission summary, allowed scope, forbidden expansions, acceptance criteria, testing expectations, evidence requirements, planning note). Briefs are readable and immediately useful to an agent.

### Evidence/decision logging
`spine evidence add` and `spine decision add` work cleanly. JSONL appends are correct and parseable. The required field validation (title, why, decision) is correct.

### Test suite
117 tests pass, 1 skipped (Windows SIGINT issue — not a real failure). Tests are well-organized and cover the Phase 2 surface.

### Review aggregation
`spine review weekly` correctly aggregates evidence, decisions, drift events, and mission state into a readable markdown document. The Rich table formatting for drift severity is useful.

### CLI ergonomics
Typer subcommand groups work correctly (`spine mission show`, `spine mission set`, etc.). `--cwd` flag support in init is correct. Help text is functional.

---

## What Felt Clunky

### `spine opportunity score` argument order
The command requires `TITLE` as a positional argument: `spine opportunity score "title" -d "description"`. The `-d` for `--description` is non-obvious. A `--description` long form would be clearer.

### Drift scanner misses committed forbidden files
`spine drift scan` uses `git diff HEAD` which only catches **uncommitted** changes. If a forbidden file (e.g., `ui/dashboard.py`) is committed to the current branch, drift scan will NOT flag it. This is a real false-negative gap — a user could drift their scope by committing forbidden files and never being warned.

**Impact:** A builder could add `ui/` or `auth/` to their repo, commit it, and run `drift scan` without any HIGH severity alert.

### Review `--days 1` may not work correctly
When running `spine review weekly --days 1`, the first review run showed 0 evidence events despite events existing with timestamps within the last day. Regenerating with `--days 7` showed all 4 events correctly. Possible timezone edge case when the cutoff lands near midnight UTC.

### Brief files use timestamp names
Brief files are named `20260406_015946.md` (timestamp-based). This is not human-friendly for navigation. `claude_brief.md` / `codex_brief.md` or `claude/current.md` would be easier to reference.

### Review doesn't distinguish between duplicate drift events
Two drift scans both flagged `pyproject.toml` as `dependency_bloat` — the review shows them as separate events without deduplication or a "same file scanned twice" note.

### Doctor output for a healthy repo is verbose
`spine doctor` prints many lines of output even on a clean, healthy repo. For a validation loop, a `--quiet` flag would be useful.

---

## What Felt Fake or Too Manual

### AGENTS.md and CLAUDE.md are stale
Both files still say "Phase 1 only" and describe `spine init` as the only implemented command. They were not updated when Phase 2 shipped. An agent reading these files today would get a wrong picture of what SPINE can do.

### `spine drift scan` requires a real git repo
`drift scan` exits with code 1 when run outside a git repo. For a self-governance tool, this is fine in practice but the error message could be friendlier ("Not a git repository — drift scan requires a git repo").

### No automatic evidence linking
Evidence records are standalone strings. There's no automatic linking to the decision that prompted them or the brief that was generated. This is fine for Phase 1 but makes the review feel like a list of facts rather than a connected narrative.

---

## Commands and Outputs That Need Polish

### `spine mission set` — `--promise` vs `--one-sentence-promise`
The CLI uses `--promise` but the spec and user mental model expect `--one-sentence-promise`. Minor friction.

### `spine evidence add` — `--kind` enum choices not shown in help
`spine evidence add --help` does not list the allowed `EVIDENCE_KINDS` values. A user has to guess or read source. Same for `--recommendation` in `spine review weekly`.

### `spine drift scan` — summary doesn't distinguish scan runs
The drift summary shows `LOW: 1` but doesn't indicate whether this is a new scan or cumulative. The `drift.jsonl` accumulates events across scans.

### Brief footer says "v0.1" but version constant was recently fixed
After `constants.py` was fixed to `SPINE_VERSION = "0.1"`, the brief footer correctly shows "v0.1". Confirmed working.

---

## Drift Scanner Quality Notes

### False Positive Risk: Unanchored Regex
`drift_service.py` uses unanchored regex patterns like `(?i)auth(?:entication|orization)?` which can match in the middle of words (e.g., "authorization" in a variable name). This could cause false positives on large codebases.

**Example:** A file containing `def handle_authorization()` would trigger the auth forbidden_expansion pattern even if the mission doesn't forbid auth.

### False Negative Risk: Committed Files (see above)
`git diff HEAD` is blind to committed forbidden files. The scanner is a "session cleaner" not a "scope auditor."

### Severity Calibration
- `pyproject.toml` change → LOW `dependency_bloat` — appropriate
- `ui/dashboard.py` uncommitted → would be flagged as HIGH `forbidden_expansion` — appropriate if uncommitted
- A committed `ui/dashboard.py` → silently ignored — inappropriate

---

## Brief Quality Notes

Both briefs (Claude and Codex) are well-structured and usable. Required sections present:
- Mission summary ✓
- Allowed scope ✓
- Forbidden expansions ✓
- Acceptance criteria ✓
- Testing expectations ✓
- Evidence requirements ✓
- Planning note ✓
- Worktree recommendation (Codex only) ✓
- Repo discipline (Codex only) ✓

**Minor polish items:**
- Footer: `_Generated by SPINE v0.1_` is correct
- `proof_requirements` shows placeholder `_No proof requirements defined yet._` — not wrong, just slightly rough
- No explicit "non-goals" section in briefs

---

## Review Quality Notes

The review is honest and readable. It correctly shows:
- Mission title and status
- Evidence events with timestamps
- Decision with why and alternatives
- Drift severity groupings
- Recommendation

**Issues:**
- First `--days 1` run produced 0 events (possible timezone issue near midnight UTC cutoff)
- Drift events for same file across multiple scans show as separate entries
- Recommendation choices are not validated with helpful error until the command runs

---

## Correctness Bugs Found

1. **CRITICAL (already fixed before this cycle):** `opportunity_service` was not instantiated in `mcp_cmd.py` line 65, causing a `NameError` at runtime when `opportunity_score` tool was called.

2. **CRITICAL (already fixed before this cycle):** MCP `call_tool` responses used `TextResourceContents` (resource protocol type) instead of `TextContent` (tool result type).

3. **FIXED in v0.1.1 hardening:** Drift scanner was using only `git diff HEAD` (working tree only). Now implements two modes:
   - Mode A: `git diff HEAD` for working tree / uncommitted changes
   - Mode B: `git diff <default_branch>...HEAD` for committed branch drift
   - Default branch detection: `origin/HEAD` → local `main` → local `master` → working tree only
   - Fixed regex anchoring for auth/billing patterns (path-separator anchored)
   - **Verified:** `ui/dashboard.py` committed on a feature branch is now detected as HIGH forbidden_expansion

4. **FIXED in v0.1.1:** AGENTS.md and CLAUDE.md updated to reflect Phase 2 command surface

5. **LOW:** `spine opportunity score` uses `-d` short form for `--description`, non-obvious.

6. **LOW:** `spine evidence add --help` doesn't list valid `--kind` choices.

7. **LOW:** Review `--days 1` produced empty results in first test run (timezone edge case suspected).

8. **LOW:** Drift regex patterns are unanchored — potential false positives in large codebases.

9. **LOW:** Brief files named by timestamp instead of stable identifiers.

10. **LOW:** Doctor command lacks `--quiet` flag.

---

## Cleanup Tasks for v0.1.1

### Must Fix (Correctness) — DONE

- [x] Anchor regex patterns in `drift_service.py` FORBIDDEN_PATTERNS (add `^` and `$` anchors) — done
- [x] Add `--against-branch` detection in drift scan to compare against parent branch, not just uncommitted diff — done (Mode A + Mode B detection)
- [x] Update AGENTS.md to reflect Phase 2 command surface — done
- [x] Update CLAUDE.md to reflect Phase 2 scope (remove "Phase 1 only" constraint) — done

### Should Fix (Usability)

- [ ] Add `--description` long-form option to `spine opportunity score`
- [ ] List `EVIDENCE_KINDS` values in `spine evidence add --help`
- [ ] List recommendation choices in `spine review weekly --help`
- [ ] Investigate `--days 1` timezone edge case in review filtering
- [ ] Add `--quiet` / `--json` flag to `spine doctor`

### Nice to Have (Polish)

- [ ] Deduplicate drift events in review aggregation
- [ ] Name brief files as `claude/current.md` / `codex/current.md` instead of timestamps
- [ ] Add `spine opportunity score --list` to show all scored opportunities
- [ ] Validate `recommendation` enum before calling service in review command

---

## Items Explicitly Deferred (Phase 3 Expansion)

These are out of scope for v0.1.1 based on the self-dogfood validation:

- Dashboard / TUI — violates forbidden expansions, no evidence of need
- Remote MCP — violates forbidden expansions
- SQLite projection — not yet justified; JSONL + YAML approach is sufficient
- Model-assisted scoring — violates Phase 1/2 deterministic-first rule
- Multi-mission support — Phase 4 territory
- Auto-evidence linking — requires richer data model
- Background drift scanning — violates non-daemon requirement
- Auth/billing/cloud sync — explicitly forbidden

---

## Summary

SPINE completed one real self-governance loop on its own repo:
- Mission set and visible
- 5 opportunity scores recorded
- 2 briefs generated and verified
- 5 evidence events logged
- 1 decision recorded
- 2 drift scans executed (baseline + drill)
- 1 weekly review generated
- 1 cleanup report produced

**Net verdict:** SPINE Core v0.1 is usable for its intended purpose. The governance loop is real, not theatrical. Evidence and decisions are logged correctly. Opportunity scoring is honest. The drift scanner has a real false-negative gap for committed files that should be fixed in v0.1.1. Brief and review quality are high. The main cleanup work is updating docs and polishing ergonomics — not adding surface.

**Proof:** this report itself is evidence that the loop works.
