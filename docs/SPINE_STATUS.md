# SPINE Status

**Last updated:** 2026-04-08 (blocker stabilization — Beta Bug Hunt complete)
**Repo:** `Hashi-Ai-Dev/SPINE`

---

## Current Release

| | |
|---|---|
| **Version** | `v0.2.0-beta` |
| **Status** | Published (2026-04-07) — pre-release |
| **Target** | Beta stabilization |

---

## Phase Map

| Phase | Status |
|---|---|
| Phase 1 + 2 | ✅ Complete |
| Alpha Exit → v0.2.0-beta | ✅ Released — v0.2.0-beta (2026-04-07) |
| Beta blocker stabilization | 🔄 In Progress |
| Beta feature queue | 📋 Queued |

---

## Current Milestone

**`Beta`** — v0.2.0-beta

### ⚠️ BLOCKERS — 3 regression issues found in shipped Beta features

> These regressions were found in the Beta Bug Hunt (PR #42). They must be fixed before more Beta features ship.

| # | Issue | Priority |
|---|---|---|
| #43 | [BUG] `check before-pr` exits 1 on healthy repos due to doctor warnings | 🔴 FIX FIRST |
| #44 | [BUG] Hook script uses `spine` instead of `uv run` — hook fails | 🔴 FIX SECOND |
| #45 | [BUG] AGENTS.md template has invalid commands — shipped to users | 🔴 FIX THIRD |

### Beta Feature Queue (after blockers resolved)

| # | Issue | Status |
|---|---|---|
| #36 | Mission refine draft flow | 📋 Queued |
| #37 | Compatibility/integration guide | 📋 Queued |
| #38 | Deterministic validation fixtures | 📋 Queued |

---

## Next Active Priority

**Issue #43** — Fix `check before-pr` exit 1 regression. Blockers must be cleared before returning to Beta feature queue.

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
