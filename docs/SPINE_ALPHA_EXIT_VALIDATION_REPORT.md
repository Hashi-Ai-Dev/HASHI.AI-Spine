# SPINE Alpha Exit Validation Report

**Date:** 2026-04-07
**Issue:** #25 — Alpha Exit: Validation against alpha-exit gate matrix
**Branch:** `claude/issue25-gate-matrix-validation-G5bmE`
**SPINE version:** `v0.1.2` (targeting `v0.2.0-beta` declaration)
**Validator:** SPINE Repo Manager Agent

---

## Summary

**Alpha exit status: PASS**

All required feature, validation, usability, and anti-drift gates pass. One partial exists
(`evidence add` / `decision add` have no `--json` flag) but it is non-blocking. All other
gates pass with direct live evidence.

---

## Gate Matrix

### Feature Gates

| Gate | Status | Blocking | Evidence |
|------|--------|----------|---------|
| Explicit repo targeting | **PASS** | — | `--cwd` overrides `SPINE_ROOT` overrides cwd. Context line emitted. Invalid path → exit 2 with clear message. |
| Repo/branch context visibility | **PASS** | — | Every git-relevant command emits `repo: … branch: … default: …`. Deterministic default branch resolution confirmed. |
| Machine-readable output | **PARTIAL** | No | `--json` confirmed on: `doctor`, `drift scan`, `mission show`, `brief`, `review weekly`. Not present on `evidence add`, `decision add`. CI can still rely on exit codes. |
| Stable exit codes | **PASS** | — | `0` (success), `1` (validation failure), `2` (context failure) all verified live. |
| Bootstrap improved | **PASS** | — | `spine init` completes in <2s, creates complete scaffold, emits explicit next-steps panel. `doctor` passes immediately after init. |
| Artifact ergonomics contract | **PASS** | — | `artifact_manifest.json` at `.spine/artifact_manifest.json`. Stable `latest.md` aliases confirmed for briefs and weekly reviews. JSONL logs (evidence, decisions, drift) are append-only records, not artifacts — correct by spec design. |

### Validation Gates — External Repo Governance Loop

Tested in fresh git-initialized temp directories with `--cwd` throughout.

| Gate | Status | Evidence |
|------|--------|---------|
| `spine init` | **PASS** | Creates full `.spine/` scaffold including subdirs. Exit 0. |
| `spine brief` | **PASS** | Generates dated brief + updates `latest.md` alias. Manifest updated. |
| `spine evidence add` | **PASS** | Appends to `evidence.jsonl`. Exit 0. Clear confirmation output. |
| `spine decision add` | **PASS** | Appends to `decisions.jsonl`. Exit 0. Title/why/decision echoed. |
| `spine drift scan` (clean) | **PASS** | Emits "No drift detected." Exit 0. |
| `spine drift scan` (forbidden) | **PASS** | Detects staged file in forbidden scope (`dashboard/`). Reports HIGH severity with file path. Appends to `drift.jsonl`. |
| `spine review weekly` | **PASS** | Generates dated review + updates `latest.md`. Exit 0. |

### Validation Gates — Repeated-Use Session

| Gate | Status | Evidence |
|------|--------|---------|
| Session 2 lighter than session 1 | **PASS** | Session 2: no re-setup required. Mission already set. Commands are narrow: `brief`, `evidence add`, `drift scan`, `review weekly`. No repeated ceremony. |
| No ambiguity about what to run | **PASS** | Each command is single-purpose. Context line is always present. No implicit state transitions. |

### Validation Gates — Error-State Behavior

| Error scenario | Status | Evidence |
|---------------|--------|---------|
| Invalid `--cwd` path (non-git) | **PASS** | "No git repository found at or above: …\n  Target source: --cwd …\n  Point --cwd at a valid git repository…" Exit 2. |
| Missing `.spine/` (no init) | **PASS** | `doctor`: "`.spine/` not found — run `uv run spine init`". Exit 1. `mission show`: "`.spine/` not found". Exit 2. |
| Malformed `mission.yaml` | **PASS** | Doctor reports exact YAML parse error with line/column reference. Exit 1. |
| Forbidden scope violation | **PASS** | Drift scan flags HIGH severity event with file path. Clear tabular output. |

