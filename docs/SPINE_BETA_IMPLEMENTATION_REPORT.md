# SPINE Beta Implementation Report

---

## Issue #58 — README Exit Code Contract Fix

**Date:** 2026-04-09
**Branch:** `beta/bug58-readme-exit-code-contract`
**Issue targeted:** #58 — [BUG] README exit code table implies code 2 is git-not-found for all commands — only init defines it

---

### Summary

Corrects two public-facing contract errors in `README.md` and fixes stale test
count. No CLI behavior was changed. Option A (docs-only fix) applied as
recommended.

---

### Audit Findings

**Exit code audit:**

| Command module | Code for git-not-found | Code for missing .spine/ |
|---|---|---|
| `init_cmd.py` | 2 (`_EXIT_GIT_NOT_FOUND = 2`, local) | N/A |
| All other commands | 2 (`EXIT_CONTEXT = 2`, from `app.py`) | 2 (`EXIT_CONTEXT = 2`) |

All commands use `EXIT_CONTEXT = 2` from `app.py` for context failures. The
issue description's claim that "other commands exit 1 for git-not-found" was
incorrect. The README description of code 2 was broadly accurate.

**What was actually wrong in the README:**
1. Exit code `3` (`spine init` conflict — target files already exist) was not
   documented at all.
2. The code 2 row did not clarify that `--allow-no-git` is a `spine init`-only
   flag.
3. Test count was stale: "300+ passing (15 test files)" vs actual 505 tests in
   23 test files.

---

### Changes Made

| File | Change |
|---|---|
| `README.md` | Exit code table: added code 3 (init conflict), clarified code 2 with `--allow-no-git` note |
| `README.md` | Validation section: fixed test count "300+ passing (15 files)" → "505 passing (23 test files)" |
| `docs/SPINE_STATUS.md` | Narrow update — #58 marked fixed, blocker count 3 → 2 |
| `docs/SPINE_FEATURE_BACKLOG.md` | Narrow update — #58 marked fixed |
| `docs/SPINE_BETA_IMPLEMENTATION_REPORT.md` | This section |

---

### Test Results

```
505 passed (23 test files)
0 failures
```

No new tests were needed — this was a pure docs contract fix. Existing exit
code contract tests in `tests/test_fixture_contracts.py` already cover all
scenarios including exit code 2 (init no-git, mission show no-.spine/, etc.)
and exit code 3 (init already initialized).

---

### SPINE Governance

- `spine decision add` — recorded rationale for Issue #58
- `spine evidence add` — logged implementation work
- `spine review weekly --recommendation continue --notes "Pre-beta-exit bugfix: Issue #58 README exit-code contract"`

---

### What Was Explicitly Deferred

| Item | Issue | Status |
|---|---|---|
| Consistent exit code 2 across all commands for git-not-found | #58 Option B | Deferred — all commands already correctly emit exit 2; no code change needed |
| `drift scan --json` | #59 | Out of scope for this PR |
| SPINE_SECURITY_BASELINE.md wrong repo name | #60 | Out of scope for this PR |
| Beta-exit proof/validation | #51 | Out of scope for this PR |

---

## Issue #38 — Deterministic Validation Fixtures and Contract Harness

**Date:** 2026-04-08
**Branch:** `claude/issue38-validation-fixtures-VwFXQ`
**Issue targeted:** #38 — Beta: deterministic validation fixtures and contract harness

---

### Summary

Adds `tests/fixtures/` — a layer of explicit, human-readable fixtures and a
focused harness (`tests/test_fixture_contracts.py`) that validates SPINE's core
contracts deterministically.  No new features, no framework rewrite, no runtime
services.  Pure local pytest, compatible with CI.

---

### Fixture/Harness Design Chosen

**Static fixture files + shape-validation harness.**

- `tests/fixtures/*.yaml` / `*.json` — human-readable, version-controlled
  specifications of expected SPINE file formats and output shapes
