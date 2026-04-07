# SPINE v0.1.2 Stabilization Report

**Branch**: `claude/stabilize-v0.1.2-cwd-Rc4CD`  
**Date**: 2026-04-07  
**Status**: Complete — green, ready for PR review

---

## Summary

Issue #5 (`Add --cwd support to Phase 2 commands`) is fully addressed. All Phase 2 commands now accept `--cwd PATH` to target an external repository without `cd` or `SPINE_ROOT`. 136 tests pass (up from 123).

---

## What Was Done

### 1. `--cwd` added to 9 command surfaces

Each command received one new optional parameter:
```
--cwd PATH   Target repository path (for external-repo usage without cd or SPINE_ROOT).
```

Affected files:
- `src/spine/cli/mission_cmd.py` — `mission show`, `mission set`
- `src/spine/cli/evidence_cmd.py` — `evidence add`
- `src/spine/cli/decision_cmd.py` — `decision add`
- `src/spine/cli/opportunity_cmd.py` — `opportunity score`
- `src/spine/cli/drift_cmd.py` — `drift scan`
- `src/spine/cli/brief_cmd.py` — `brief`
- `src/spine/cli/doctor_cmd.py` — `doctor`
- `src/spine/cli/mcp_cmd.py` — `mcp serve`

### 2. `spine review weekly --cwd` unhidden

`review_weekly` already had `--cwd` as a `hidden=True` parameter described as "for testing". Updated to visible with consistent help text and corrected type annotation (`Path | None`).

File: `src/spine/cli/review_cmd.py`

### 3. New test file: `tests/test_cwd_support.py`

13 focused tests, all passing:
- `test_doctor_cwd` — doctor targets external repo
- `test_doctor_cwd_json` — JSON output verified
- `test_mission_show_cwd` — shows external repo mission
- `test_mission_show_cwd_json` — JSON output verified
- `test_mission_set_cwd` — sets and persists title in external repo
- `test_evidence_add_cwd` — appends to external repo's evidence.jsonl
- `test_decision_add_cwd` — appends to external repo's decisions.jsonl
- `test_opportunity_score_cwd` — appends to external repo's opportunities.jsonl
- `test_drift_scan_cwd` — scans external repo's git state
- `test_brief_cwd` — generates brief in external repo's .spine/briefs/
- `test_review_weekly_cwd` — generates review in external repo
- `test_review_weekly_cwd_json` — JSON output verified
- `test_cwd_two_repos_isolated` — two side-by-side repos targeted correctly

### 4. Stabilization plan document

`docs/SPINE_v0.1.2_STABILIZATION_PLAN.md`

---

## SPINE Self-Governance Commands Run

```
uv run spine mission show
uv run spine doctor
uv run spine decision add  --title "Add --cwd to Phase 2 commands" ...
uv run spine evidence add  --kind commit --description "v0.1.2 stabilization: ..."
uv run spine review weekly --recommendation continue --notes "v0.1.2 stabilization: ..."
```

---

## Test Results

```
136 passed in 5.08s
```

- Pre-existing tests: 123 (all passing, no regressions)
- New `--cwd` tests: 13
- Total: 136

---

## Issue #9 (README quickstart) — Partial

The change makes the README's "Known Limitation #1" (`--cwd` only works with `spine init`) obsolete. A follow-on README update to reflect the new `--cwd` availability across all commands is the natural next step, but was not done in this pass to keep scope tight.

---

## What Was Deferred

- README quickstart update for external-repo usage (Issue #9 proper)
- Phase 3A (SQLite projection, model-assisted scoring)
- CI pipeline
- Org-level ruleset / Dependabot

---

## Recommendation

**Continue.** Branch is green, changes are narrow and backward-compatible. Ready for PR review as `stabilize/v0.1.2-cwd-support`.
