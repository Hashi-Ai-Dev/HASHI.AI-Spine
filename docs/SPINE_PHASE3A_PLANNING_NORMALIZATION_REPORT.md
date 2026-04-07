# SPINE Phase 3A Planning Normalization Report

**Date:** 2026-04-07  
**Issue:** #10 — Phase 3A Planning / v0.2 spec and implementation scope  
**Branch:** `claude/docs-phase3a-v0.2-planning-53uew`  
**Type:** Planning-only pass. No code changes. No test changes. No feature implementation.

---

## 1. Context

v0.1.2 stabilization is complete. SPINE is in public alpha. The canonical spec and related planning docs contained stale bootstrap-era language that reflected Phase 1/2 as ongoing build gates rather than completed historical phases. Before any Phase 3A implementation begins, the internal documentation truth must match current reality.

This report documents what was found, what was corrected, and what is now the official next phase.

---

## 2. What Was Stale

### `docs/SPINE_OFFICIAL_SPEC_v0.1.md`

| Stale item | Problem |
|---|---|
| "Phase 2 (current) implements the core command surface" | Phase 2 is complete, not current |
| Development Phases table: `Phase 2 \| Current` | Should read Complete |
| Development Phases table: `Phase 3 \| Future \| SQLite projection, model-assisted scoring` | Phase 3A is now specifically "Portability + operator polish", not that vague description |
| Acceptance Criteria framed as current work | These were Phase 2 completion criteria — historical |
| Duplicate Severity Levels section in Drift Detection Rules | Copy-paste duplicate that created two identical blocks |
| No status note indicating public alpha / Phase 2 complete reality | Reader had no orientation to current state |

### `docs/SPINE_PHASE3A_v0.2_SPEC.md`

| Stale/missing item | Problem |
|---|---|
| No "Portability + operator polish" framing in title/header | Core phase identity not surfaced |
| No explicit discipline tax section | A key design lens was missing from the planning spec |
| Section numbering broken after existing sections | 4.x subsections inside old section 4, now section 5 |
| Milestone 3A.1 framed as spec finalization only | Did not account for the planning normalization pass happening now |
| "Relation to Current State" referenced v0.1.1 Self-Dogfood as primary motivation | Should reference the full current-state picture including v0.1.2 completion |
| Why Phase 3A Exists didn't mention v0.1.2 or discipline tax | Missing current context |

### `docs/SPINE_STATUS.md`

| Stale item | Problem |
|---|---|
| v0.1.2 Status: "🔄 Release in preparation" | Stabilization is complete; should read "Stabilization complete — tag pending" |
| Current Phase commands listed wrong CLI surface | Listed `spine brief`, `spine proof`, `spine decision`, `spine drift` — not matching actual CLI which uses `spine brief --target`, `spine evidence add`, `spine decision add`, `spine drift scan`, etc. |
| Phase 3A note didn't reflect planning normalization | Should note that Issue #10 planning pass is complete |

### `docs/SPINE_ROADMAP.md`

| Stale item | Problem |
|---|---|
| "Current stabilization target: v0.1.2" | v0.1.2 stabilization is done |
| v0.1.2 Milestone status: "🔄 Next" | Should read complete |
| v0.1.2 section said "Planned items" with future tense | All items are done |
| v0.2 description: "Expand command surface beyond Phase 2, implement Phase 3 architecture spec" | Should be "Portability + operator polish" |

### `docs/SPINE_FEATURE_BACKLOG.md`

| Stale item | Problem |
|---|---|
| v0.2 items were generic ("CLI surface expansion", "Phase 3 architecture implementation") | Didn't match Phase 3A actual scope |
| No discipline tax item in v0.2 | A major Phase 3A lens was absent |
| No portability-specific items | Backlog didn't reflect the portability + polish framing |

---

## 3. What Was Corrected

### `docs/SPINE_OFFICIAL_SPEC_v0.1.md`
- Added status note at top: public alpha, Phase 1+2 complete, Phase 3A is next
- Changed "Phase 2 (current)" → "Phase 2 (complete)" in the v0.1 Scope section
- Fixed Development Phases table: Phase 2 = Complete, Phase 3A = Planned (Portability + operator polish), Phase 3B+ and Phase 4+ properly deferred
- Renamed "Acceptance Criteria" → "v0.1 Acceptance Criteria (Historical — Phase 1 + 2 Complete)" with a forward reference to the Phase 3A spec
- Removed duplicate Severity Levels section

