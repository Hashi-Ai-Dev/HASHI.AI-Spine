# SPINE Phase 3A Internal Dogfood Report

**Date:** 2026-04-06  
**Branch:** `claude/dogfood-phase3a-polish-zHDuu`  
**Scope:** Internal SPINE-repo-only dogfood slice. Not external validation. Not Phase 3 completion.

---

## 1. Branch Used

`claude/dogfood-phase3a-polish-zHDuu`

This is an internal dogfood branch only. It is not automatically for merge. External validation is being handled on a separate lane.

---

## 2. Chosen Implementation Slice

**Primary:** README polish + `docs/SPINE_STATUS.md`  
**Adjacent code slice:** `--json` for `spine mission show` + repo/branch context header in `spine doctor`

This slice was chosen because:
- README was entirely out of date (documented Phase 1 only while Phase 2 was fully implemented) — high friction, zero risk to fix
- `SPINE_STATUS.md` was required by the dogfood spec and provides operator orientation
- `--json` on `mission show` is the lowest-risk, highest-CI-value code change
- Context header on `doctor` is narrow, additive, and directly improves operator trust per Phase 3A spec §4.2

One adjacent slice deliberately deferred: `--json` on `spine doctor` itself. It would require more structural work to normalize the issues list into a clean schema, and is a lower-priority addition at this stage.

---

## 3. What Changed

### `README.md`
- Replaced Phase-1-only docs with full Phase 2 command surface
- Added concrete CLI examples for every command group
- Added State files table explaining all `.spine/` artifacts
- Added Design principles section
- Added `spine doctor` to the quickstart flow (missing before)

### `docs/SPINE_STATUS.md` (new)
- Created live status tracker per dogfood spec requirements
- Covers: completed milestones, current blocker, release gate, next 3 moves
- Notes that external validation is separate and this branch is internal only

### `src/spine/cli/mission_cmd.py`
- Added `--json` flag to `spine mission show`
- When passed, outputs `mission.model_dump()` as indented JSON via `print()` (bypasses Rich, suitable for `jq` and CI piping)
- Human-readable table output unchanged when `--json` is not passed

### `src/spine/cli/doctor_cmd.py`
- Added one-line context header before check results: `repo: <path>  branch: <name>`
- Uses `get_current_branch()` utility; works with detached HEAD and when git is unavailable (graceful fallback strings)

### `src/spine/utils/paths.py`
- Added `get_current_branch(repo_root)` utility function
- Returns branch name, `(detached:<sha>)`, or `(git unavailable)` — no exceptions leak

### `tests/test_mission.py`
- Added `test_mission_show_json_output` — validates `--json` flag produces parseable JSON with all expected fields

---

## 4. What Was Improved

| Area | Before | After |
|------|--------|-------|
| README | Described Phase 1 only (`spine init`). Phase 2 surface invisible to new operators. | Full command surface documented with examples. |
| Project status | No status doc. Unclear where Phase 3A stood. | `docs/SPINE_STATUS.md` gives clear milestone table, blockers, next moves. |
| `mission show` | Human-readable table only. Unusable in CI or scripting. | `--json` flag enables `spine mission show --json \| jq .status` patterns. |
| `spine doctor` output | No context — operator didn't know which repo or branch was being checked. | Context header: `repo: /path  branch: name` printed before results. |

---

## 5. What Felt Better

- `spine mission show --json | jq .status` works immediately and cleanly.
- `spine doctor` context line (repo + branch) feels immediately more trustworthy — you know at a glance which repo and branch is being validated.
- README now reflects reality — a new operator reading it will understand Phase 2 exists.
- `SPINE_STATUS.md` provides a single-file orientation point that doesn't require reading the full spec.

---

## 6. What Still Feels Clunky