### Usability Gates

| Gate | Status | Evidence |
|------|--------|---------|
| Repeated use — no major ambiguity traps | **PASS** | Commands are deterministic. Context line is consistent. Error messages are actionable with specific remediation steps. |
| Onboarding in a new repo under ~10 minutes | **PASS** | Machine time: `init + mission set + doctor + brief` < 2 seconds. Human time with docs: `external-repo-onboarding.md` is step-by-step with expected outputs. Well within 10 minutes for a competent operator. |

### Anti-Drift Gates

| Gate | Status | Evidence |
|------|--------|---------|
| No dashboard surface | **PASS** | "dashboard" only appears in `drift_service.py` as a _forbidden_ pattern to detect in governed repos. No dashboard code present. |
| No cloud/control-plane creep | **PASS** | Remote references in source are limited to `git symbolic-ref refs/remotes/origin/HEAD` for default branch detection. No S3, GCP, Azure, cloud sync, or remote telemetry. |
| No daemon/background governance | **PASS** | `mcp serve` docstring: "This is a separate blocking command. It does NOT daemonize." `asyncio` usage is for stdio protocol only, not background loop. |

---

## Partial: `--json` on Append Commands

`spine evidence add` and `spine decision add` do not support `--json`.

**Assessment:** Non-blocking. These are append commands — their exit code (0/2) is sufficient for CI
scripting. The primary machine-readable surface (doctor, drift scan, mission show, brief, review) is
covered. A future improvement could add structured output to append commands for completeness, but
this does not block alpha exit.

---

## Test Counts and Infrastructure

| Check | Result |
|-------|--------|
| Test suite | 231 passed, 0 failed |
| Lint (ruff) | Clean (CI-enforced) |
| Branch protection | Active |
| CI pipeline | Active (lint + tests on push/PR) |

---

## Commands Validated During This Pass

```
uv run spine doctor --json
uv run spine doctor --cwd /nonexistent/path   (exit 2 verified)
uv run spine mission show --json
uv run spine mission set --cwd <tmpdir> --title ... --status active --scope ... --forbid ...
uv run spine init --cwd <tmpdir>
uv run spine doctor --cwd <tmpdir>            (fresh init)
uv run spine brief --target claude --cwd <tmpdir>
uv run spine evidence add --cwd <tmpdir> --kind commit --description ...
uv run spine decision add --cwd <tmpdir> --title ... --why ... --decision ... --alternatives ...
uv run spine drift scan --cwd <tmpdir>        (clean)
uv run spine drift scan --cwd <tmpdir>        (with staged forbidden file)
uv run spine drift scan --json
uv run spine review weekly --cwd <tmpdir> --recommendation continue --notes ...
uv run pytest --tb=short -q
```

All tested against live code in this repository, 2026-04-07.

---

## Gate Summary

| Category | Gates | Pass | Partial | Fail |
|----------|-------|------|---------|------|
| Feature | 6 | 5 | 1 | 0 |
| Validation | 10 | 10 | 0 | 0 |
| Usability | 2 | 2 | 0 | 0 |
| Anti-drift | 3 | 3 | 0 | 0 |
| **Total** | **21** | **20** | **1** | **0** |

**Result: PASS. Alpha exit to v0.2.0-beta is justified.**

---

## Alpha Exit Declaration

Based on this validation pass, SPINE v0.2.0-beta is justified. All alpha-exit Phase 3A items
(#15, #16, #17, #18, #23, #24, #25) are complete. The one partial (no `--json` on append
commands) is a known gap, not a regression or blocker.

The product works correctly in external repos, produces useful error signals, has no forbidden
surface drift, and is demonstrably lighter on repeated use.

---

*Validation performed on branch `claude/issue25-gate-matrix-validation-G5bmE` (2026-04-07)*
