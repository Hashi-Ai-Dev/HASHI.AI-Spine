# SPINE Beta Implementation Report — Blocker Stabilization Pass

**Date:** 2026-04-08
**Branch:** `beta/blocker-fixes-checkpoint-hooks`
**Issues targeted:** #43, #44, #45

---

## Summary

This pass fixes three shipped Beta regression blockers that prevented the
checkpoint + hook workflow from functioning correctly.  No scope was expanded
beyond these targeted bug fixes.

---

## Blockers Fixed

### Issue #43 — `check before-pr` exits 1 on healthy repos (doctor warnings)

**Root cause:** `_check_doctor_health()` in `check_service.py` mapped any
doctor `warning` to a `warn` CheckItem.  `BeforePrResult.result` treated any
`warn` as `review_recommended`, causing exit 1.

The four warnings about missing `.spine/reviews`, `.spine/briefs`,
`.spine/skills`, and `.spine/checks` are documented as expected and
non-blocking on a freshly cloned repo (empty git-untracked dirs).  But
`check before-pr` treated them as failures.

**Fix applied:** Doctor *errors* still produce a `fail` CheckItem (blocking).
Doctor *warnings* now produce a `pass` CheckItem with an advisory note.
Signal is preserved — the warnings appear in output — but they no longer
force `review_recommended` / exit 1.

**File changed:** `src/spine/services/check_service.py` — `_check_doctor_health()`

**Tests added:**
- `tests/test_check_before_pr.py::test_doctor_warnings_do_not_cause_failure`
- `tests/test_check_before_pr.py::test_doctor_errors_still_cause_failure`

---

### Issue #44 — Installed hook script uses bare `spine` instead of `uv run spine`

**Root cause:** `_build_hook_script()` in `hooks_service.py` emitted
`spine check before-pr`.  Since SPINE is invoked via `uv run spine` in
standard setups, the bare `spine` command is not in PATH.  The installed
pre-push hook failed with "command not found" in standard installations.

**Fix applied:** Hook script now emits `uv run spine check before-pr`.
The comment lines in the hook script header were also updated to use
`uv run spine hooks list` / `uv run spine hooks uninstall`.  The human-
readable install success message was updated to match.

**File changed:** `src/spine/services/hooks_service.py` — `_build_hook_script()`

**Tests added:**
- `tests/test_hooks.py::test_install_hook_uses_uv_run_spine`

---

### Issue #45 — AGENTS.md template ships invalid CLI commands to governed repos

**Root cause:** The `_AGENTS_MD_CONTENT` template in `init_service.py`
contained two stale/invalid SPINE command references:
1. `uv run spine brief generate ...` — invalid; correct form is `uv run spine brief --target claude`
2. `uv run spine opportunity add ...` — invalid; correct form is `uv run spine opportunity score <title>`

Any agent or human reading a SPINE-generated `AGENTS.md` would attempt these
commands and receive errors.

**Fix applied:** Both command references corrected in the template string.

**File changed:** `src/spine/services/init_service.py` — `_AGENTS_MD_CONTENT`

**Tests added:**
- `tests/test_init.py::test_agents_md_template_has_valid_brief_command`
- `tests/test_init.py::test_agents_md_template_has_valid_opportunity_command`

---

## Files Changed

| File | Change |
|------|--------|
| `src/spine/services/check_service.py` | Doctor warnings demoted to advisory-only (`pass` not `warn`) |
| `src/spine/services/hooks_service.py` | Hook script uses `uv run spine check before-pr` |
| `src/spine/services/init_service.py` | AGENTS.md template: corrected two invalid command references |
| `tests/test_check_before_pr.py` | Added 2 regression tests for #43 |
| `tests/test_hooks.py` | Added 1 regression test for #44 |
| `tests/test_init.py` | Added 2 regression tests for #45 |
| `docs/SPINE_BETA_IMPLEMENTATION_REPORT.md` | This file |

---

## Test Results

```
352 passed in 11.65s
```

All pre-existing tests continue to pass.  5 new focused regression tests added.

---

## SPINE Governance

- `uv run spine decision add` — recorded rationale for this blocker-fix pass
- `uv run spine evidence add` — logged implementation evidence
- `uv run spine review weekly --recommendation continue` — weekly review generated

---

## Scope Confirmation

- **#36, #37, #38:** Not touched. Not in scope.
- No daemon/background behavior added.
- No check/hook system redesign.
- No new features.
- No broad docs rewrite — only this report added.