- `tests/fixtures/json_shapes/*.json` — per-command JSON output shape contracts
  (required keys + expected types)
- `tests/test_fixture_contracts.py` — loads fixtures and validates them against
  live commands or Pydantic models; 6 test classes, 58 tests

Rationale:
- Explicit and readable — fixtures are self-documenting
- Low maintenance — shapes rarely change; tests fail loudly when they do
- No magic — no snapshot sprawl, no opaque diff format
- Deterministic in CI — pure Python, no network, no runtime services
- Extendable — adding a new contract requires one fixture file + one test

---

### Contracts Now Covered

| Contract Surface | Coverage |
|---|---|
| `mission.yaml` structure | Pydantic round-trip on both `mission_valid.yaml` and `mission_minimal.yaml` fixtures; all model fields present |
| `artifact_manifest.json` structure | Required keys, relative paths, both briefs and reviews sections |
| `spine doctor --json` shape | `passed`, `error_count`, `warning_count`, `issues` keys verified |
| `spine check before-pr --json` shape | `result`, `passed`, `checks` keys; each check item has `name`, `status`, `message` |
| `spine mission show --json` shape | `id`, `title`, `status`, `one_sentence_promise`, `success_metric` keys |
| `spine review handoff --json` shape | `mission`, `recent_decisions`, `recent_evidence`, `drift_records`, `totals` keys |
| `spine brief --json` shape | `canonical_path`, `latest_path` keys |
| `spine drift scan --json` shape | `clean`, `event_count`, `severity_summary` keys |
| Exit code contracts | 7 core scenarios: init (new/re-init/force/no-git), mission show (valid/.spine-missing), mission set (invalid enum), doctor (valid/no-.spine/), check before-pr (pass/no-.spine/), brief (valid/invalid-target/.spine-missing), review weekly, drift scan |
| `--cwd` external-repo targeting | 5 scenarios: valid repo, uninitialized repo, non-git dir, repo isolation (2 repos), all-commands acceptance |

---

### Files Changed

| File | Change |
|---|---|
| `tests/fixtures/mission_valid.yaml` | New: complete valid mission fixture |
| `tests/fixtures/mission_minimal.yaml` | New: minimal valid mission fixture |
| `tests/fixtures/artifact_manifest_full.json` | New: full manifest fixture (briefs + reviews) |
| `tests/fixtures/artifact_manifest_minimal.json` | New: minimal manifest fixture |
| `tests/fixtures/exit_codes.json` | New: exit code contract reference (all scenarios) |
| `tests/fixtures/json_shapes/doctor.json` | New: doctor --json output shape |
| `tests/fixtures/json_shapes/check_before_pr.json` | New: check before-pr --json output shape |
| `tests/fixtures/json_shapes/mission_show.json` | New: mission show --json output shape |
| `tests/fixtures/json_shapes/review_handoff.json` | New: review handoff --json output shape |
| `tests/fixtures/json_shapes/brief.json` | New: brief --json output shape |
| `tests/fixtures/json_shapes/drift_scan.json` | New: drift scan --json output shape |
| `tests/test_fixture_contracts.py` | New: 58-test fixture contract harness |
| `docs/SPINE_STATUS.md` | Narrow update — #38 marked done |
| `docs/SPINE_FEATURE_BACKLOG.md` | Narrow update — #38 marked done |
| `docs/SPINE_BETA_IMPLEMENTATION_REPORT.md` | This file (updated) |

---

### Test Results

```
58 focused tests added (tests/test_fixture_contracts.py)
436 total tests pass
0 failures
```

