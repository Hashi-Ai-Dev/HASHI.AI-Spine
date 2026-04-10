# SPINE Roadmap

> **What SPINE is:** Local-first, repo-native mission governor for AI coding agents. Governance layer above coding agents (Claude Code, Codex, OpenClaw, and similar). Manages mission, scope, proof, decisions, drift, and reviews.

> **What SPINE is NOT:** A coding agent itself. A dashboard-first product. A cloud control plane. A swarm orchestration system.

---

## Project Stage

**Beta achieved.** v0.2.0-beta published 2026-04-07. Beta exit validation passed 2026-04-09. Core CLI is functional and governance-validated.

---

## Current Phase

**Phase 3A Complete.** SPINE has a working Phase 1 (init), Phase 2 (governance commands), and Phase 3A (drift detection, MCP, review, check surfaces) CLI suite.

Current target: **v0.2.0 — post-beta release**

---

## Milestone Structure

| Milestone | Scope | Status |
|-----------|-------|--------|
| `v0.1.1-alpha` | Phase 1 + 2 core, public alpha launch | ✅ Published 2026-04-07 |
| `v0.2.0-beta` | Phase 3A full surface, beta stabilization, integrations | ✅ Beta achieved 2026-04-09 |
| `v0.2.0` | Post-beta: bug fixes only, Phase 3B candidates deferred | 📋 Next |

---

## v0.2.0 — Post-Beta Release (Next)

**Goal:** Bug fixes only. No new features until v0.2.0 is stable. Phase 3B candidates remain deferred.

### Post-beta policy:
- Bug fixes and security issues only
- No new feature work until v0.2.0 stabilizes
- Phase 3B candidates tracked in `docs/SPINE_FEATURE_BACKLOG.md`

### Out of scope until Phase 3B:
- New CLI surfaces beyond existing Phase 3A suite
- Cloud dashboards or remote control planes
- Agent orchestration or task decomposition
- Universal agent framework positioning

---

## Phase 3B — Growth (Deferred)

### Candidates:
- Optional governance profiles (e.g., strict / relaxed / audit)
- Stronger local tool-consumption surfaces
- Deeper external-agent compatibility (OpenClaw first-class path)
- Version story normalization across repo surfaces

---

## Getting Started

```bash
pip install spine-cli
spine init
spine doctor
uv run spine brief --target claude
```
