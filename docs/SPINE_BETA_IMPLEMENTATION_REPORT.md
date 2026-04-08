# SPINE Beta Implementation Report

---

## Issue #36 — Mission Refine Draft Flow

**Date:** 2026-04-08
**Branch:** `beta/issue36-mission-refine-draft-flow`
**Issue targeted:** #36 — Beta: mission refine draft flow — explicit operator-invoked mission interview

---

### Summary

Implements an explicit mission refinement flow that produces a draft mission
first, requiring explicit operator confirmation before any canonical update.
No silent mutation of `mission.yaml`.

---

### Refine/Draft Flow Chosen

**Non-interactive flag-based design** — same option surface as `spine mission set`
but writes to a draft instead of canonical state.

Rationale:
- Deterministic and testable without interactive input
- Explicit operator control — every field is visible in the command line
- Low implementation risk — reuses existing model/service patterns
- `--cwd` support falls out naturally from the existing `resolve_roots` pattern

Command:
```
spine mission refine [--cwd <path>] [--title ...] [--status ...] [--target-user ...]
                     [--user-problem ...] [--promise ...] [--metric-type ...]
                     [--metric-value ...] [--scope ...] [--forbid ...]
                     [--proof ...] [--kill ...]
```

Output: draft at `.spine/drafts/missions/<timestamp>.yaml`, clearly labeled
non-canonical via YAML comment headers.

---

### Confirmation/Promotion Behavior

```
spine mission confirm <draft_id> [--cwd <path>]
```

- Reads draft from `.spine/drafts/missions/<draft_id>.yaml`
- Validates as `MissionModel` (pydantic)
- Writes to canonical `.spine/mission.yaml` (overwrites)
- Removes draft file
- Exits non-zero if draft_id does not exist or is malformed
- **Never silent, never automatic**

---

### Draft/Canonical Separation Rules

| Surface | Behavior |
|---|---|
| `.spine/mission.yaml` | Unchanged by `refine` — operator must `confirm` |
| `.spine/drafts/missions/` | Non-canonical; ignored by `brief`, `doctor`, `review` |
| `spine brief` | Reads canonical mission only |
| `spine doctor` | Scans canonical state only |
| `spine drafts list` | Lists JSON drafts (evidence/decision) — not mission drafts |
| `spine mission drafts` | Lists mission-specific YAML drafts |

Mission drafts are never auto-promoted. Agents may call `refine`; only
operators (or agents with explicit authorization) may call `confirm`.

---

### Draft File Format

```yaml
# SPINE MISSION DRAFT — non-canonical
# Draft ID: mission-20260408T163012345678
# Promote with: uv run spine mission confirm mission-20260408T163012345678
# Source canonical: .spine/mission.yaml
#
version: 1
id: mission-0001
title: ...
status: active
...
```

YAML comments at the top label the file non-canonical and provide the exact
promotion command. The underlying YAML body is a full valid `MissionModel`
(comments are stripped by the YAML parser on load).

---

### Files Changed

| File | Change |
|---|---|
| `src/spine/constants.py` | Added `MISSION_DRAFTS_DIR = "drafts/missions"` |
| `src/spine/services/mission_service.py` | Added `MissionDraftNotFoundError`, `MissionDraftResult`, `refine()`, `confirm_draft()`, `list_mission_drafts()`, `_generate_draft_id()`, `_apply_fields()` (refactored shared field-apply logic) |
| `src/spine/cli/mission_cmd.py` | Added `mission refine`, `mission confirm`, `mission drafts` subcommands |
| `tests/test_mission_refine.py` | New: 26 focused tests |
| `docs/SPINE_STATUS.md` | Narrow update — #36 marked done, next priority updated |
| `docs/SPINE_FEATURE_BACKLOG.md` | Narrow update — #36 marked done, blocker note removed |
| `docs/SPINE_BETA_IMPLEMENTATION_REPORT.md` | This file (updated) |

---

### Test Results

```
26 focused tests added (tests/test_mission_refine.py)
378 total tests pass
0 failures
```

Focused tests cover:
- Command registration (refine, confirm, drafts)
- Draft creation at correct path
- Draft contains proposed fields
- Draft labeled non-canonical (YAML comments)
- Canonical mission.yaml unchanged after refine
- CLI output includes draft_id and promotion hint
- Deterministic naming pattern (mission-YYYYMMDDTHHMMSS)
- Multiple drafts stored separately
- Confirm promotes to canonical
- Confirm removes draft file
- Confirm removes from drafts list
- Nonexistent draft_id fails gracefully
- One confirm leaves other drafts intact
- Canonical unchanged until confirm
- Invalid --status exits 1
- Requires init (exits 2 if no mission.yaml)
- --cwd support for refine, confirm, drafts

---

### SPINE Governance

- `spine decision add` — recorded rationale for Issue #36
- `spine evidence add` — logged implementation work
- `spine review weekly --recommendation continue` — weekly review generated

---

### What Was Explicitly Deferred

| Item | Issue | Status |
|---|---|---|
| Compatibility/integration guide | #37 | Not started — next |
| Deterministic validation fixture harness | #38 | Not started — queued |
| Hook redesign | — | Out of scope |
| Handoff redesign | — | Out of scope |
| AI-generated mission writing (model API calls) | — | Explicitly excluded |
| Team/orchestration features | — | Explicitly excluded |
| Broad draft system expansion | — | Out of scope |

---

## Blocker Stabilization Pass (Issues #43, #44, #45)

**Date:** 2026-04-08
**Branch:** `beta/blocker-fixes-checkpoint-hooks`
**Issues targeted:** #43, #44, #45

---

### Summary

This pass fixes three shipped Beta regression blockers that prevented the
checkpoint + hook workflow from functioning correctly.  No scope was expanded
beyond these targeted bug fixes.

---

### Blockers Fixed

#### Issue #43 — `check before-pr` exits 1 on healthy repos (doctor warnings)

**Root cause:** `_check_doctor_health()` in `check_service.py` mapped any
doctor `warning` to a `warn` CheckItem.  `BeforePrResult.result` treated any
`warn` as `review_recommended`, causing exit 1.

**Fix applied:** Doctor *errors* still produce a `fail` CheckItem (blocking).
Doctor *warnings* now produce a `pass` CheckItem with an advisory note.

**File changed:** `src/spine/services/check_service.py`

---

#### Issue #44 — Installed hook script uses bare `spine` instead of `uv run spine`

**Root cause:** `_build_hook_script()` in `hooks_service.py` emitted `spine check before-pr`.

**Fix applied:** Hook script now emits `uv run spine check before-pr`.

**File changed:** `src/spine/services/hooks_service.py`

---

#### Issue #45 — AGENTS.md template ships invalid CLI commands

**Root cause:** Two stale command references in `init_service.py` template.

**Fix applied:** Both command references corrected.

**File changed:** `src/spine/services/init_service.py`

---

### Test Results (Blocker Pass)

```
352 passed
```