Focused tests cover:
- Fixture file integrity (all files parse, required keys present)
- mission.yaml Pydantic round-trip (valid + minimal fixtures)
- mission_valid.yaml has all MissionModel fields
- artifact_manifest full fixture has contract_version, relative paths, required keys
- artifact_manifest minimal fixture structure
- Live brief/review manifest matches fixture shape
- JSON output shape for: doctor, check before-pr, mission show, review handoff, brief, drift scan
- check before-pr checks[] items have name/status/message
- review handoff totals keys
- Exit code 0: init (new), init --force, mission show (valid), check before-pr (with evidence+decisions), brief (valid), review weekly, drift scan
- Exit code 1: mission set (invalid enum), doctor (no .spine/), check before-pr (no .spine/), brief (invalid target)
- Exit code 2: init (no git), mission show (no .spine/), brief (no .spine/), review weekly (no git), drift scan (no git)
- Exit code 3: init (already initialized)
- --cwd points to valid repo succeeds from different cwd
- --cwd to uninitialized repo exits 2
- --cwd to non-git dir exits 2
- Two repos initialized with --cwd remain isolated
- All 7 core commands accept --cwd on a valid repo

---

### SPINE Governance

- `spine decision add` — recorded rationale for Issue #38
- `spine evidence add` — logged implementation work (58 tests, 436 total passing)
- `spine review weekly --recommendation continue` — weekly review generated

---

### What Was Explicitly Deferred

| Item | Issue | Status |
|---|---|---|
| Concurrent command safety | — | Not in scope for fixture harness |
| Large file/repo performance | — | Not in scope for fixture harness |
| Hook execution in real git workflow | — | Smoke tested in existing test_hooks.py |
| Generalized snapshot testing | — | Explicitly excluded per Issue #38 |
| JSONL atomicity/corruption recovery | — | Not in scope |
| Beta-exit proof/reporting | — | Later work |

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

---

## Issue #49 — Write-Flow Machine-Readable Consistency

**Date:** 2026-04-08
**Branch:** `beta/issue49-write-flow-machine-readable-consistency`
**Issue targeted:** #49 — Beta: machine-readable consistency for governance write flows

---

### Summary

Audited all write-oriented CLI commands for JSON output consistency.
Added `--json` flag to 7 write-oriented commands with deterministic,
stable output shapes. Exit code contracts unchanged. No hidden behavior added.

---

### Audit Results

| Command | Pre-#49 JSON | Gap Found | Action |
|---|---|---|---|
| `spine evidence add` | None | Yes — agents need machine-readable write confirmation | Added `--json` |
| `spine decision add` | None | Yes — agents need machine-readable write confirmation | Added `--json` |
| `spine drafts list` | None | Yes — list surface should be machine-readable | Added `--json` |
| `spine drafts confirm` | None | Yes — confirm surface should be machine-readable | Added `--json` |
| `spine mission refine` | None | Yes — draft creation needs stable output for agent use | Added `--json` |
| `spine mission confirm` | None | Yes — draft promotion needs stable output | Added `--json` |
| `spine mission drafts` | None | Yes — list surface should be machine-readable | Added `--json` |
| Exit codes (all write cmds) | Already consistent | No gap | No change needed |
| `--cwd` support | Already consistent | No gap | No change needed |

---

### JSON Output Shapes

All write commands follow the established SPINE pattern from `mission show` / `brief`:
- Success: `{"ok": true, ...record_fields...}`
- Draft mode: `{"ok": true, "draft": true, "draft_id": "...", ...record_fields...}`
- Error: `{"error": "...", "exit_code": N}`

Specific shapes:

**`spine evidence add --json`**
```json
{"ok": true, "kind": "commit", "description": "...", "evidence_url": "...", "created_at": "..."}
```

**`spine evidence add --draft --json`**
```json
{"ok": true, "draft": true, "draft_id": "evidence-20260408T...", "kind": "commit", ...}
```

**`spine decision add --json`**
```json
{"ok": true, "title": "...", "why": "...", "decision": "...", "alternatives": [...], "created_at": "..."}
```

**`spine drafts list --json`**
```json
{"ok": true, "count": 1, "drafts": [{"draft_id": "...", "_record_type": "evidence", ...}]}
```

