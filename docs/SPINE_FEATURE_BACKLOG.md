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

### ✅ Artifact ergonomics contract (#23)
**Description:** Machine-readable artifact manifest, canonical naming, discoverable artifacts.
**Status:** DONE — implemented in PR #27 (2026-04-07)

### ✅ External-repo onboarding docs (#24)
**Description:** Practical guide for using SPINE in an arbitrary external repo. Created docs/external-repo-onboarding.md.
**Status:** DONE — implemented in PR #28 (2026-04-07)
**Description:** Practical guide for using SPINE in an arbitrary external repo.
**Status:** IN QUEUE — Alpha Exit

### ✅ Alpha-exit validation gate matrix (#25)
**Description:** 21 gates assessed, 20 pass, 1 non-blocking partial. Alpha exit validated.
**Status:** DONE — implemented in PR #29 (2026-04-07)

---

## Beta — v0.2.0-beta Active Issues

> Beta milestone — Phase 3B. Issues execute in order: #31 first, then #32–#34.

### ✅ `spine check before-pr` — preflight checkpoint (#31)
**Description:** Bounded preflight checkpoint command. Exit 0=pass, exit 1=review recommended. Local, explicit, operator-controlled.
**Status:** DONE — implemented in PR #35 (2026-04-08)

### ✅ Handoff/PR-prep summary primitive (#32)
**Description:** `spine review handoff` — generates human-readable governance summary for PR context.
**Status:** DONE — implemented in PR #39 (2026-04-08)

### 📋 Draftable governance records (#33)
**Description:** Draft evidence/decisions with explicit operator confirm before becoming canonical.
**Why it matters:** Reduces governance friction — provisional entries without silently mutating truth.
**Status:** QUEUED — after #32

### 📋 Local optional hook/checkpoint integration (#34)
**Description:** `spine hooks install/list/uninstall` — opt-in pre-PR hook wiring.
**Why it matters:** Operators who want enforcement can opt in without daemon or cloud dependency.
**Status:** QUEUED — after #33

### 📋 Mission refine draft flow (#36)
**Description:** `spine mission refine` — explicit operator-invoked refinement producing draft mission.
**Status:** QUEUED — Phase 3B candidate, after hook integration

### 📋 Compatibility/integration guide (#37)
**Description:** Public guide for SPINE + Claude Code / oh-my-claudecode / Superpowers layering.
**Status:** QUEUED — Phase 3B candidate, docs-only

### 📋 Deterministic validation fixtures (#38)
**Description:** Fixture harness for repeatable command/file/contract validation.
**Status:** QUEUED — Phase 3B candidate, after hook integration
**Description:** `spine brief handoff` — generates human-readable governance summary for PR context.
**Why it matters:** Next operator or reviewer can understand governance state without reading raw JSONL.
**Status:** QUEUED — after #31

### 📋 Draftable governance records (#33)
**Description:** Draft evidence/decisions with explicit operator confirm before becoming canonical.
**Why it matters:** Reduces governance friction — provisional entries without silently mutating truth.
**Status:** QUEUED — after #32

### 📋 Local optional hook/checkpoint integration (#34)
**Description:** `spine hooks install/list/uninstall` — opt-in pre-PR hook wiring.
**Why it matters:** Operators who want enforcement can opt in without daemon or cloud dependency.
**Status:** QUEUED — after #33

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
