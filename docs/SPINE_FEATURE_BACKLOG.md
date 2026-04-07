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
**Description:** Deterministic default branch resolution (remote origin/HEAD → local main → local master) + context line on brief, doctor, drift, mission, review.
**Why it matters:** Operators need to always know which context SPINE is operating in.
**Status:** DONE — implemented in PR #20 (2026-04-07)

### ✅ [Phase 3A.3] Operator/CI output modes + stable exit codes (#17)
**Description:** Stable exit codes (0=success, 1=validation fail, 2=context fail). `--json` output on all relevant commands. Error context in JSON on failure paths.
**Why it matters:** Human-readable output is insufficient for CI and scripting.
**Status:** DONE — implemented in PR #21 (2026-04-07)

### ✅ [Phase 3A] Bootstrap polish + discipline-tax ergonomics (#18)
**Description:** Fixed stale `spine init` templates (AGENTS.md, CLAUDE.md now reflect Phase 3A commands); improved init next-steps panel (doctor verification + git commit guidance); fixed doctor absolute-path bug in contract file errors; context-aware `MissionNotFoundError` messages; unhid `--cwd` in `spine init`; updated top-level `--help` text. 8 new focused tests. 213/213 passing.
**Why it matters:** SPINE only has value if operators sustain its use. Governance that costs too much attention gets abandoned.
**Status:** DONE — implemented in PR on branch `phase3a/issue18-bootstrap-discipline-tax` (2026-04-07)

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

## Phase 3B / Beta Candidates

> Preserved inputs from product review session 2026-04-07. Not active work. Phase 3B begins after alpha exit is validated.

### 🟡 Draftable governance records (Phase 3B)
**Description:** Draft evidence, draft decisions, draft PR/handoff summaries. Governance records that are explicitly tentative until the operator confirms them as canonical.
**Why it matters:** Reduces friction without mutating truth silently. Makes governance feel lighter without hiding anything.
**Status:** CANDIDATE — Phase 3B

### 🟡 Native hooks / lifecycle enforcement (Phase 3B)
**Description:** Local, explicit, opt-in pre-commit / pre-PR governance hooks. Not hidden daemon behavior.
**Why it matters:** Makes SPINE governance naturally part of existing developer workflow. Low friction, high signal.
**Status:** CANDIDATE — Phase 3B

### 🟡 Mission interview / brainstorm flow (Phase 3B)
**Description:** Explicit operator-invoked mission refinement. Draft mission generation only. Operator controls what becomes canonical.
**Why it matters:** Reduces discipline tax around mission framing without silently mutating canonical truth.
**Status:** CANDIDATE — Phase 3B, constrained

### 🟡 Stronger local tool-consumption surfaces (Phase 3B)
**Description:** Stable command contracts, machine-readable outputs, stable artifact references, richer local MCP surfaces.
**Why it matters:** Makes SPINE governance accessible to agents and tools without requiring human intermediaries.
**Status:** CANDIDATE — Phase 3B

### 🟡 Optional governance profiles (Phase 3B)
**Description:** Explicit opt-in workflow profiles. Visible rules, not hidden methodology enforcement.
**Why it matters:** Could support team-specific governance styles without forcing adoption.
**Status:** CANDIDATE — Phase 3B, optional

### 🚫 HUD / live observability mode
**Description:** Dashboard or live monitoring of governance state.
**Why it matters:** Too easy to drift toward dashboard creep. SPINE is governance, not observability.
**Status:** REJECTED

### 🚫 Notification / webhook systems
**Description:** Ping operators when governance events occur.
**Why it matters:** A governance tool that notifies you is no longer purely local-first.
**Status:** REJECTED

---

*Last updated: 2026-04-07 by SPINE Repo Manager Agent*