**`spine drafts confirm <id> --json`**
```json
{"ok": true, "draft_id": "...", "record_type": "evidence", "kind": "...", "description": "..."}
```

**`spine mission refine --json`**
```json
{"ok": true, "draft_id": "mission-...", "draft_path": ".spine/drafts/missions/...", "title": "...", ...}
```

**`spine mission confirm <id> --json`**
```json
{"ok": true, "draft_id": "...", "title": "...", "status": "...", "updated_at": "..."}
```

**`spine mission drafts --json`**
```json
{"ok": true, "count": 1, "drafts": [{"draft_id": "...", "title": "...", "status": "..."}]}
```

---

### Files Changed

| File | Change |
|---|---|
| `src/spine/cli/evidence_cmd.py` | Added `--json` option; JSON success/error output; updated docstring with exit codes |
| `src/spine/cli/decision_cmd.py` | Added `--json` option; JSON success/error output; updated docstring with exit codes |
| `src/spine/cli/drafts_cmd.py` | Added `--json` to both `list` and `confirm`; JSON output on all paths |
| `src/spine/cli/mission_cmd.py` | Added `--json` to `refine`, `confirm`, `drafts` subcommands |
| `tests/test_write_flow_json.py` | New: 37 focused contract tests for all write-flow JSON surfaces |
| `docs/SPINE_STATUS.md` | Narrow update — #49 marked done |
| `docs/SPINE_FEATURE_BACKLOG.md` | Narrow update — #49 marked done, #50/#51 added as deferred |
| `docs/SPINE_BETA_IMPLEMENTATION_REPORT.md` | This section |

---

### Test Results

```
37 new focused contract tests (tests/test_write_flow_json.py)
473 total tests pass
0 failures
```

Focused tests cover:
- `evidence add --json`: success shape, draft shape, url field, context failure, stdout purity
- `decision add --json`: success shape, draft shape, alternatives field, validation failure, context failure, stdout purity
- `drafts list --json`: empty shape, with evidence draft, with decision draft, context failure, stdout purity
- `drafts confirm --json`: evidence success, decision success, not-found exits 1, context failure, canonical promotion verified
- `mission refine --json`: success shape, stdout purity, context failure
- `mission confirm --json`: success shape (with round-trip), not-found exits 1, context failure
- `mission drafts --json`: empty shape, with draft, context failure, stdout purity
- Exit code contract: evidence add 0/2, decision add 0/1, drafts list 2, drafts confirm 1

---

### SPINE Governance

- `spine decision add` — recorded rationale for Issue #49
- `spine evidence add` — logged implementation work
- `spine review weekly --recommendation continue` — weekly review generated

---

### What Was Explicitly Deferred

| Item | Issue | Reason |
|---|---|---|
| Before-work / start-session checkpoint | #50 | Out of scope for #49 |
| Beta-exit repeated-use proof | #51 | Out of scope for #49 |
| New governance command surfaces | — | Not in scope — write-path consistency only |
| General snapshot testing overhaul | — | Explicitly excluded |
| Cloud/webhook/platform features | — | Explicitly excluded |

---

## Issue #50 — Before-Work / Start-Session Governance Checkpoint

**Date:** 2026-04-08
**Branch:** `claude/issue-50-checkpoint-2Aq80`
**Issue targeted:** #50 — Beta: before-work / start-session governance checkpoint

---

### Summary

Adds `spine check before-work` — a bounded pre-work/start-session checkpoint
that helps operators and agents start work with better context and fewer missed
governance steps. No hidden state, no daemon behavior, no session tracking.

---

### Checkpoint Behavior Chosen

**`spine check before-work`** — added as a subcommand under the existing
`spine check` surface, parallel to `before-pr`.

**Checks (in order):**

