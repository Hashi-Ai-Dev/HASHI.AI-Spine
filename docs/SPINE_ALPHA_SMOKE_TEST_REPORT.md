# SPINE v0.1.1-alpha Smoke Test Report

**Date:** 2026-04-06
**Branch:** `prep/v0.1.1-alpha`
**Environment:** Windows 11, Python 3.12.9, uv

---

## Smoke Test Setup

1. Created fresh temp git repo: `/tmp/smoke-test-repo/`
2. Initialized with `git init --initial-branch=main` and a `README.md`
3. Ran all SPINE commands from the SPINE repo with `SPINE_ROOT` targeting the external temp repo

---

## Commands Run and Results

### `uv sync`
Not run separately (dependency install is implicit in `uv run`). Assumed clean.

### `uv run spine --help`
**Result:** PASS
```
SPINE — local-first, repo-native mission governor.
Commands: init, brief, doctor, mission, opportunity, evidence, decision, drift, review
```

### `uv run spine init --cwd /tmp/smoke-test-repo`
**Result:** PASS
- All 17 files created correctly (mission.yaml, constraints.yaml, JSONL logs, AGENTS.md, CLAUDE.md, etc.)
- No errors

### `spine mission show` (on external repo via SPINE_ROOT)
**Result:** PASS
- Displayed mission-0001 with all fields
- `repo:` and `branch:` context shown

### `spine mission set --title "Smoke test mission" --status active`
**Result:** PASS
- Mission updated to "Smoke test mission", status active
- Confirmation output correct

### `spine brief --target claude`
**Result:** PASS
- Canonical brief created at `.spine/briefs/claude/20260406_233939.md`
- `latest.md` alias updated
- Output shows both paths

### `spine doctor` (on external repo)
**Result:** PASS
```
repo: /tmp/smoke-test-repo  branch: main
All checks passed.
SPINE state is valid and compliant.
```

### `spine drift scan`
**Result:** PASS
- "No drift detected." (clean repo, no changes)
- Correct — no drift to report

### `spine review weekly --recommendation continue --notes "Smoke test"`
**Result:** PASS
- Canonical review: `.spine/reviews/2026-04-06.md`
- `latest.md` alias updated
- Both paths shown in output

### `spine mission show --json`
**Result:** PASS
- Valid JSON with all mission fields
- `"title": "Smoke test mission"`, `"status": "active"`

### `spine doctor --json`
**Result:** PASS
```json
{
  "passed": true,
  "repo": "C:\\Users\\ZeusPR\\AppData\\Local\\Temp\\smoke-test-repo",
  "branch": "main",
  "checked_at": "2026-04-06T23:42:30.139607+00:00",
  "error_count": 0,
  "warning_count": 0,
  "issues": []
}
```

### `spine review weekly --json --recommendation continue`
**Result:** PASS
```json
{
  "canonical_path": "C:\\Users\\ZeusPR\\AppData\\Local\\Temp\\smoke-test-repo\\.spine\\reviews\\2026-04-06.md",
  "latest_path": "...\\.spine\\reviews\\latest.md",
  "recommendation": "continue",
  "period_days": 7,
  "mission_title": "Smoke test mission",
  "mission_status": "active",
  "evidence_count": 0,
  "decisions_count": 0,
  "drift_count": 0
}
```

---

## External Targeting Smoke Test

Using `SPINE_ROOT=/tmp/smoke-test-repo`:
- All Phase 2 commands correctly targeted the external temp repo
- No SPINE repo files appeared in external target's `.spine/` or drift results
- Branch context (`main`) correctly detected in external repo
- Confirms the `resolve_roots()` fix is working

---

## Overall Smoke Test Result: PASS

All 11 smoke test commands passed. SPINE is usable from a clean starting point on a separate repo with external targeting. No regressions detected.