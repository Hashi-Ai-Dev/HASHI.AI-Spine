# SPINE Feature Backlog

Grouped by target milestone. Each item: title, short description, why it matters, status.

---

## v0.1.2 — Stabilization

### ✅ Add `--cwd` support to Phase 2 commands
**Status:** DONE — PR #11

### ✅ Add minimal CI pipeline
**Status:** DONE — PR #12

### ✅ Clarify onboarding / quickstart docs
**Status:** DONE — PR #13

---

## Alpha Exit — v0.2.0-beta (Released 2026-04-07)

### ✅ All Phase 3A items (#15–#18, #23–#25)
**Status:** DONE — PRs #19–#29

---

## Beta — v0.2.0-beta

### ✅ `spine check before-pr` preflight checkpoint (#31)
**Status:** DONE — PR #35

### ✅ Handoff/PR-prep summary primitive (#32)
**Status:** DONE — PR #39

### ✅ Draftable governance records (#33)
**Status:** DONE — PR #40

### ✅ Local optional hook/checkpoint integration (#34)
**Status:** DONE — PR #41

### ✅ Beta blocker stabilization (#43, #44, #45)
**Status:** DONE — PR #46

### ✅ Mission refine draft flow (#36)
**Description:** `spine mission refine [--cwd]` creates a draft mission at `.spine/drafts/missions/<timestamp>.yaml`. Explicit `spine mission confirm <draft_id>` promotes to canonical. No silent mutation.
**Status:** DONE — branch `beta/issue36-mission-refine-draft-flow`

### 📋 Compatibility/integration guide (#37)
**Description:** Public guide for SPINE + Claude Code / oh-my-claudecode / Superpowers layering.
**Status:** NEXT — after #36

### 📋 Deterministic validation fixtures (#38)
**Description:** Fixture harness for repeatable command/file/contract validation.
**Status:** QUEUED — after #37

---

## Phase 3B Candidates

### 🟡 Stronger local tool-consumption surfaces
**Status:** CANDIDATE — Phase 3B

### 🟡 Optional governance profiles
**Status:** CANDIDATE — Phase 3B, optional

### 🚫 HUD / live observability mode
**Status:** REJECTED

### 🚫 Notification / webhook systems
**Status:** REJECTED

---

*Last updated: 2026-04-08 by SPINE Repo Manager Agent*