- **`spine doctor` does not have `--json`** — issues list is still Rich-formatted only. A CI script cannot reliably parse exit code alone if it needs to distinguish error vs warning. This should be the next narrow code slice.
- **`spine drift scan` has no context header** — symmetry with `doctor` would help. The drift scan is where repo/branch confusion is highest risk (you want to know which base branch was used).
- **Drift test failures are pre-existing (4 tests)** — `test_drift_scan_staged_forbidden_file_detected` and related tests fail on this repo because the staging environment in tests doesn't work as expected. These failures predate this branch and are not introduced here, but they need to be diagnosed and fixed before Phase 3A can be considered clean.
- **`mission show` could show the file path** — knowing which `.spine/mission.yaml` was read would reduce targeting confusion, especially with `SPINE_ROOT` overrides.
- **README quickstart flow** still points to a blank-slate mission after `spine init`. A brief note about using `spine mission set` to actually populate the mission would reduce new-operator confusion.

---

## 7. Whether This Branch Is Merge-Worthy

**Assessment: Yes, conditionally merge-worthy.**

If the external-validation lane succeeds cleanly, this branch is worth reviewing for merge because:
- All changes are additive and backward-compatible
- No public CLI contract was broken
- No speculative architecture was introduced
- The README fix is urgently needed regardless of Phase 3A status
- `SPINE_STATUS.md` is useful project hygiene
- `--json` on `mission show` is clean and narrow
- The `doctor` context header is non-breaking and directly useful

This branch should **not** be merged before external validation succeeds — it is exploratory and reference quality only as stated in the branch purpose.

---

## 8. What Should Still Wait for External Validation

- `--json` on `spine doctor` (needs schema design for the issues list)
- `--json` on `spine drift scan` (same concern)
- `--against` default-branch visibility improvements
- Stable artifact naming (briefs/reviews as `current.md` aliases)
- Any external repo targeting changes
- Fix of the 4 pre-existing drift test failures (investigation needed, not a quick patch)
- Bootstrap/quickstart improvement for zero-context operators in non-SPINE repos
- Operator docs and examples for external repo usage

---

## 9. Actual Dogfood Loop — Commands Run and Observed Output

All commands run on the live SPINE repo (`/home/user/HASHI.AI-Spine`) on branch `claude/dogfood-phase3a-polish-zHDuu`.

### `uv run spine mission show`
```
                        Mission
 id                    mission-0001
 title                 Define active mission
 status                active
 ...
```
Output unchanged from before. Table format readable. No regression.

### `uv run spine mission show --json` (new)
```json
{
  "version": 1,
  "id": "mission-0001",
  "title": "Define active mission",
  "status": "active",
  ...
}
```
Immediately pipeable. `spine mission show --json | jq .status` returns `"active"` with no extra parsing. Materially better for CI use.

### `uv run spine doctor` (with new context header)
```
repo: /home/user/HASHI.AI-Spine  branch: claude/dogfood-phase3a-polish-zHDuu
                                 Doctor Issues
 Severity  File            Message
 WARNING   .spine/reviews  Subdirectory does not exist (will be created as needed)
 WARNING   .spine/briefs   Subdirectory does not exist (will be created as needed)
 WARNING   .spine/skills   Subdirectory does not exist (will be created as needed)
 WARNING   .spine/checks   Subdirectory does not exist (will be created as needed)

Doctor check passed with warnings.
```
Context header immediately visible. Knowing the branch is `claude/dogfood-phase3a-polish-zHDuu` (not `main`) is directly reassuring — you know doctor is running on the right branch.

### `uv run spine review weekly --recommendation continue --notes "..."`
```
Weekly review generated: /home/user/HASHI.AI-Spine/.spine/reviews/2026-04-06.md
```
Works cleanly. No regressions.

### `uv run spine brief --target claude`
```
Brief generated: /home/user/HASHI.AI-Spine/.spine/briefs/claude/20260406_163836.md
```
Works cleanly. Artifact generated successfully.

### Evaluation

The slice made SPINE materially better in actual usage:
- `--json` on `mission show` is immediately useful for scripting. Zero friction.
- The `doctor` context line removes a small but real source of ambiguity. When you're on a dogfood branch checking governance state, seeing the branch name is grounding.
- No regressions observed in any command.

---

## 10. Test Results

```
4 failed (pre-existing, in test_drift.py — unrelated to this branch's changes)
118 passed
```

All tests added by this branch pass. The 4 drift failures were confirmed pre-existing by stashing all changes and running the drift test suite independently — same 4 failures reproduced.
