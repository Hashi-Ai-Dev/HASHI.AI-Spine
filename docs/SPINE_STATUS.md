# SPINE Status

**Last updated:** 2026-04-09 (Issue #59 — drift scan --json merged, 4 pre-beta-exit blockers remain)
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
| Beta core feature queue | ✅ Complete |
| Beta polish queue | ✅ Complete |
| **Pre-Beta-Exit blockers** | ⚠️ **4 open — beta exit blocked** |

---

## ⚠️ Beta Exit Blocked

Beta exit is NOT currently justified. 4 pre-beta-exit issues remain.

**Agent-usability-first ordering** (from dogfood session): agent-usage issues before docs cleanup.

### Pre-Beta-Exit Queue (Milestone #5)

| Priority | # | Issue | Status |
|---|---|---|---|
| 1 | ~~#59~~ | ~~`spine drift scan --json` missing~~ | ✅ Fixed — PR #67 |
| 2 | #64 | `spine evidence list` + `spine decision list` | 🟡 Medium — Open |
| 3 | #65 | `check before-pr --json` structured doctor detail | 🟡 Medium — Open |
| 4 | #66 | `check before-work` no-brief advisory not exit 1 | 🟡 Medium — Open |
| 5 | #60 | SECURITY_BASELINE wrong repo name | 🟡 Medium — Open |

### Fixed

| # | Issue | Status |
|---|---|
| ~~#57~~ | ~~MCP TextContent NameError~~ | ✅ Fixed — PR #61 |
| ~~#58~~ | ~~README exit code + test count~~ | ✅ Fixed — PR #63 |
| ~~#59~~ | ~~`spine drift scan --json` missing~~ | ✅ Fixed — PR #67 |

---

## Current Milestone

**`Beta`** — v0.2.0-beta

### Beta Complete

| # | Issue | PR |
|---|---|---|
| #31–#50 | All Beta core + polish issues | PRs #35–#54 |
| #57 | MCP TextContent NameError | PR #61 |
| #58 | README exit codes + test count | PR #63 |
| #59 | `spine drift scan --json` | PR #67 |

### Beta Polish Queue

| # | Issue | Status |
|---|---|---|
| #51 | Beta-exit proof/validation | 📋 Last — blocked until pre-beta-exit issues cleared |

---

## Next Active Priority

**Issue #64** — `spine evidence list` + `spine decision list`. Agent-usability-first ordering.

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
