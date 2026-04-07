# SPINE v0.1.1-alpha — PR Body Draft

## Title
`feat: SPINE v0.1.1-alpha — Phase 2 complete + external targeting fix`

## Body

```markdown
## Summary

SPINE v0.1.1-alpha is the first public alpha release, representing Phase 2 completion:

- **External targeting fix**: `SPINE_ROOT` env var now correctly binds both canonical state AND git-native operations to the same external repo (was previously only binding state, not git operations)
- **Full Phase 2 command surface**: `mission show/set`, `opportunity score`, `evidence add`, `decision add`, `drift scan` (Mode A + B), `brief --target`, `review weekly`, `doctor`, `mcp serve`
- **Machine-readable output**: `--json` flags on `mission show`, `doctor`, `review weekly`
- **Artifact hygiene**: `latest.md` aliases for briefs and reviews, same-day review regeneration always fresh
- **Branch context**: `spine doctor` now shows `repo:` and `branch:` context line

## What's New

| Feature | PR/Commit |
|---------|-----------|
| External targeting fix (`resolve_roots()`) | #current |
| `spine mission show --json` | #current |
| `spine doctor --json` + branch context | #current |
| `spine review weekly --json` + `ReviewResult` dataclass | #current |
| Brief `latest.md` always updated | #current |
| Review `force=True` same-day regeneration | #current |
| `get_current_branch()` helper | #current |
| External targeting tests | #current |

## Validation

- Self-dogfood: full governance loop on SPINE's own repo ✅
- External repo (gsn-connector): `SPINE_ROOT` targeting verified, no SPINE-repo pollution ✅
- Smoke test: 11 commands on fresh external repo, all pass ✅
- Test suite: **122 passed, 1 skipped** (Windows SIGINT — not a real failure)

## Alpha Scope

**In:** Phase 1 (`spine init`) + Phase 2 (all governance commands) + MCP stdio server

**Out (intentionally):** Dashboard UI, auth, billing, cloud sync, remote MCP, daemon, multi-user, live model dependency, autonomous orchestration

## Test plan

- [x] `uv run pytest` — 122 passed
- [x] `spine init --cwd <fresh-repo>` — creates `.spine/` correctly
- [x] `spine mission show` + `mission set` — state persists
- [x] `spine brief --target claude` — brief + `latest.md` created
- [x] `spine doctor` — validates `.spine/` state
- [x] `spine drift scan` — git-native detection works
- [x] `spine review weekly` — review + `latest.md` created
- [x] `SPINE_ROOT=<external-repo> spine doctor` — external targeting works

---

Generated with [Claude Code](https://claude.com/claude-code)
```

---

## Notes for human

- The `main` branch is at `ffd2075` (Phase 2 complete, validated)
- `prep/v0.1.1-alpha` has all the integration work on top
- After merge, tag as `v0.1.1-alpha` and create GitHub release with `docs/SPINE_PUBLIC_ALPHA_RELEASE_NOTES_DRAFT.md` as the body