### `docs/SPINE_PHASE3A_v0.2_SPEC.md`
- Added "Portability + Operator Polish" as explicit subtitle
- Updated status block to reflect planning normalization date and next required step
- Added current-state context to "Why Phase 3A Exists" (v0.1.2 complete, discipline tax framing)
- Added Section 4: **Discipline Tax Lens** — defines the concept, explains what it means for Phase 3A design decisions, and links it explicitly to the scope items
- Renumbered all sections after the insertion (old 4→5, 5→6, 6→7, 7→8, 8→9, 9→10, 10→11)
- Updated subsection references (4.x → 5.x)
- Updated Milestone 3A.1 to note that the planning normalization pass is now in progress
- Updated "Relation to Current State" to reflect current v0.1.2-complete picture

### `docs/SPINE_STATUS.md`
- Fixed v0.1.2 status: "Release in preparation" → "Stabilization complete — tag pending"
- Fixed Current Phase commands list to match actual CLI surface
- Updated Next Active Phase note to reflect Issue #10 planning normalization complete

### `docs/SPINE_ROADMAP.md`
- Fixed Current Phase section to remove "current stabilization target" language
- Fixed v0.1.2 milestone status from "🔄 Next" to "✅ Stabilization complete — tag pending"
- Rewrote v0.1.2 scope items from future tense "Planned" to past tense "Completed"
- Rewrote v0.2/Phase 3A description to "Portability + Operator Polish" with correct scope items
- Updated footer

### `docs/SPINE_FEATURE_BACKLOG.md`
- Replaced generic v0.2 items with specific Phase 3A scope items matching `SPINE_PHASE3A_v0.2_SPEC.md`:
  - Explicit repo targeting
  - Repo context and branch visibility
  - Operator/CI output modes
  - Artifact naming and path conventions
  - **Discipline tax reduction (new explicit item)**
  - External-repo docs and usage examples
  - Bootstrap/install polish
  - Enhanced CI

### `.spine/` governance (SPINE tracking)
- `spine decision add`: Phase 3A planning normalization rationale recorded
- `spine evidence add`: Planning normalization completion recorded (kind: review_done)
- `spine review weekly --recommendation continue`: Weekly review generated at `.spine/reviews/2026-04-07.md`

---

## 4. What the Official Next Phase Now Is

**`v0.2 / Phase 3A — Portability + Operator Polish`**

Spec location: `docs/SPINE_PHASE3A_v0.2_SPEC.md`

Phase 3A is **specified and planning-normalized, not implementation-approved**.

Core focus:
1. Explicit repo targeting with clear error paths
2. Repo/branch/default-branch context visibility
3. Operator/CI output modes (`--json`, `--quiet`, stable exits)
4. Artifact naming and path convention standardization
5. Discipline tax reduction (ergonomics, defaults, ceremony reduction)
6. Bootstrap/install polish for non-SPINE repos
7. External-repo usage docs and examples

Any implementation requires separate human review and explicit approval.

---

## 5. Pre-Existing Issues Not In Scope

The following pre-existing gaps were observed but are out of scope for this planning-only pass:

| Issue | Status |
|---|---|
| `AGENTS.md` missing from repo root | Pre-existing. `spine doctor` reports ERROR. Out of scope for this pass. |
| `CLAUDE.md` missing from repo root | Pre-existing. `spine doctor` reports ERROR. Out of scope for this pass. |
| `docs/SPINE_ORIGIN_AND_PRODUCT_THESIS_v0.1.md` missing | Referenced in README, never created. Out of scope for this pass. |
| v0.1.2 tag not yet published | A human action. Not a doc issue. |

These should be addressed in a separate follow-on task before Phase 3A implementation begins.

---

## 6. What Remains Intentionally Deferred

The following are firm deferrals — not reconsidered in this pass, not to be added to Phase 3A:

- Dashboard / web UI / TUI visualization
- Remote MCP transport or hosting
- Cloud sync or hosted features
- Authentication, billing, account systems
- Multi-user / collaboration
- Autonomous orchestration or background agent loops
- Broad adapter expansion or plugin matrix
- Model-based scoring or required live-model dependencies
- Phase 3B+ architecture (SQLite projections, model-assisted scoring)
- Phase 4+ features (multi-mission, web UI, multi-user)

---

## 7. Summary

| Item | Result |
|---|---|
| Branch created | `claude/docs-phase3a-v0.2-planning-53uew` |
| `SPINE_OFFICIAL_SPEC_v0.1.md` matches current reality | ✅ Yes |
| `SPINE_PHASE3A_v0.2_SPEC.md` exists and is usable | ✅ Yes — normalized |
| STATUS/ROADMAP/BACKLOG aligned | ✅ Yes |
| SPINE CLI governance commands run | ✅ Yes |
| Code changes | ❌ None |
| Test changes | ❌ None |
| Feature implementation | ❌ None |
| Official next active phase | **v0.2 / Phase 3A — Portability + Operator Polish** |
| Implementation authorized | ❌ Not yet — requires human approval |