| Check | Behavior | Fail → |
|---|---|---|
| `spine_dir` | .spine/ directory present | fail → exit 1, stop |
| `mission` | mission.yaml present and readable | fail → exit 1 |
| `doctor` | repo health (errors only; warnings advisory) | error → fail; warning → pass |
| `branch_context` | current branch/repo context | always pass — informational |
| `recent_brief` | brief files present in .spine/briefs/ | no briefs → warn → exit 1 |

**Key design choice:** `before-work` does NOT check for evidence, decisions, or
drift — those are `before-pr`'s concern. The start-session check answers "can I
responsibly begin work here?" not "have I done enough governance for a PR?"

---

### Output and Exit Behavior

- Human-readable table (same style as `before-pr`)
- `--json` flag for machine-readable output (same shape as `before-pr` JSON)
- `--cwd` flag for targeting external repos

**Exit codes:**
- `0` — all checks passed — clear to begin work
- `1` — review recommended — one or more checks need attention
- `2` — context failure — cannot resolve repo or .spine/ root

Does NOT mutate state. No hidden logging. No background behavior.

---

### Files Changed

| File | Change |
|---|---|
| `src/spine/services/check_service.py` | Added `BeforeWorkResult` dataclass; added `run_before_work()` method; added `_check_branch_context()` and `_check_recent_brief()` private check methods |
| `src/spine/cli/check_cmd.py` | Added `check_before_work` subcommand with `--cwd`/`--json`; added `_output_before_work_json()` and `_output_before_work_human()` formatters; imported `BeforeWorkResult` |
| `tests/test_check_before_work.py` | New: 28 focused tests |
| `docs/SPINE_STATUS.md` | Narrow update — #50 marked done, next priority updated |
| `docs/SPINE_FEATURE_BACKLOG.md` | Narrow update — #50 marked done, #51 added |
| `docs/SPINE_BETA_IMPLEMENTATION_REPORT.md` | This section |

---

### Test Results

```
28 focused tests added (tests/test_check_before_work.py)
501 total tests pass
0 failures
```

Focused tests cover:
- Command registration (before-work in check --help)
- Help text (--cwd, --json, exit codes documented)
- Pass path: all checks pass with brief present
- Pass path: all expected check names in output
- Pass path: branch_context shown in output
- Review-recommended: .spine/ missing → exit 1
- Review-recommended: mission.yaml missing → exit 1
- Review-recommended: mission.yaml corrupt → exit 1
- Review-recommended: no briefs → exit 1
- Review-recommended: briefs dir empty (no .md files) → exit 1
- No-brief message contains actionable suggestion
- Context failure: non-git dir → exit 2
- --cwd support without process chdir
- --cwd invalid path → exit 2
- JSON output structure (all required keys)
- JSON output includes all 5 check names
- JSON exit codes match result field
- JSON context failure emits error JSON
- Deterministic: same result twice
- No state mutation (.spine/ unchanged after run)
- Human output includes repo path
- Human output includes final Result line
- Doctor warnings do NOT cause exit 1 (advisory only)
- Doctor errors DO cause exit 1
- No evidence required (before-work isolation from before-pr)
- No decisions required (before-work isolation from before-pr)
- Drift events do NOT block before-work

---

### SPINE Governance

- `spine decision add` — recorded rationale for Issue #50
- `spine evidence add` — logged implementation work (28 tests, 501 total passing)
- `spine review weekly --recommendation continue --notes "Beta issue #50: before-work / start-session governance checkpoint"`

---

### What Was Explicitly Deferred

| Item | Issue | Status |
|---|---|---|
| Beta-exit proof/validation | #51 | Not started — explicitly out of scope |
| Session state tracking / session management | — | Explicitly excluded |
| Background reminders / daemon behavior | — | Explicitly excluded |
| Hook installation redesign | — | Explicitly excluded |
| Notifications, dashboards, webhooks | — | Explicitly excluded |
| Broad `check` system redesign | — | Explicitly excluded |
