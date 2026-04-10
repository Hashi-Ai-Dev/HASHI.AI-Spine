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

> ✅ Beta core and polish complete. **Beta exit achieved** (2026-04-09).

### Completed Beta Issues

| # | Issue | PR |
|---|---|
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
| #57 | MCP TextContent NameError | PR #61 |
| #58 | README exit code + test count | PR #63 |
| #59 | `spine drift scan --json` | PR #67 |
| #64 | `spine evidence list` + `spine decision list` | PR #68 |
| #65 | `check before-pr --json` structured doctor detail | PR #69 |
| #66 | `check before-work` no-brief advisory | PR #70 |
| #60 | SECURITY_BASELINE wrong repo name | commit `9feb2642` |
| #51 | Beta-exit proof/validation | PR #72 |

---

## ✅ Pre-Beta-Exit Blockers — All Cleared (Milestone #5)

| # | Issue | Status |
|---|---|
| ~~#65~~ | ~~`check before-pr --json` structured doctor detail~~ | ✅ Fixed — PR #69 |
| ~~#66~~ | ~~`check before-work` no-brief advisory not exit 1~~ | ✅ Fixed — PR #70 |
| ~~#60~~ | ~~SECURITY_BASELINE wrong repo name~~ | ✅ Fixed — commit `9feb2642` |
| ~~#51~~ | ~~Beta-exit proof/validation~~ | ✅ Fixed — PR #72 |

Beta exit gate is open. See `docs/SPINE_BETA_EXIT_VALIDATION.md` for the full evidence-backed judgment.

---

## v1.0 — Post-Beta Stabilization (Active — Milestone #6)

> Bug fixes and usability hardening only. No new features until v0.2.0 stabilizes.

| # | Issue | Status |
|---|---|
| #73 | SPINE_ROOT ergonomics for long-running shells / multi-repo use | ✅ Done — `spine target` command added |
| #74 | Discipline-tax reduction in repeated governance workflows | 🟡 Open — Phase 3B candidate |
| #75 | OpenClaw first-class startup/skill path | 🟡 Open — Phase 3B candidate |

---

## Phase 3B Candidates

### ✅ SPINE_ROOT ergonomics (#73)
**Status:** Done — `spine target` command added. Shows resolved target with source annotation. Documents one-shot `SPINE_ROOT=/path spine <cmd>` pattern. 15 new tests, all passing.

### 🟡 Discipline-tax reduction (#74)
**Status:** Active — Phase 3B candidate

### 🟡 OpenClaw first-class startup/skill path (#75)
**Status:** Active — Phase 3B candidate

### 🚫 HUD / live observability mode
**Status:** REJECTED

### 🚫 Notification / webhook systems
**Status:** REJECTED

### 🚫 Remote MCP (strategic question — INTERNAL, not yet approved)
**Status:** DEFERRED — Issue #76 — product decision pending

---

*Last updated: 2026-04-10 — v0.2.0 released. Post-beta stabilization active. Milestone #6 open.*
