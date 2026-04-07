# SPINE Status

**Last updated:** 2026-04-07
**Repo:** `Hashi-Ai-Dev/SPINE`
**Agent:** SPINE Repo Manager

---

## Current Release

| | |
|---|---|
| **Version** | `v0.1.1-alpha` |
| **Published** | 2026-04-07 |
| **Tag** | `v0.1.1-alpha` at commit `3f2b3ef` |
| **Type** | Public alpha (prerelease) |
| **Next target** | `v0.1.2` |

---

## Current Phase

**Phase 2 Complete.** Full governance command suite implemented:
- `spine init` — mission bootstrapping
- `spine brief` — current mission display
- `spine doctor` — environment validation
- `spine mission` — goal check
- `spine proof` — artifact manifest
- `spine decision` — decision logger
- `spine drift` — deviation detection

Phase 1 + 2 = stable core. No known critical bugs. Alpha smoke test: 120+ tests passing.

---

## Current Milestone

**`v0.1.2 — Stabilization** (in progress — 4/5 done)

| # | Item | Status |
|---|------|--------|
| 1 | Add `--cwd` to Phase 2 commands | ✅ Done (PR #11 merged) |
| 2 | Enable Dependabot alerts + secret scanning | ✅ Done (owner via GitHub settings) |
| 3 | Add minimal CI pipeline | ✅ Done (PR #12 merged — ruff + pytest) |
| 4 | ~~Create org-level ruleset~~ | ❌ Not a SPINE issue — removed |
| 5 | Clarify onboarding docs | 🔄 Pending — Issue #9 |

Tests now at **136+** (CI runs on every push/PR).

---

## Current Blockers

None.

---

## Next Move

**README / onboarding polish** (Issue #9) — the last remaining v0.1.2 item.

Once done: close #9, tag `v0.1.2`, publish release.

---

## Branch / Release State

| | |
|---|---|
| **Default branch** | `main` (protected) |
| **Branch protection** | PR required + CI status checks + force-push blocked + delete blocked |
| **Open PRs** | None |
| **Open branches** | `main` only |
| **Releases** | `v0.1.1-alpha` (published) |
| **CI pipeline** | ✅ Active — `ci.yml` (ruff + pytest on push/PR) |

---

## Phase 3A Planning Status

**Phase 3A spec** exists at `docs/SPINE_PHASE3A_v0.2_SPEC.md` — committed to repo.

Planning status: ✅ Spec exists. **Requires human review and approval before implementation begins.**

See GitHub issue #10 for the Phase 3A planning tracking issue.

---

## Repo Health

| Check | Status |
|-------|--------|
| README | ✅ Clean, public-alpha appropriate |
| LICENSE | ✅ MIT |
| SECURITY.md | ✅ Contact + policy |
| Branch protection | ✅ `main` protected + CI required |
| CI pipeline | ✅ Active (ruff + pytest) |
| Dependabot alerts | ✅ Enabled |
| Secret scanning | ✅ Enabled |

---

*Next status review: when v0.1.2 is ready for release*
