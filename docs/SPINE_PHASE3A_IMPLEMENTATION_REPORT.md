# SPINE Phase 3A Implementation Report

**Issue:** #18 — Bootstrap polish + discipline-tax ergonomics  
**Branch:** `phase3a/issue18-bootstrap-discipline-tax`  
**Date:** 2026-04-07  
**Status:** Complete

---

## Issue Targeted

Issue #18: Bootstrap polish + discipline-tax ergonomics.

Scope: reduce first-run friction and repeated-use ceremony without hiding
governance or introducing silent behavior. All changes are explicit,
deterministic, and operator-visible.

---

## Friction Points Addressed

### 1. Stale AGENTS.md and CLAUDE.md templates (bootstrap content)

**Before:** `spine init` generated `AGENTS.md` and `CLAUDE.md` files containing
"Phase 1 implements only `spine init`", "Do not add new CLI commands", and
"The only implemented command is `spine init`". These were factually wrong for
any repo in Phase 3A (nine commands now exist). Operators bootstrapping a new
repo would receive misleading governance guidance.

**After:** Updated templates reflect Phase 3A reality:
- `AGENTS.md` lists all governance commands (`mission show`, `doctor`,
  `evidence add`, `decision add`, `drift scan`, `review weekly`, `brief generate`)
- `CLAUDE.md` title is "SPINE Governance" (not "SPINE Phase 1"); stale
  copy-restrictions removed; updated quick reference includes `spine doctor`

### 2. `spine init` next-steps panel — stale title, wrong verification step

**Before:** Panel title was "SPINE Phase 1" (stale). Step 4 was
"Run `uv run pytest`" — a developer instruction, not an operator verification
step. No mention of `spine doctor` or committing governance state to git.

**After:**
- Panel title: "Bootstrap complete"
- Step 3: "Run `uv run spine doctor` — verify governance state is valid"
- Step 4: `git add .spine/ AGENTS.md CLAUDE.md .claude/ .codex/` +
  `git commit -m 'chore: add SPINE governance'`
- Footer: "Run `uv run spine --help` to see all available commands."

### 3. Doctor: absolute paths in contract-file error messages

**Before:** `_check_repo_contract()` used `str(path)` for the file column,
producing full absolute paths like `/home/user/myrepo/AGENTS.md`. These were
noisy, leaked host-specific paths, and were inconsistent with all other doctor
error rows (which used relative paths).

**After:** File column now shows the relative filename (`AGENTS.md`,
`CLAUDE.md`, etc.). Error message changed to "Missing repo contract file — run
'spine init' to create it" — actionable with a specific command.

### 4. Doctor: `.spine/` missing error message not explicit about the fix

**Before:** ".spine/ directory does not exist. Run 'spine init' first."

**After:** ".spine/ not found — run 'uv run spine init' to bootstrap governance
state" — uses the exact full command, consistent with other messages.

### 5. `MissionNotFoundError`: context-blind error message

**Before:** "mission.yaml not found at /absolute/path/to/.spine/mission.yaml.
Run 'spine init' first." — showed absolute path; same message whether
`.spine/` was absent entirely or just `mission.yaml` was missing.

**After:** Two distinct cases with relative paths:
- If `.spine/` is absent: ".spine/ not found — run 'uv run spine init' to
  bootstrap governance state"
- If `.spine/` exists but `mission.yaml` is missing: ".spine/mission.yaml not
  found — run 'uv run spine init' to create it, or restore it from version
  control"

### 6. `--cwd` option hidden in `spine init`

**Before:** `--cwd` was `hidden=True` in `init_cmd.py`, making it invisible in
`spine init --help` — inconsistent with all other commands where `--cwd` is
visible. Operators couldn't discover the targeting option.

**After:** `--cwd` is visible in `spine init --help`.

### 7. Top-level `spine --help` tautological text

**Before:** "Run `spine --help` to see all commands." — self-referential, no
value.

**After:** "First time? Run `spine init` to bootstrap .spine/ governance state,
then `spine doctor` to verify, and `spine mission show` to see your active
mission." — provides a clear first-run path.

### 8. SPINE repo's own AGENTS.md and CLAUDE.md (stale)

Updated the SPINE development repo's own `AGENTS.md` and `CLAUDE.md` to match
the new templates — same stale "Phase 1 only" content was present here too.

---

## Files Changed

| File | Change |
|------|--------|
| `src/spine/services/init_service.py` | Updated `_AGENTS_MD_CONTENT` and `_CLAUDE_MD_CONTENT` templates |
| `src/spine/cli/init_cmd.py` | Improved next-steps panel; unhid `--cwd` option |
| `src/spine/services/doctor_service.py` | Fixed absolute-path bug; improved `.spine/` missing message |
| `src/spine/services/mission_service.py` | Context-aware `MissionNotFoundError` with relative paths |
| `src/spine/cli/app.py` | Updated top-level `--help` text |
| `AGENTS.md` | Updated from stale Phase 1 content to Phase 3A |
| `CLAUDE.md` | Updated from stale Phase 1 content to Phase 3A |
| `tests/test_init.py` | Updated stale assertion; added 5 new focused tests |
| `tests/test_doctor.py` | Added 3 new focused tests for error quality |
| `docs/SPINE_STATUS.md` | Updated #18 status to Done |
| `docs/SPINE_FEATURE_BACKLOG.md` | Updated #18 entry |
| `docs/SPINE_PHASE3A_IMPLEMENTATION_REPORT.md` | This file (created) |

---

## Test Results

- **Focused tests added:** 8 (5 in `test_init.py`, 3 in `test_doctor.py`)
- **Full suite:** 213/213 passing
- **No regressions**

New tests cover:
- `spine init` output mentions `spine doctor` as verification step
- `spine init` output mentions `git commit` guidance
- `spine init` output does not show stale "SPINE Phase 1" title
- Generated `AGENTS.md` lists all key governance commands
- `--cwd` option is visible in `spine init --help`
- Doctor `.spine/` missing error mentions `spine init`
- Doctor contract error file column is relative, not absolute
- Doctor contract error message is actionable (mentions `spine init`)

---

## What Was Explicitly Deferred

| Item | Deferred to |
|------|-------------|
| Artifact naming / stable artifact references | #22 |
| External-repo docs/examples as a docs package | #23 |
| Validation matrix / alpha-exit verification gate | #24 |
| New JSON families or exit-code redesign | Out of scope |
| Branch-local governance lanes | Future |
| PR-prep or handoff commands | Future |
| Auto-drafting governance records | Explicitly rejected (hidden automation) |
| Broad docs rewrite | Deferred |

---

## SPINE Commands Run

```
uv run spine mission show
uv run spine doctor
uv run spine decision add ...
uv run spine evidence add ...
uv run spine review weekly --recommendation continue --notes "Phase 3A issue #18: ..."
```
