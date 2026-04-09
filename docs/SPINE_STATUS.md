# SPINE Status

**Last updated:** 2026-04-09 (Issue #57 — MCP fix merged, 3 pre-beta-exit blockers remain)
**Repo:** `Hashi-Ai-Dev/SPINE`

---

## Current Release

| | |
|---|---|
| **Version** | `v0.2.0-beta` |
| **Status** | Published (2026-04-07) — pre-release |
| **Target** | Beta |

---

## Phase Map

| Phase | Status |
|---|---|
| Phase 1 + 2 | ✅ Complete |
| Alpha Exit → v0.2.0-beta | ✅ Released (2026-04-07) |
| Beta blocker stabilization | ✅ Complete — PR #46 |
| Beta core feature queue | ✅ Complete — all core issues done |
| Beta polish queue | ✅ Complete |
| **Pre-Beta-Exit blockers** | ⚠️ **3 open — beta exit still blocked** |

---

## ⚠️ Beta Exit Blocked

Beta exit is NOT currently justified. MCP is now fixed (PR #61). Three blockers remain.

### Remaining Pre-Beta-Exit Blockers (Milestone #5)

| # | Issue | Severity | Status |
|---|---|---|---|
| ~~#57~~ | ~~MCP TextContent NameError~~ | ~~🔴 Blocker~~ | ✅ **Fixed — PR #61** |
| #58 | README exit code table wrong | 🟡 High | Open |
| #59 | `drift scan --json` missing | 🟡 Medium | Open |
| #60 | SPINE_SECURITY_BASELINE.md wrong repo name | 🟡 Medium | Open |

---

## Current Milestone

**`Beta`** — v0.2.0-beta

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
| #57 | MCP TextContent NameError | PR #61 |

### Beta Polish Queue

| # | Issue | Status |
|---|---|---|
| #51 | Beta-exit proof/validation | 📋 Queued — blocked until pre-beta-exit blockers cleared |

---

## Next Active Priority

**Issue #58** — README exit code table fix (high). 3 blockers remain before beta-exit is unblocked.

---

## What SPINE Is

SPINE is a **repo-native mission governor** for AI coding agents. It sits above the agent and keeps it aligned to a defined mission — not by being smart, but by being explicit.

**Core loop:** Mission → Scope → Proof → Decisions → Drift Check

**Discipline rule:** SPINE should reduce discipline tax not by hiding governance, but by making governance easy for agents and tools to execute explicitly.

**Authority rule:** Agents may execute governance mechanics. Operators retain governance authority.

---

## Links

- Repo: https://github.com/Hashi-Ai-Dev/SPINE
- Releases: https://github.com/Hashi-Ai-Dev/SPINE/releases
- Spec: `docs/SPINE_PHASE3A_v0.2_SPEC.md`
- Tracking policy: `docs/SPINE_TRACKING_POLICY.md`

---

*Updated by: SPINE Repo Manager Agent*
