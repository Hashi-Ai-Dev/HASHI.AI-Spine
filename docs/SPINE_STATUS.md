# SPINE Status

**Last updated:** 2026-04-10 (Post-beta stabilization active; #73 SPINE_ROOT ergonomics resolved — `spine target` added)
**Repo:** `Hashi-Ai-Dev/SPINE`

---

## Current Release

| | |
|---|---|
| **Version** | `v0.2.0-beta` |
| **Status** | Beta exit achieved — ready for formal v0.2.0 tag |
| **Target** | v0.2.0 |

---

## Phase Map

| Phase | Status |
|---|---|
| Phase 1 + 2 | ✅ Complete |
| Alpha Exit → v0.2.0-beta | ✅ Released (2026-04-07) |
| Beta blocker stabilization | ✅ Complete — PR #46 |
| Beta core feature queue | ✅ Complete |
| Beta polish queue | ✅ Complete |
| **Beta exit** | ✅ Achieved (2026-04-09) |
| **Next** | v0.2.0 tag + post-beta stabilization |

---

## ✅ Beta Exit — All Closed

Beta exit gate cleared. All pre-beta-exit issues resolved.

| # | Issue | PR |
|---|---|
| #57 | MCP TextContent NameError | PR #61 |
| #58 | README exit code + test count | PR #63 |
| #59 | `spine drift scan --json` | PR #67 |
| #64 | `spine evidence list` + `spine decision list` | PR #68 |
| #65 | `check before-pr --json` structured doctor detail | PR #69 |
| #66 | `check before-work` no-brief advisory | PR #70 |
| #60 | SECURITY_BASELINE wrong repo name | commit `9feb2642` |
| #51 | Beta-exit proof/validation | PR #72 |

### Beta Exit Validation

See `docs/SPINE_BETA_EXIT_VALIDATION.md` for the full evidence-backed judgment.

### Post-Beta Housekeeping (2026-04-10)
- `.spine/mission.yaml` populated with real self-governance values (commit `c0cf5d3c`) — beta-exit caveat resolved
- `docs/SPINE_ROADMAP.md` updated for post-beta state
- `milestone/6` created: "v1.0 — Post-Beta Stabilization"

---

## Current Milestone

**`v0.2.0`** — Post-beta release

Next: operator cuts the v0.2.0 tag. See `docs/SPINE_ROADMAP.md`.

---

## v1.0 Stabilization Progress (Milestone #6)

| # | Issue | Status |
|---|---|---|
| #73 | SPINE_ROOT ergonomics — `spine target` command | ✅ Done — branch `claude/spine-root-ergonomics-l2Vu3` |
| #74 | Discipline-tax reduction | 🟡 Open |
| #75 | OpenClaw first-class startup/skill path | 🟡 Open |
| #76 | Remote MCP (strategic) | 🔵 Deferred |

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
- Spec: `docs/SPINE_SPEC.md` (canonical post-beta)
- Phase 3A planning history: `docs/SPINE_PHASE3A_v0.2_SPEC.md` (complete/historical)
- Tracking policy: `docs/SPINE_TRACKING_POLICY.md`
- Agent skill: `docs/SPINE_AGENT_SKILL.md`
- Beta-exit validation: `docs/SPINE_BETA_EXIT_VALIDATION.md`
- Roadmap: `docs/SPINE_ROADMAP.md`

---

*Updated by: SPINE Repo Manager Agent*
