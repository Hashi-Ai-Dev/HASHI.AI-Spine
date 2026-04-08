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

## Alpha Exit — v0.2.0-beta (Released 2026-04-07)

### ✅ Explicit repo targeting contract (#15)
**Status:** DONE — merged in PR #19 (2026-04-07)

### ✅ Repo/branch context visibility (#16)
**Status:** DONE — merged in PR #20 (2026-04-07)

### ✅ Operator/CI output modes + stable exit codes (#17)
**Status:** DONE — merged in PR #21 (2026-04-07)

### ✅ Bootstrap polish + discipline-tax ergonomics (#18)
**Status:** DONE — merged in PR #26 (2026-04-07)

### ✅ Artifact ergonomics contract (#23)
**Status:** DONE — implemented in PR #27 (2026-04-07)

### ✅ External-repo onboarding docs (#24)
**Status:** DONE — implemented in PR #28 (2026-04-07)

### ✅ Alpha-exit validation gate matrix (#25)
**Status:** DONE — implemented in PR #29 (2026-04-07)

---

## Beta — v0.2.0-beta Active Issues

> Beta milestone. Execution order: **#34 → #36 → #37 → #38**
>
> Dependency rationale:
> - **#34 first** — builds on #31 checkpoint; anticipates #33 draft confirmation
> - **#36 second** — depends on #33's draft infrastructure
> - **#37 third** — docs-only, can run parallel to implementation
> - **#38 fourth** — hardens Beta surface once core mechanics are in place

### ✅ `spine check before-pr` — preflight checkpoint (#31)
**Status:** DONE — implemented in PR #35 (2026-04-08)

### ✅ Handoff/PR-prep summary primitive (#32)
**Status:** DONE — implemented in PR #39 (2026-04-08)

### ✅ Draftable governance records (#33)
**Description:** Draft evidence/decisions with explicit operator confirm before becoming canonical.
**Status:** DONE — implemented in PR #40 (2026-04-08)

### ✅ Local optional hook/checkpoint integration (#34)
**Description:** `spine hooks install/list/uninstall` — opt-in pre-push hook wiring.
**Why it matters:** Operators who want enforcement can opt in without daemon or cloud dependency.
**Status:** DONE — implemented in PR #41 (2026-04-08)

### 📋 Mission refine draft flow (#36)
**Description:** `spine mission refine` — explicit operator-invoked refinement producing draft mission.
**Status:** QUEUED — after #34

### 📋 Compatibility/integration guide (#37)
**Description:** Public guide for SPINE + Claude Code / oh-my-claudecode / Superpowers layering.
**Status:** QUEUED — after #36

### 📋 Deterministic validation fixtures (#38)
**Description:** Fixture harness for repeatable command/file/contract validation.
**Status:** QUEUED — after #36

---

## Phase 3B Candidates

> Preserved inputs. Not active work. These are potential Phase 3B directions — not all will become issues.

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

*Last updated: 2026-04-08 by SPINE Repo Manager Agent*
