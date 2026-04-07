# SPINE v0.1.2 Stabilization Report

**Date:** 2026-04-07
**Branch:** `claude/stabilize-v0.1.2-readme-eoTjK`
**Status:** Complete — all 5 stabilization items done

---

## Summary

v0.1.2 stabilization is complete. All planned items are merged or resolved:

| # | Item | Status |
|---|------|--------|
| 1 | Add `--cwd` to Phase 2 commands | ✅ Done (PR #11) |
| 2 | Enable Dependabot alerts + secret scanning | ✅ Done (owner via GitHub settings) |
| 3 | Add minimal CI pipeline | ✅ Done (PR #12) |
| 4 | ~~Create org-level ruleset~~ | ❌ Rejected — not a SPINE issue |
| 5 | README / onboarding polish (Issue #9) | ✅ Done (this pass) |

---

## Issue #9 — README Onboarding Polish

### What was wrong

- **No installation instructions** — README said "Requires uv" but never told users how to install SPINE itself
- **Misleading Quickstart** — `cd /your/project && uv run spine init` would fail without SPINE installed or being in the SPINE source directory
- **Stale Known Limitations** — Item #1 said "`--cwd` works only with `spine init`"; this was invalidated by PR #11 which added `--cwd` to all Phase 2 commands
- **Stale "What's Next"** — First bullet said "`--cwd` support on all commands (not just `spine init`)" — already shipped in PR #11
- **Wrong `--cwd` priority** — "Governing an External Repo" section used `SPINE_ROOT` as primary pattern; `--cwd` (now available on all commands) is cleaner and should be primary
- **Wrong Python version badge** — Badge said Python 3.11+; `pyproject.toml` requires 3.12+
- **Stale test count** — Validation section showed "123 passed"; CI now reports 136+

### What was changed

**`README.md`:**
- Added **Installation** section with `git clone` + `uv sync` instructions
- Rewrote **Quickstart** as "Use SPINE on any repo" with `--cwd` as the primary pattern throughout
- Renamed "Governing an External Repo" → "Using SPINE on any repo", promoted `--cwd` as primary, demoted `SPINE_ROOT` to "Alternative"
- Removed stale Known Limitation #1 (re: `--cwd` init-only restriction)
- Removed stale "What's Next" bullet (re: `--cwd` expansion — already done)
- Fixed Python badge: 3.11+ → 3.12+
- Fixed test count: 123 → 136+

**`docs/SPINE_STATUS.md`:**
- Marked Item #5 (onboarding docs) as ✅ Done
- Updated milestone from "4/5 done" to "5/5 done"
- Updated "Next Move" to reflect completion

**`docs/SPINE_FEATURE_BACKLOG.md`:**
- Marked onboarding item as ✅ Done with description of changes

**`docs/SPINE_v0.1.2_STABILIZATION_REPORT.md`:** (this file)
- Created

### SPINE governance records

- **Decision added:** "README onboarding polish for v0.1.2"
- **Evidence added:** commit — README changes described
- **Weekly review:** recommendation=continue, notes="v0.1.2 stabilization: README onboarding polish"

---

## Test Results

```
136 passed in 4.41s
```

CI remains green.

---

## Onboarding Quality Check

Does the new README answer:

| Question | Answer |
|----------|--------|
| What is SPINE? | ✅ First paragraph + "Who is this for?" |
| Who is it for? | ✅ "Who is this for?" section |
| How do I install it? | ✅ New "Installation" section |
| How do I use it on an external repo? | ✅ Quickstart + "Using SPINE on any repo" both show `--cwd` |
| What are the current alpha limitations? | ✅ "Known Limitations" (now accurate, 5 items) |

---

## Deferred

- Phase 3A / v0.2 planning — remains in spec, awaits human approval (Issue #10)
- Richer drift detection
- Improved weekly review output
- Migration tooling

*Next step: close Issue #9, tag v0.1.2, publish release.*
