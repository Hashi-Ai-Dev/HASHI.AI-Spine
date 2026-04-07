# SPINE Status

**Version:** v0.1.1-alpha
**Updated:** 2026-04-06
**Branch:** `prep/v0.1.1-alpha`

---

## Current State: Alpha-Ready

SPINE has completed:
1. Self-dogfood validation on its own repo ✅
2. External repo validation on gsn-connector ✅
3. Integration pass (approved Phase3A polish slices) ✅
4. Smoke test from clean external repo ✅
5. Full test suite: 122 passed, 1 skipped ✅

---

## Command Surface

### Implemented (Phase 1 + Phase 2)

| Command | Status |
|---------|--------|
| `spine init` | ✅ |
| `spine mission show` | ✅ (--json) |
| `spine mission set` | ✅ |
| `spine opportunity score` | ✅ |
| `spine evidence add` | ✅ |
| `spine decision add` | ✅ |
| `spine drift scan` | ✅ |
| `spine brief --target` | ✅ (latest.md) |
| `spine review weekly` | ✅ (--json, latest.md, force=True) |
| `spine doctor` | ✅ (--json, branch context) |
| `spine mcp serve` | ✅ |

### External Targeting
- `SPINE_ROOT` env var: ✅ (binds both state AND git operations)
- `spine init --cwd`: ✅ (creates .spine/ at target path)

---

## Test Coverage

- **122 tests passing** (1 skipped — Windows SIGINT platform issue, not a failure)
- Tests cover: init, mission, opportunity, evidence, decision, drift, brief, review, doctor, MCP

---

## Known Rough Edges

1. No `--cwd` on Phase 2 commands (only `SPINE_ROOT` env var for external targeting)
2. `SPINE_ROOT` is process-global (no local/session scope)
3. `spine brief` naming vs spec (`--target` vs `generate`)
4. Doctor `get_open_drift()` minor path inconsistency
5. `spine init --cwd` conflict check uses git-root's files

---

## Next Steps

- Merge `prep/v0.1.1-alpha` → `main` for public alpha release
- Tag as `v0.1.1-alpha`
- Announce on GitHub

---

## Documentation

- `docs/SPINE_OFFICIAL_SPEC_v0.1.md` — authoritative spec
- `docs/SPINE_ORIGIN_AND_PRODUCT_THESIS_v0.1.md` — product thesis
- `docs/SPINE_v0.1.1_SELF_DOGFOOD_CLEANUP.md` — self-dogfood report
- `docs/SPINE_v0.1.1_EXTERNAL_REPO_VALIDATION_gsn_connector.md` — external validation
- `docs/SPINE_ALPHA_SMOKE_TEST_REPORT.md` — smoke test results
- `docs/SPINE_PUBLIC_ALPHA_RELEASE_NOTES_DRAFT.md` — release notes draft