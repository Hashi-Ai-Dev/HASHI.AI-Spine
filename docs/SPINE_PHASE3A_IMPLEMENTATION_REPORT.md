# SPINE Phase 3A Implementation Report — Issue #23

**Issue:** #23 — Alpha Exit: Artifact ergonomics contract  
**Branch:** `claude/artifact-ergonomics-issue23-CVn57`  
**Date:** 2026-04-07  
**Status:** Complete

---

## Issue Targeted

Issue #23 — Formalize the artifact ergonomics contract for SPINE governance
artifacts. Goal: make generated artifacts easy to find, predictable in naming,
scriptable, and explicit about current vs historical.

---

## Artifact Contract Implemented

### Naming conventions (formalized, not changed)

| Artifact | Location | Naming pattern | Note |
|----------|----------|----------------|------|
| Brief (claude) | `.spine/briefs/claude/` | `YYYYMMDD_HHMMSS.md` | timestamped, history preserved |
| Brief (codex) | `.spine/briefs/codex/` | `YYYYMMDD_HHMMSS.md` | timestamped, history preserved |
| Review (weekly) | `.spine/reviews/` | `YYYY-MM-DD.md` | dated, same-day overwrites |
| Brief latest | `.spine/briefs/{target}/latest.md` | `latest.md` | regular file, always current |
| Review latest | `.spine/reviews/latest.md` | `latest.md` | regular file, always current |
| Evidence log | `.spine/evidence.jsonl` | append-only JSONL | per-record ISO 8601 timestamps |
| Decisions log | `.spine/decisions.jsonl` | append-only JSONL | per-record ISO 8601 timestamps |

### Canonical vs historical distinction

- **Latest/current:** `latest.md` in each artifact directory — a regular file
  (not a symlink) overwritten on each generation. Stable path, always reflects
  the most recent generation.
- **Historical:** timestamped / dated canonical files accumulate in the same
  directory. Never deleted. Discoverable by glob (`*.md` minus `latest.md`).
- **No draft concept:** SPINE does not have a draft/staging workflow. All
  generated artifacts are immediately canonical. Draft distinction deferred to
  future phases if ever needed.

### Machine-readable artifact manifest

**`.spine/artifact_manifest.json`** — created and updated on each brief or
review generation. Format:

```json
{
  "contract_version": "1",
  "briefs": {
    "claude": {
      "latest": ".spine/briefs/claude/latest.md",
      "last_generated_at": "2026-04-07T22:00:00+00:00"
    },
    "codex": {
      "latest": ".spine/briefs/codex/latest.md",
      "last_generated_at": "2026-04-07T22:00:00+00:00"
    }
  },
  "reviews": {
    "weekly": {
      "latest": ".spine/reviews/latest.md",
      "last_generated_at": "2026-04-07T22:00:00+00:00"
    }
  }
}
```

Properties:
- All `latest` paths are **relative to repo root** (portable across checkouts)
- `last_generated_at` is ISO 8601 with UTC timezone
- `contract_version` is `"1"` — enables future format evolution
- Written atomically (overwrite) — always reflects current state
- Evidence and decisions are JSONL already (machine-readable natively); no
  manifest entry needed for them

### CLI JSON output (existing, verified)

Both `spine brief --json` and `spine review weekly --json` output
`canonical_path` and `latest_path` (absolute), enabling scripted artifact
consumption without filesystem inspection.

---

## Files Changed

### New files
- `tests/test_artifact_contract.py` — 18 focused tests for the artifact contract

### Modified files
- `src/spine/constants.py` — added `ARTIFACT_MANIFEST_FILE = "artifact_manifest.json"`
- `src/spine/utils/io.py` — added `update_artifact_manifest()` helper
- `src/spine/services/brief_service.py` — calls `update_artifact_manifest()` after
  each claude/codex brief generation
- `src/spine/services/review_service.py` — calls `update_artifact_manifest()` after
  each weekly review generation
- `docs/SPINE_STATUS.md` — marked #23 as done, updated next priority to #24
- `docs/SPINE_FEATURE_BACKLOG.md` — marked #23 as done with description
- `docs/SPINE_PHASE3A_v0.2_SPEC.md` — updated implementation state header

---

## Test Results

| | |
|---|---|
| New tests | 18 |
| Total passing | 231 |
| Total failing | 0 |

New test coverage in `tests/test_artifact_contract.py`:
- Brief canonical name matches `YYYYMMDD_HHMMSS.md` pattern
- Brief `latest.md` is a regular file (not symlink)
- Review canonical name matches `YYYY-MM-DD.md` pattern
- Review `latest.md` is a regular file (not symlink)
- `artifact_manifest.json` created on brief generation
- Manifest has `contract_version`, `briefs.{target}.latest`, `briefs.{target}.last_generated_at`
- Manifest latest paths are relative (portable)
- Manifest accumulates claude + codex entries independently
- `last_generated_at` is timezone-aware ISO 8601
- Review generation creates `reviews.weekly` manifest entry
- Brief + review entries coexist in manifest
- `brief --json` includes `canonical_path` and `latest_path`
- `review weekly --json` includes `canonical_path` and `latest_path`
- JSON canonical paths match expected naming patterns

---

## SPINE Commands Run

```bash
uv run spine doctor                    # passed with warnings (expected)
uv run spine mission show              # confirmed mission state
uv run spine decision add              # Issue #23 decision recorded
uv run spine evidence add --kind commit  # implementation evidence recorded
uv run spine review weekly --recommendation continue --notes "..."
```

---

## Explicitly Deferred

The following are explicitly **not** implemented in this PR:

| Item | Deferred to |
|------|-------------|
| External-repo onboarding docs | Issue #24 |
| Alpha-exit validation gate matrix | Issue #25 |
| Draft/staging artifact workflow | Not planned (no current need) |
| Database-backed artifact catalog | Non-goal (Phase 3A spec section 3) |
| Artifact indexing or search UI | Non-goal (Phase 3A spec section 3) |
| Branch-local governance lanes | Not in scope |
| Cloud sync or remote artifact storage | Non-goal (permanent) |

---

## Assessment

Issue #23 is **fully addressed** within its defined scope. The artifact
ergonomics contract is now:

1. **Explicit** — naming patterns documented and tested
2. **Deterministic** — `YYYYMMDD_HHMMSS.md` for briefs, `YYYY-MM-DD.md` for reviews
3. **Machine-readable** — `artifact_manifest.json` with stable relative paths
4. **Discoverable** — `latest.md` always points to current artifact
5. **Scriptable** — `--json` output includes `canonical_path` + `latest_path`
6. **Compatible** — no existing artifact history broken; all changes additive
