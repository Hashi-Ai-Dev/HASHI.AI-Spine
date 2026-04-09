# SPINE Feature Backlog

Grouped by target milestone. Each item: title, short description, why it matters, status.

---

## v0.1.2 — Stabilization

### ✅ Add `--cwd` support to Phase 2 commands
**Status:** DONE — PR #11

### ✅ Add minimal CI pipeline
**Status:** DONE — PR #12

### ✅ Clarify onboarding / quickstart docs
**Status:** DONE — PR #13

---

## Alpha Exit — v0.2.0-beta (Released 2026-04-07)

### ✅ All Phase 3A items (#15–#18, #23–#25)
**Status:** DONE — PRs #19–#29

---

## Beta — v0.2.0-beta

> ✅ Beta blocker stabilization complete (PR #46). Beta core queue complete. Beta polish active.

### Completed Beta Issues

| # | Issue | PR |
|---|---|---|
| #31 | `spine check before-pr` preflight checkpoint | PR #35 |
| #32 | Handoff/PR-prep summary primitive | PR #39 |
| #33 | Draftable governance records | PR #40 |
| #34 | Local optional hook/checkpoint integration | PR #41 |
| #36 | Mission refine draft flow | PR #47 |
| #37 | Compatibility/integration guide | PR #48 |
| #38 | Deterministic validation fixtures | PR #52 |
| #43 | `check before-pr` exit 1 on healthy repos | PR #46 |
| #44 | Hook script missing `uv run` | PR #46 |
| #45 | AGENTS.md template invalid commands | PR #46 |
| #49 | Write-flow machine-readable consistency | PR #53 |
| #50 | Before-work / start-session governance checkpoint | PR #54 |

### Beta Polish Queue

| # | Issue | Status |
|---|---|---|
| #51 | Beta-exit proof/validation | 📋 Active — last Beta polish issue |

---

## ⚠️ Pre-Beta-Exit Blockers (Milestone #5)

> Beta exit blocked until these are resolved. See `docs/SPINE_STATUS.md` for full explanation.

| # | Issue | Severity | Status |
|---|---|---|---|
| #57 | MCP TextContent NameError — all tool calls crash | 🔴 Blocker | ✅ Fixed — PR #61 |
| #58 | README exit code table wrong | 🟡 High | ✅ Fixed — `beta/bug58-readme-exit-code-contract` |
| #59 | `drift scan --json` missing | 🟡 Medium | Open |
| #60 | SPINE_SECURITY_BASELINE.md wrong repo name | 🟡 Medium | Open |

---

## Phase 3B Candidates

### 🟡 Stronger local tool-consumption surfaces
**Status:** CANDIDATE — Phase 3B

### 🟡 Optional governance profiles
**Status:** CANDIDATE — Phase 3B, optional

### 🚫 HUD / live observability mode
**Status:** REJECTED

### 🚫 Notification / webhook systems
**Status:** REJECTED

---

*Last updated: 2026-04-09 — Issue #58 fixed (README exit-code contract + stale test count)*
