# SPINE Status

**Last updated:** 2026-04-08 (Issue #38 — deterministic fixtures merged, Beta core complete)
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
| Beta feature queue | ✅ Complete — core issues done, polish queued |

---

## Current Milestone

**`Beta`** — v0.2.0-beta

### Completed Beta Issues

| # | Issue | Status |
|---|---|---|
| #31 | `spine check before-pr` preflight checkpoint | ✅ Done — PR #35 |
| #32 | Handoff/PR-prep summary primitive | ✅ Done — PR #39 |
| #33 | Draftable governance records | ✅ Done — PR #40 |
| #34 | Local optional hook/checkpoint integration | ✅ Done — PR #41 |
| #43 | `check before-pr` exit 1 on healthy repos | ✅ Fixed — PR #46 |
| #44 | Hook script missing `uv run` | ✅ Fixed — PR #46 |
| #45 | AGENTS.md template invalid commands | ✅ Fixed — PR #46 |
| #36 | Mission refine draft flow | ✅ Done — PR #48 |
| #37 | Compatibility/integration guide | ✅ Done — PR #48 |
| #38 | Deterministic validation fixtures and contract harness | ✅ Done — PR #52 |

### Beta Polish Queue

| # | Issue | Status |
|---|---|---|
| #38 | Deterministic validation fixtures | ✅ Done — PR #52 |
| #49–#51 | Beta polish issues | 📋 Queued |

---

## Next Active Priority

**Beta core queue complete.** All scheduled Beta core issues (#31–#38) done. Beta polish (#49, #50, #51) queued.

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
