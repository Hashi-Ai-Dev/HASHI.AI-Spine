# SPINE Roadmap

> **What SPINE is:** Local-first, repo-native mission governor for AI coding agents. Governance layer above coding agents (Claude Code, Codex, OpenClaw, OpenCode). Manages mission, scope, proof, decisions, drift, and reviews.

> **What SPINE is NOT:** A coding agent itself. A dashboard-first product. A cloud control plane. A swarm orchestration system.

---

## Project Stage

**Stage: Post-beta stable.** v0.2.1 released 2026-04-14. v1.0 target.

---

## Current Phase

**Phase 2 Complete.** SPINE has a working Phase 1 (init) and Phase 2 (governance commands: brief, doctor, mission, proof, decision, drift) CLI suite.

Current stabilization target: **v0.1.2**

---

## Milestone Structure

| Milestone | Scope | Status |
|-----------|-------|--------|
| `v0.1.1-alpha` | Phase 1 + 2 core, public alpha launch | ✅ Published |
| `v0.1.2` | Stabilization: CI, `--cwd` support, security settings, docs | 🔄 Next |
| `v0.2 / Phase 3A` | CLI surface expansion, Phase 3 spec implementation | 📋 Planned |

---

## v0.1.2 — Stabilization (Next)

**Goal:** Fix known gaps, add minimal CI, improve external-repo support, close security settings.

### Planned items:
- Enable Dependabot alerts + secret scanning (human action required in GitHub settings)
- Add `--cwd` support to Phase 2 commands (only `spine init` accepts it currently)
- Add minimal CI pipeline (lint + tests on push/PR)
- Create org-level ruleset for `Hashi-Ai-Dev`
- Clarify onboarding / quickstart docs

---

## v0.2 / Phase 3A — CLI Expansion

**Goal:** Expand command surface beyond Phase 2, implement Phase 3 architecture spec.

### Planned items (see `docs/SPINE_FEATURE_BACKLOG.md` for full list):
- CLI surface: additional governance commands
- Phase 3 architecture decisions from planning spec
- Further external-repo compatibility
- CI/status check improvements

**Phase 3A spec exists** at `docs/SPINE_PHASE3A_v0.2_SPEC.md`. Implementation requires human review + explicit approval.

---

## Later Phases (Not Yet Planned)

- Phase 3B and beyond
- Remote MCP server / networking layer
- Multi-user / collaboration features
- Web UI / dashboard
- Auth, billing, cloud sync

---

## Explicitly Out of Scope (v0.x)

- Any cloud control plane or SaaS layer
- Swarm orchestration or multi-agent coordination
- Dashboard-first product thinking
- Remote networking (until Phase 3+ explicitly approved)
- Non-AI-coder use cases (this is a coder tool for coder tools)

---

## Strategic Positioning

SPINE sits **above** the coding agent layer. It does not code — it governs the agent that does. The product is the governance primitive: clear mission, enforced scope, proof of work, decision audit trail, drift detection.

Solo builder advantage: no committee, no infinite scope. Ship fast, learn fast.

---

*Last updated: 2026-04-07 by SPINE Repo Manager Agent*
