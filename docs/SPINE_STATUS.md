# SPINE Status

**Last updated:** 2026-04-07 (Phase 3A planning normalization — Issue #10)
**Repo:** `Hashi-Ai-Dev/SPINE`
**Agent:** SPINE Repo Manager

---

## Current Release

| | |
|---|---|
| **Version** | `v0.1.2` |
| **Status** | ✅ Stabilization complete — tag pending |
| **Previous** | `v0.1.1-alpha` (2026-04-07) |
| **Tag** | Pending — stabilization done, release to be published |

---

## Current Phase

**Phase 1 + 2 Complete.** Full governance command suite implemented:
- `spine init` — mission bootstrapping
- `spine mission show/set` — mission management
- `spine brief --target <claude|codex>` — brief generation
- `spine evidence add` — evidence logging
- `spine decision add` — decision logging
- `spine opportunity score` — deterministic opportunity scoring
- `spine drift scan` — scope drift detection
- `spine review weekly` — weekly review generation
- `spine doctor` — environment and state validation
- `spine mcp serve` — stdio MCP server

Phase 1 + 2 = stable core. 136+ tests passing.

---

## v0.1.2 Stabilization — Complete ✅

| # | Item | Status |
|---|------|--------|
| 1 | Add `--cwd` to Phase 2 commands | ✅ Done (PR #11) |
| 2 | Enable Dependabot alerts + secret scanning | ✅ Done (owner via GitHub settings) |
| 3 | Add minimal CI pipeline | ✅ Done (PR #12 — ruff + pytest) |
| 4 | ~~Create org-level ruleset~~ | ❌ Rejected — not a SPINE issue |
| 5 | Clarify onboarding / README polish | ✅ Done (PR #13 — README + quickstart) |

Tests: **136+** passing.

---

## Next Active Phase

**Phase 3A / v0.2 — Portability + operator polish** — planning only, not implementation.

Phase 3A spec normalized 2026-04-07 at `docs/SPINE_PHASE3A_v0.2_SPEC.md`. Planning normalization (Issue #10) complete. Implementation requires human review and explicit approval before beginning.

---

## Branch / Release State

| | |
|---|---|
| **Default branch** | `main` (protected) |
| **Branch protection** | PR required + CI status checks + force-push blocked + delete blocked |
| **Open PRs** | None |
| **Open branches** | `main` only |
| **Releases** | `v0.1.1-alpha` (published) · `v0.1.2` pending |
| **Milestone** | `v0.1.2` — closed |

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

*Next status review: after v0.1.2 release is published*
