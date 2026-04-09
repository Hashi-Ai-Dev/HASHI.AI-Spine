# SPINE Beta Implementation Report

**Repo:** `Hashi-Ai-Dev/SPINE`
**Last updated:** 2026-04-09

---

## Purpose

Tracks the implementation state of pre-beta-exit issues (Milestone #5) and the
broader beta feature queue.  Updated as issues are resolved.

---

## Pre-Beta-Exit Blockers (Milestone #5)

| # | Issue | Branch / PR | Status |
|---|---|---|---|
| #65 | `check before-pr --json` structured doctor detail | PR #69 | ✅ Merged |
| #66 | `check before-work` no-brief advisory not exit 1 | `beta/usability66-before-work-advisory` | ✅ Implemented — PR pending |
| #60 | SECURITY_BASELINE wrong repo name | — | 🟡 Open |

**Remaining blockers:** 1 (#60)

---

## Issue #66 — before-work no-brief advisory (2026-04-09)

### Problem

`spine check before-work` returned exit 1 ("Review recommended") when no brief
had been generated yet.  A fresh repo or a first-run agent would be blocked
before any useful work began — a hard failure for something that is merely
orientation context, not a governance requirement.

### Fix

**File:** `src/spine/services/check_service.py`

Changed `BeforeWorkResult.result` to only block on hard failures (`status="fail"`).
Warns (like `recent_brief=warn` for no-brief) now surface advisory guidance and
exit 0.  `BeforePrResult` is unchanged — it retains its strict warn+fail blocking
because a PR gate should be strict.

```python
# Before (both warn and fail triggered exit 1):
if item.status in ("warn", "fail"):
    return "review_recommended"

# After (only hard failures trigger exit 1):
if item.status == "fail":
    return "review_recommended"
```

Updated `_check_recent_brief()` message to preferred wording:

```
No brief found. Run `spine brief --target claude` to generate one.
```

Updated `check_before_work` help text and docstring to document advisory behavior.

### Behavior change

| Scenario | Before | After |
|---|---|---|
| No brief generated | exit 1 + WARN shown | exit 0 + WARN shown |
| Empty briefs dir | exit 1 + WARN shown | exit 0 + WARN shown |
| Brief exists | exit 0 + PASS shown | exit 0 + PASS shown (unchanged) |
| Missing .spine/ | exit 1 + FAIL | exit 1 + FAIL (unchanged) |
| Bad mission.yaml | exit 1 + FAIL | exit 1 + FAIL (unchanged) |
| Doctor errors | exit 1 + FAIL | exit 1 + FAIL (unchanged) |

### Files changed

- `src/spine/services/check_service.py` — `BeforeWorkResult.result` logic + `_check_recent_brief()` message
- `src/spine/cli/check_cmd.py` — help text and docstring
- `tests/test_check_before_work.py` — updated 2 tests, added 8 new tests

### Tests

35 tests in `test_check_before_work.py`, all passing.  New tests cover:

- `test_no_brief_is_advisory_exit_0` — exit 0 for no-brief
- `test_no_brief_still_shows_warn_in_output` — WARN still visible in table
- `test_no_brief_advisory_message_wording` — preferred wording present
- `test_briefs_dir_empty_is_advisory_exit_0` — empty briefs dir also exits 0
- `test_no_brief_json_result_is_pass` — JSON `result` field is `"pass"`, `recent_brief` status is `"warn"`
- `test_no_brief_json_advisory_message` — JSON message contains `spine brief --target claude`
- `test_real_blockers_still_cause_exit_1_after_advisory_fix` — mission failures still exit 1
- `test_spine_dir_missing_still_causes_exit_1_after_advisory_fix` — missing .spine/ still exits 1
- `test_help_text_updated_for_advisory_behavior` — help text reflects advisory behavior

Full suite: **544 tests passing**.

### SPINE governance

- `spine decision add` — recorded decision rationale
- `spine evidence add` — recorded implementation evidence
- `spine review weekly --recommendation continue` — weekly review generated

---

## Beta Feature Queue — Summary

| # | Issue | Status |
|---|---|---|
| #31 | `spine check before-pr` preflight checkpoint | ✅ Merged — PR #35 |
| #32 | Handoff/PR-prep summary primitive | ✅ Merged — PR #39 |
| #33 | Draftable governance records | ✅ Merged — PR #40 |
| #34 | Local optional hook/checkpoint integration | ✅ Merged — PR #41 |
| #36 | Mission refine draft flow | ✅ Merged — PR #47 |
| #37 | Compatibility/integration guide | ✅ Merged — PR #48 |
| #38 | Deterministic validation fixtures | ✅ Merged — PR #52 |
| #43 | `check before-pr` exit 1 on healthy repos | ✅ Merged — PR #46 |
| #49 | Write-flow machine-readable consistency | ✅ Merged — PR #53 |
| #50 | Before-work / start-session governance checkpoint | ✅ Merged — PR #54 |
| #57 | MCP TextContent NameError | ✅ Merged — PR #61 |
| #58 | README exit code + test count | ✅ Merged — PR #63 |
| #59 | `spine drift scan --json` | ✅ Merged — PR #67 |
| #64 | `spine evidence list` + `spine decision list` | ✅ Merged — PR #68 |
| #65 | `check before-pr --json` structured doctor detail | ✅ Merged — PR #69 |
| #66 | `check before-work` no-brief advisory | ✅ Branch ready — PR pending |
| #60 | SECURITY_BASELINE wrong repo name | 🟡 Open |
| #51 | Beta-exit proof/validation | 📋 Last — blocked until #60 cleared |
