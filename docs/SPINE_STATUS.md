# SPINE Project Status

**Last updated:** 2026-04-06  
**Branch context:** This file tracks internal project state. External validation is handled separately.

---

## Current Project State

SPINE v0.1 / v0.1.1 is in post-Phase-2 hardening. The core governance loop is implemented and self-dogfooded. External validation is in progress on a separate lane.

This branch (`claude/dogfood-phase3a-polish-zHDuu`) is an **internal Phase 3A dogfood slice only**. It is not the external-validation lane and may or may not be merged.

---

## Completed Phases / Milestones

| Milestone | Status | Notes |
|-----------|--------|-------|
| Phase 1: `spine init` | Complete | Bootstraps `.spine/` governance contract |
| Phase 2: Core CLI + MCP | Complete | Full command surface implemented and tested |
| v0.1.1 Hardening | Complete | Self-dogfood pass, doc cleanup, test fixes |
| Phase 3A Spec (v0.2) | Complete | Planning doc exists at `docs/SPINE_PHASE3A_v0.2_SPEC.md` |
| Phase 3A Internal Dogfood | In progress | This branch — narrow operator polish slice only |

---

## Current Blocker

**External validation gate not yet cleared.**

A separate lane is handling real-world external repo validation. Until that succeeds, Phase 3A is not considered production-ready. Internal dogfood work (this branch) is exploratory and reference quality only.

---

## Current Release Gate

Phase 3A is not released. No public release is imminent.

Release gate requirements (not yet met):
- External validation succeeds on at least one non-SPINE repo
- All Phase 3A acceptance criteria from `SPINE_PHASE3A_v0.2_SPEC.md` are met
- `uv run pytest` passes with zero failures on the release commit

---

## Implemented Command Surface (Phase 2)

All commands below are implemented and tested:

| Command | Purpose |
|---------|---------|
| `spine init` | Bootstrap `.spine/` governance state |
| `spine mission show` | Display current mission |
| `spine mission set` | Update mission fields |
| `spine opportunity score` | Deterministic opportunity scoring |
| `spine brief --target claude` | Generate Claude-targeted brief |
| `spine brief --target codex` | Generate Codex-targeted brief |
| `spine evidence add` | Append evidence record |
| `spine decision add` | Append decision record |
| `spine drift scan` | Git-native drift detection |
| `spine review weekly` | Generate weekly review markdown |
| `spine doctor` | Validate `.spine/` state and repo contract |
| `spine mcp serve` | Blocking stdio MCP server |

---

## Next 3 Moves (Internal Dogfood Lane)

1. **Complete internal Phase 3A dogfood slice** — README polish, `--json` for `mission show`, repo/branch context in `doctor` output.
2. **Write and publish dogfood report** — `docs/SPINE_PHASE3A_INTERNAL_DOGFOOD_REPORT.md` capturing what worked and what still feels clunky.
3. **Wait for external validation lane result** — if it succeeds cleanly, this branch may be reviewed for merge; if not, it stands as reference only.

---

## Notes

- **External validation** is being handled on a separate lane (not this branch). Do not treat this branch as the external validation source of truth.
- **This branch is internal Phase 3A dogfooding only.** It is exploratory and serious but not automatically merge-ready.
- **Phase 4 work** (web UI, multi-user, cloud sync) is out of scope until Phase 3A is stable and the external validation gate is cleared.
