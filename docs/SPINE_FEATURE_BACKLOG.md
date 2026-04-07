# SPINE Feature Backlog

Grouped by target milestone. Each item: title, short description, why it matters, status.

---

## v0.1.2 — Stabilization

### ✅ Add `--cwd` support to Phase 2 commands
**Description:** Added `--cwd PATH` to all 9 Phase 2 commands: mission show/set, evidence add, decision add, opportunity score, drift scan, brief, doctor, mcp serve. Also unhidden on `review weekly`.
**Why it matters:** Blocks external-repo workflows — users must cd into the repo before running any SPINE command. Pain point confirmed in external validation.
**Status:** DONE — merged in PR #11 (2026-04-07)

### ✅ Add minimal CI pipeline (lint + tests on push/PR)
**Description:** `ci.yml` GitHub Actions workflow with ruff linting and pytest. Runs on every push and PR.
**Why it matters:** Enables status checks on PRs, removes "always-passing" gap in branch protection, provides automated quality signal.
**Status:** DONE — merged in PR #12 (2026-04-07)

### ✅ Enable Dependabot alerts + secret scanning push protection
**Description:** GitHub security settings enabled via GitHub settings page.
**Why it matters:** Public repos need active vulnerability monitoring. Secret scanning push protection prevents credentials from being committed.
**Status:** DONE — enabled by owner via settings page.

### ❌ ~~Create org-level ruleset for `Hashi-Ai-Dev`~~
**Description:** ~~A GitHub organization ruleset that enforces `main` branch protection across all repos in the org.~~
**Why it matters:** ~~Future repos spawned in the org will be unprotected without this.~~
**Status:** REJECTED — org-level concern, not a SPINE product issue. Close #8.

### ✅ Clarify onboarding / quickstart docs
**Description:** Added Installation section, rewrote Quickstart to show external-repo `--cwd` flow as primary pattern, promoted `--cwd` over `SPINE_ROOT` for all commands, removed stale Known Limitations and What's Next items, fixed Python badge and test count.
**Why it matters:** Public alpha with confusing onboarding loses users before they experience value.
**Status:** DONE — Issue #9, merged in this pass (2026-04-07)

---

## v0.2 / Phase 3A

### 📋 Plan: CLI surface expansion
**Description:** Additional governance commands beyond Phase 2 (e.g., `spine review`, `spine scope`, `spine sync`). Exact commands TBD from Phase 3A spec.
**Why it matters:** Phase 2 CLI is functional but deliberately minimal. Phase 3A expands the command surface with more governance primitives.
**Status:** PLANNED — requires Phase 3A spec approval before implementation

### 📋 Plan: Phase 3 architecture implementation
**Description:** Implement architectural decisions from `docs/SPINE_PHASE3A_v0.2_SPEC.md`. Likely includes refactors to Phase 2 command structure, better state management, possibly plugin architecture.
**Why it matters:** Phase 3 is the first real architectural step — not just new commands but better foundations.
**Status:** PLANNED — requires approved spec

### 📋 Plan: External-repo compatibility pass
**Description:** Broader external-repo compatibility testing and fixes beyond the `--cwd` fix in v0.1.2.
**Why it matters:** SPINE should work on any AI coding workflow repo, not just the ones with a specific setup.
**Status:** PLANNED

### 📋 Plan: Enhanced CI (integration tests, smoke tests)
**Description:** Expand CI beyond lint/unit tests to include integration tests against temp repos and smoke tests against real external repos.
**Why it matters:** Confidence at release time currently depends on manual testing. Automated regression detection is needed at scale.
**Status:** PLANNED

---

## Later / Deferred

### 🟡 Remote MCP server / networking layer
**Description:** SPINE as a local MCP server that agents can connect to remotely.
**Why it matters:** Would enable multi-machine / remote agent workflows.
**Status:** DEFERRED — out of scope for v0.x, requires Phase 3+ planning

### 🟡 Multi-user / collaboration features
**Description:** Shared mission files, team-scoped proofs, review workflows.
**Why it matters:** Would enable team usage beyond solo builder.
**Status:** DEFERRED — solo-builder focus for v0.x

### 🟡 Web UI / dashboard
**Description:** A visual interface for browsing proofs, decisions, drift reports.
**Why it matters:** Not a v0 priority. SPINE is CLI-first for a reason.
**Status:** DEFERRED — dashboard-first is explicitly not the product identity

### 🟡 Auth, billing, cloud sync
**Description:** SaaS layer on top of SPINE.
**Why it matters:** Not on the roadmap. SPINE is local-first by design.
**Status:** DEFERRED

### 🟡 Phase 3B+ full architecture
**Description:** Agentic loops, automated scope enforcement, proof aggregation.
**Why it matters:** Future vision beyond Phase 3A.
**Status:** DEFERRED — Phase 3A must be stable first

---

## Explicitly Rejected

### 🚫 Swarm orchestration / multi-agent coordination
**Description:** SPINE as a coordination layer for multiple AI agents working simultaneously.
**Why it matters:** Not SPINE's job. SPINE governs a single agent's mission, not multiple agents.
**Status:** REJECTED

### 🚫 Dashboard-first product
**Description:** Building a UI before the CLI is solid.
**Why it matters:** SPINE's identity is a governance layer above agents. A dashboard inverts the priority.
**Status:** REJECTED

### 🚫 Cloud control plane
**Description:** Centralized cloud service managing SPINE deployments.
**Why it matters:** SPINE is local-first by design. No SaaS layer.
**Status:** REJECTED

### 🚫 Non-agent integrations as primary use case
**Description:** Using SPINE to govern non-AI-coder workflows (human devs, deployment pipelines, etc.).
**Why it matters:** SPINE is built for AI coding workflows specifically. General-purpose use dilutes the product.
**Status:** REJECTED

---

*Last updated: 2026-04-07 by SPINE Repo Manager Agent*
