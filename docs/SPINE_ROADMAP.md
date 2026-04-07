# SPINE Roadmap

> **What SPINE is:** Local-first, repo-native mission governor for AI coding agents. Governance layer above coding agents (Claude Code, Codex, OpenClaw, OpenCode). Manages mission, scope, proof, decisions, drift, and reviews.

> **What SPINE is NOT:** A coding agent itself. A dashboard-first product. A cloud control plane. A swarm orchestration system.

---

## Project Stage

**Public beta.** `v0.2.0-beta` released 2026-04-07. Alpha exit complete. Phase 3A delivered.

---

## Current Phase

**Beta.** SPINE is in beta. Phase 3A (Portability + Operator Polish) is complete. Beta focus is discipline-tax reduction, agent-executable governance mechanics, and handoff/PR-prep primitives.

---

## Milestone Structure

| Milestone | Scope | Status |
|-----------|-------|--------|
| `v0.1.1-alpha` | Phase 1 + 2 core, public alpha launch | ✅ Published |
| `v0.1.2` | Stabilization: CI, `--cwd` support, security settings, docs | ✅ Released |
| `v0.2.0-beta / Phase 3A` | Portability + operator polish, alpha exit | ✅ Released 2026-04-07 |
| `Beta` | Repeated-use proof, handoff primitives, preflight commands | 🔄 Active |
| `v1.0.0` | Stable contracts, authority, automation surfaces | 📋 Planned |

---

## Beta — Active Phase

**Goal:** Prove SPINE can be used repeatedly in real workflows without turning governance into exhausting ceremony.

### Candidate workstreams (see `docs/SPINE_FEATURE_BACKLOG.md` for full list):
- Draftable governance records
- Native hooks / lifecycle enforcement
- Mission interview / brainstorm flow
- Stronger local tool-consumption surfaces
- Optional governance profiles

**Next step:** Define first bounded Beta implementation slice(s). Open Beta milestone with scoped issues.

---

## Later Phases

- v1.0.0: stable contracts, authority boundaries, automation surfaces
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

*Last updated: 2026-04-07 — post-beta normalization pass*
