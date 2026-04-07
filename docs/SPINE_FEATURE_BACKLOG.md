# SPINE Feature Backlog

Grouped by target milestone. Each item: title, short description, why it matters, status.

---

## v0.1.2 — Stabilization

### ✅ Add `--cwd` support to Phase 2 commands
**Description:** Added `--cwd PATH` to all 9 Phase 2 commands.
**Why it matters:** Blocks external-repo workflows.
**Status:** DONE — merged in PR #11 (2026-04-07)

### ✅ Add minimal CI pipeline (lint + tests on push/PR)
**Description:** `ci.yml` GitHub Actions workflow with ruff + pytest on every push/PR.
**Why it matters:** Enables status checks on PRs.
**Status:** DONE — merged in PR #12 (2026-04-07)

### ✅ Clarify onboarding / quickstart docs
**Description:** Added Installation section, rewrote Quickstart with `--cwd` as primary pattern.
**Why it matters:** Public alpha with confusing onboarding loses users.
**Status:** DONE — merged in PR #13 (2026-04-07)

---

## Alpha Exit — v0.2.0-beta

### ✅ Explicit repo targeting contract (#15)
**Description:** Fixed `--cwd` precedence over `SPINE_ROOT`. Targeting contract standardized.
**Status:** DONE — merged in PR #19 (2026-04-07)

### ✅ Repo/branch context visibility (#16)
**Description:** Deterministic default branch resolution + context line on git-relevant commands.
**Status:** DONE — merged in PR #20 (2026-04-07)

### ✅ Operator/CI output modes + stable exit codes (#17)
**Description:** Stable exit codes (0/1/2), `--json` output on all relevant commands.
**Status:** DONE — merged in PR #21 (2026-04-07)

### ✅ Bootstrap polish + discipline-tax ergonomics (#18)
**Description:** Next-steps panel, `spine doctor` verification, git commit guidance. Bug fixes: doctor absolute-path bug.
**Status:** DONE — merged in PR #26 (2026-04-07)

### 📋 Artifact ergonomics contract (#23)
**Description:** Formalize canonical artifact aliases (`latest/`), deterministic file naming, machine-readable manifest.
**Status:** IN QUEUE — Alpha Exit

### 📋 External-repo onboarding docs (#24)
**Description:** Practical guide for using SPINE in an arbitrary external repo.
**Status:** IN QUEUE — Alpha Exit

### 📋 Alpha-exit validation gate matrix (#25)
**Description:** Structured gate pass before declaring v0.2.0-beta.
**Status:** IN QUEUE — Alpha Exit

---

## Phase 3B / Beta Candidates

> Preserved inputs from product review session 2026-04-07. Not active work. Phase 3B begins after alpha exit is validated.

### 🟡 Draftable governance records
**Description:** Draft evidence, draft decisions, draft PR/handoff summaries.
**Status:** CANDIDATE — Phase 3B

### 🟡 Native hooks / lifecycle enforcement
**Description:** Local, explicit, opt-in pre-commit / pre-PR governance hooks.
**Status:** CANDIDATE — Phase 3B

### 🟡 Mission interview / brainstorm flow
**Description:** Explicit operator-invoked mission refinement. Draft mission generation only.
**Status:** CANDIDATE — Phase 3B, constrained

### 🟡 Stronger local tool-consumption surfaces
**Description:** Stable command contracts, machine-readable outputs, richer local MCP surfaces.
**Status:** CANDIDATE — Phase 3B

### 🟡 Optional governance profiles
**Description:** Explicit opt-in workflow profiles. Visible rules, not hidden enforcement.
**Status:** CANDIDATE — Phase 3B, optional

### 🚫 HUD / live observability mode
**Description:** Dashboard or live monitoring.
**Status:** REJECTED — dashboard creep

### 🚫 Notification / webhook systems
**Description:** Ping operators when governance events occur.
**Status:** REJECTED — not local-first

---

*Last updated: 2026-04-07 by SPINE Repo Manager Agent*
