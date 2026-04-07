# SPINE Roadmap

> **What SPINE is:** Local-first, repo-native mission governor for AI coding agents. Governance layer above coding agents (Claude Code, Codex, OpenClaw, OpenCode). Manages mission, scope, proof, decisions, drift, and reviews.

> **What SPINE is NOT:** A coding agent itself. A dashboard-first product. A cloud control plane. A swarm orchestration system.

---

## Project Stage

**Public alpha.** v0.1.1-alpha published 2026-04-07. Core CLI is functional and externally validated.

---

## Current Phase

**Phase 1 + 2 Complete.** SPINE has a working Phase 1 (init) and Phase 2 (full governance command suite: mission, brief, evidence, decision, opportunity, drift, review, doctor, mcp) CLI.

**v0.1.2 stabilization is complete.** Tag pending. Phase 3A planning is now the active focus.

---

## Milestone Structure

| Milestone | Scope | Status |
|-----------|-------|--------|
| `v0.1.1-alpha` | Phase 1 + 2 core, public alpha launch | ✅ Published |
| `v0.1.2` | Stabilization: CI, `--cwd` support, security settings, docs | ✅ Stabilization complete — tag pending |
| `v0.2 / Phase 3A` | Portability + operator polish | 📋 Planning (spec normalized 2026-04-07) |

---

## v0.1.2 — Stabilization (Complete ✅)

**Goal:** Fix known gaps, add minimal CI, improve external-repo support, close security settings.

### Completed items:
- ✅ Enable Dependabot alerts + secret scanning
- ✅ Add `--cwd` support to all Phase 2 commands (PR #11)
- ✅ Add minimal CI pipeline (ruff + pytest) (PR #12)
- ❌ Create org-level ruleset — rejected (org-level concern, not a SPINE issue)
- ✅ Clarify onboarding / quickstart docs (PR #13)

---

## v0.2 / Phase 3A — Portability + Operator Polish

**Goal:** Make SPINE portable and ergonomic across arbitrary repos. Reduce discipline tax without inventing fake automation. No new product surface.

### Planned items (see `docs/SPINE_PHASE3A_v0.2_SPEC.md` and `docs/SPINE_FEATURE_BACKLOG.md`):
- Explicit repo targeting with clear error paths
- Repo/branch/default-branch context visibility
- Operator/CI output modes (`--json`, `--quiet`, stable exits)
- Artifact naming and path convention standardization
- Bootstrap/install polish for non-SPINE repos
- External-repo usage docs and examples

**Phase 3A spec normalized** at `docs/SPINE_PHASE3A_v0.2_SPEC.md` (2026-04-07). Planning complete per Issue #10. Implementation requires human review + explicit approval before beginning.

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

*Last updated: 2026-04-07 — Phase 3A planning normalization (Issue #10)*
