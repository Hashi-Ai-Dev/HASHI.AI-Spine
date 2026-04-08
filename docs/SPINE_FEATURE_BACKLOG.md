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

> ⚠️ **BLOCKERS found in shipped Beta features (Beta Bug Hunt audit, PR #42):**
> - **#43** — `check before-pr` exits 1 on healthy repos (A-01) — regression in #31
> - **#44** — hook script missing `uv run` (A-02) — regression in #34
> - **#45** — AGENTS.md template has invalid commands (A-06) — shipped to users
>
> Fix these regressions before shipping more Beta features.

### ✅ `spine check before-pr` preflight checkpoint (#31)
**Status:** DONE — PR #35

### ✅ Handoff/PR-prep summary primitive (#32)
**Status:** DONE — PR #39

### ✅ Draftable governance records (#33)
**Status:** DONE — PR #40

### ✅ Local optional hook/checkpoint integration (#34)
**Status:** DONE — PR #41

### 📋 Mission refine draft flow (#36)
**Status:** QUEUED — after blockers fixed

### 📋 Compatibility/integration guide (#37)
**Description:** Public guide for SPINE + Claude Code / oh-my-claudecode / Superpowers layering.
**Status:** QUEUED — after #36

### 📋 Deterministic validation fixtures (#38)
**Description:** Fixture harness for repeatable command/file/contract validation.
**Status:** QUEUED — after #36

### ✅ Write-flow machine-readable consistency (#49)
**Description:** `--json` output for all write-oriented commands: `evidence add`, `decision add`, `drafts list`, `drafts confirm`, `mission refine`, `mission confirm`, `mission drafts`. Exit codes unchanged. 37 focused contract tests added.
**Status:** DONE — branch beta/issue49-write-flow-machine-readable-consistency

### 📋 Before-work / start-session checkpoint (#50)
**Description:** Agent session start checkpoint to anchor context and confirm mission alignment.
**Status:** QUEUED — after #49

### 📋 Beta-exit repeated-use proof (#51)
**Description:** Proof harness for repeated Beta use across multiple agent sessions.
**Status:** QUEUED — after #49

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

*Last updated: 2026-04-08 — Issue #49 in review (PR #53)*
