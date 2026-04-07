# SPINE Phase 3A Implementation Report

**Last updated:** 2026-04-07  
**Author:** SPINE Repo Manager Agent  
**Branch:** `claude/phase3a-targeting-contract-YAHcW`

---

## Issue #15 — Explicit Repo Targeting Contract

**Phase:** 3A.2  
**Status:** Complete  
**Spec reference:** `docs/SPINE_PHASE3A_v0.2_SPEC.md` §5.1

---

### Problem

`resolve_roots()` was silently letting `SPINE_ROOT` override `--cwd`. When both were set, the explicitly-provided `--cwd` flag was ignored. This was the inverse of what operators expect: explicit > ambient. The result was:

- Operators who passed `--cwd` while `SPINE_ROOT` was set in their environment were silently targeting the wrong repo.
- Error messages did not explain what path was resolved or where it came from.
- `--cwd` help text was inconsistent and did not mention the precedence contract.

---

### Contract Chosen

**Target resolution precedence (highest to lowest):**

| Priority | Source | Condition |
|---|---|---|
| 1 | `--cwd <path>` | if explicitly provided at invocation time |
| 2 | `SPINE_ROOT` | if set in the environment and no `--cwd` given |
| 3 | current working directory | fallback default |

**Required behavior:**

- `--cwd` always wins over `SPINE_ROOT` when both are present.
- `SPINE_ROOT` path existence is validated; a clear error is raised if it does not exist.
- Commands requiring a git repo fail fast when the resolved target is not inside a git repository.
- All errors state: the resolved target path, which source produced it, and what the operator should do.

---

### Precedence Rules (exact)

```
if cwd is not None:           # --cwd explicitly provided
    target = cwd.resolve()
    source = f"--cwd {cwd}"
    git_root = find_git_root(target)      # raises with source in message if invalid
elif SPINE_ROOT is set:       # SPINE_ROOT in environment
    repo_root = Path(SPINE_ROOT).resolve()
    validate repo_root.exists()           # raises with SPINE_ROOT in message if missing
else:                         # default cwd
    git_root = find_git_root(Path.cwd())  # raises with "current working directory" if invalid
```

---

### Error Behavior

All `GitRepoNotFoundError` and `FileNotFoundError` messages from `resolve_roots()` now include:

1. **Resolved target path** — e.g., `No git repository found at or above: /path/to/foo`
2. **Source** — e.g., `Target source: --cwd /path/to/foo` or `SPINE_ROOT=/path/to/foo`
3. **Corrective action** — e.g., `Point --cwd at a valid git repository, or run 'git init' first.`

---

### Files Changed

| File | Change |
|---|---|
| `src/spine/cli/app.py` | Rewrote `resolve_roots()`: fixed precedence, added SPINE_ROOT existence validation, improved all error messages with source and corrective action |
| `src/spine/cli/doctor_cmd.py` | Updated `--cwd` help text |
| `src/spine/cli/mission_cmd.py` | Updated `--cwd` help text (show + set) |
| `src/spine/cli/evidence_cmd.py` | Updated `--cwd` help text |
| `src/spine/cli/decision_cmd.py` | Updated `--cwd` help text |
| `src/spine/cli/opportunity_cmd.py` | Updated `--cwd` help text |
| `src/spine/cli/drift_cmd.py` | Updated `--cwd` help text |
| `src/spine/cli/brief_cmd.py` | Updated `--cwd` help text |
| `src/spine/cli/review_cmd.py` | Updated `--cwd` help text |
| `src/spine/cli/mcp_cmd.py` | Updated `--cwd` help text |
| `src/spine/cli/init_cmd.py` | Updated `--cwd` help text |
| `tests/test_targeting_contract.py` | New: 11 targeting contract tests |
| `docs/SPINE_STATUS.md` | Marked #15 done, updated test count to 147 |
| `docs/SPINE_FEATURE_BACKLOG.md` | Marked #15 done with implementation summary |
| `docs/SPINE_PHASE3A_v0.2_SPEC.md` | Updated status, added implemented contract note to §5.1 |
| `README.md` | Added Targeting Contract section, updated test count |

---

### Test Results

**New tests (11):** `tests/test_targeting_contract.py`

| Test | Coverage |
|---|---|
| `test_resolve_roots_cwd_wins_over_spine_root` | --cwd overrides SPINE_ROOT in unit call |
| `test_resolve_roots_spine_root_wins_over_cwd_fallback` | SPINE_ROOT wins over default cwd |
| `test_resolve_roots_cwd_fallback_when_nothing_set` | Default cwd used when nothing set |
| `test_resolve_roots_invalid_cwd_not_a_git_repo` | Clear error when --cwd is not a git repo |
| `test_resolve_roots_invalid_spine_root_path_missing` | Clear error when SPINE_ROOT doesn't exist |
| `test_resolve_roots_no_repo_in_cwd` | Clear error when cwd has no git repo |
| `test_cli_cwd_overrides_spine_root` | CLI integration: --cwd beats SPINE_ROOT |
| `test_cli_spine_root_used_when_no_cwd` | CLI integration: SPINE_ROOT governs without --cwd |
| `test_cli_invalid_cwd_exit_code_and_message` | CLI exit 1 + useful message on invalid --cwd |
| `test_cli_invalid_spine_root_exit_code_and_message` | CLI exit 1 + SPINE_ROOT in message |
| `test_deterministic_targeting_multi_repo` | 3 side-by-side repos always target correctly |

**Full suite:** 147 passed, 0 failed (was 136 before this issue).

---

### SPINE Self-Governance Records

- **Decision:** `Standardise --cwd > SPINE_ROOT > cwd targeting contract (Issue #15)` — recorded 2026-04-07
- **Evidence:** `commit` — implementation evidence recorded 2026-04-07
- **Weekly review:** `continue` recommendation — 2026-04-07

---

### What Was Explicitly Deferred

The following are **out of scope for Issue #15** and belong to later Phase 3A issues:

| Deferred item | Issue |
|---|---|
| Repo/branch context visibility in command output (current branch, default branch) | #16 |
| Machine-readable `--json` output on all commands | #17 |
| Stable exit code documentation and `--quiet` mode | #17 |
| Bootstrap polish and first-run ergonomics | #18 |
| Repo discovery "magic" across parent directories | Deferred per spec |
| Multi-repo orchestration from a single invocation | Deferred per spec |

Rich branch/default-branch context reporting was intentionally not implemented here. Issue #16 will build on the stable targeting foundation established by this issue.

---

*End of Issue #15 implementation report.*
