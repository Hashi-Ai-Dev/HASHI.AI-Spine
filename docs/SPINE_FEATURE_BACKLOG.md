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
**Description:** Added Installation section (git clone + uv sync), rewrote Quickstart with `--cwd` as primary pattern, renamed "Governing an External Repo" section, removed stale references, fixed Python badge 3.11→3.12, updated test count.
**Why it matters:** Public alpha with confusing onboarding loses users before they experience value.
**Status:** DONE — merged in PR #13 (2026-04-07)

---

## v0.2 / Phase 3A — Portability + Operator Polish

> Phase 3A focus: make SPINE portable and ergonomic across arbitrary repos. Reduce discipline tax. No new product surface.
> Spec approved 2026-04-07. Implementation queue live — issues #15–#18.

### ✅ [Phase 3A.2] Explicit repo targeting contract (#15)
**Description:** Fixed `resolve_roots()` so `--cwd` takes precedence over `SPINE_ROOT`. Targeting contract standardized.
**Why it matters:** Ambiguous targeting causes operators to accidentally govern the wrong repo.
**Status:** DONE — implemented in PR #19 (2026-04-07)

### ✅ [Phase 3A.2] Repo/branch context visibility (#16)
**Description:** Standard context reporting: repo path, HEAD branch/detached state, resolved default branch. Clear warning path for unresolved states.
**Why it matters:** Operators need to always know which context SPINE is operating in.
**Status:** DONE — implemented on branch `claude/issue16-context-visibility-QKMkH` (2026-04-07)

### 📋 [Phase 3A.3] Operator/CI output modes + stable exit codes (#17)
**Description:** `--json` flag on key commands, reduced-noise mode, documented stable exit codes (0=success, 1=validation fail, 2=context fail).
**Why it matters:** Human-readable output is insufficient for CI and scripting.
**Status:** APPROVED — implementation queue #17

### 📋 [Phase 3A] Bootstrap polish + discipline-tax ergonomics (#18)
**Description:** Improve first-run messaging, reduce mandatory ceremony, improve default flows, clarify error messages.
**Why it matters:** SPINE only has value if operators sustain its use. Governance that costs too much attention gets abandoned.
**Status:** APPROVED — implementation queue #18

### 🟡 Enhanced CI (integration + smoke tests)
**Description:** Expand CI beyond lint/unit to integration tests against temp repos and smoke tests against real external repos.
**Why it matters:** Confidence at release time currently depends on manual testing.
**Status:** DEFERRED — Phase 3A.2+ stability required first

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
