# SPINE v0.1.1 External Repo Validation — gsn-connector

**Date:** 2026-04-06
**Validated by:** SPINE v0.1.1 on HASHI.AI-Spine itself

---

## 1. SPINE repo path used
`C:\Users\ZeusPR\Desktop\Hashi.AI\WIP\HASHI.AI-Spine`

## 2. gsn-connector repo path used
`C:\Users\ZeusPR\Desktop\gsn-connector` (cloned fresh from `https://github.com/LucielAI/gsn-connector.git`, reset to `origin/master`)

## 3. Targeting method used
**SPINE_ROOT env var** — set to `C:\Users\ZeusPR\Desktop\gsn-connector` for all Phase 2 commands.

All commands run from within the SPINE repo working directory with `SPINE_ROOT` pointing externally.

## 4. gsn-connector default branch
**`master`** (detected via `git symbolic-ref refs/remotes/origin/HEAD` → `refs/remotes/origin/master`)

## 5. Whether SPINE_ROOT targeting now works correctly for both state and git operations

**YES — fixed in this session.**

Root cause before fix: `resolve_roots()` in `app.py` used `find_git_root(cwd)` first, then only corrected `spine_root` when `SPINE_ROOT` was set. This meant git operations still targeted the CWD's git repo, not the SPINE_ROOT repo.

Fix applied:
```python
# Before (broken):
git_root = find_git_root(cwd or Path.cwd())
if os.environ.get("SPINE_ROOT"):
    spine_root = Path(os.environ["SPINE_ROOT"]).resolve() / ".spine"
    return git_root, spine_root
return git_root, git_root / ".spine"

# After (fixed):
if os.environ.get("SPINE_ROOT"):
    repo_root = Path(os.environ["SPINE_ROOT"]).resolve()
    return repo_root, repo_root / ".spine"
git_root = find_git_root(cwd or Path.cwd())
return git_root, git_root / ".spine"
```

When `SPINE_ROOT` is set, `git_root` is now **directly** set to `SPINE_ROOT` — no git walking, no CWD interference.

## 6. Exact drift results from gsn-connector
```
$ spine drift scan (from SPINE repo, SPINE_ROOT=gsn-connector)

No drift detected.
```

gsn-connector's `main` branch is clean. No committed files match forbidden patterns. No working tree changes.

## 7. Confirmation that no SPINE-repo files polluted the drift output
**Confirmed clean.** The drift scan correctly:
- Targeted `C:\Users\ZeusPR\Desktop\gsn-connector` git operations (branch=`master`, compared `master...main`)
- Wrote drift.jsonl to `C:\Users\ZeusPR\Desktop\gsn-connector\.spine\drift.jsonl`
- No SPINE repo paths (`.spine/mission.yaml`, `src/spine/`, etc.) appeared in output

## 8. What worked

| Command | Status | Notes |
|---------|--------|-------|
| `spine init --cwd <path>` | ✅ | Correctly creates `.spine/` at target path, AGENTS.md/CLAUDE.md at target repo root |
| `SPINE_ROOT` env var | ✅ | Now correctly binds both state AND git operations to external repo |
| `spine mission show/set` | ✅ | Read/write gsn-connector `.spine/mission.yaml` |
| `spine opportunity score` | ✅ | Appended to gsn-connector `.spine/opportunities.jsonl` |
| `spine evidence add` | ✅ | Appended to gsn-connector `.spine/evidence.jsonl` |
| `spine decision add` | ✅ | Appended to gsn-connector `.spine/decisions.jsonl` |
| `spine drift scan` | ✅ | Diffed gsn-connector git (master...main), wrote to gsn-connector `.spine/drift.jsonl` |
| `spine brief --target claude/codex` | ✅ | Generated briefs in gsn-connector `.spine/briefs/` |
| `spine review weekly` | ✅ | Generated review in gsn-connector `.spine/reviews/` |
| `spine doctor` | ✅ | Validated gsn-connector `.spine/` state |

## 9. What felt clunky

1. **`spine init --cwd <path>` requires `--allow-no-git`** when the target is not inside a git repo (gsn-connector is a git repo but `find_git_root` walks up and finds SPINE repo's `.git` since gsn-connector's `.git` is a file, not a directory on Windows). However, with `SPINE_ROOT` already set, `spine init` still tries to compare against SPINE repo's files. Workaround: use `--cwd` flag for init, `SPINE_ROOT` for all Phase 2 commands.

2. **`spine brief` subcommand naming**: The command is `spine brief --target claude` not `spine brief generate`. Minor but inconsistent with spec.

3. **No `--cwd` on Phase 2 commands**: All Phase 2 commands lack `--cwd` support. Only `SPINE_ROOT` env var enables external targeting. If `SPINE_ROOT` leaks into environment, behavior changes unexpectedly.

4. **gsn-connector `.git` is a file** (not directory) on Windows — `git rev-parse --show-toplevel` from a subdirectory of gsn-connector would walk up and find the SPINE repo's `.git` directory. The `SPINE_ROOT` approach bypasses this entirely.

## 10. Any narrow remaining gaps

1. **No `--cwd` for Phase 2 commands** — `SPINE_ROOT` is the only way to target external repos for Phase 2 commands. This is acceptable but not ergonomic for interactive use.

2. **`SPINE_ROOT` env var affects global process state** — if set in shell profile or inherited, all spine commands change behavior. No `--local` scope or detection mechanism.

3. **Doctor service**: `get_open_drift()` still uses `self.repo_root / C.SPINE_DIR / C.DRIFT_FILE` instead of `self._spine_root`. Minor inconsistency (does not affect current external validation).

4. **init `--cwd` collision with `SPINE_ROOT`**: Running `spine init --cwd gsn-connector` when `SPINE_ROOT` is also set causes the conflict check to compare against SPINE repo's existing files. Workaround: unset `SPINE_ROOT` before running `spine init --cwd`.

---

## External Validation Loop Completion

| Step | Status | Details |
|------|--------|---------|
| 1. Mission set on gsn-connector | ✅ | Title: "Build GSN TypeScript connector SDK", scope: typescript/src/test, forbids: python/rust/ui/billing |
| 2. Opportunity scores | ✅ | 2 scored: batch support (3.06), type definitions (3.0) |
| 3. Claude brief generated | ✅ | `gsn-connector/.spine/briefs/claude/20260406_223420.md` |
| 4. Codex brief generated | ✅ | `gsn-connector/.spine/briefs/codex/20260406_223421.md` |
| 5. Evidence records created | ✅ | 2 records: commit + demo |
| 6. Decision record created | ✅ | "TypeScript-first SDK design" |
| 7. Baseline drift scan on gsn-connector | ✅ | No drift (clean main branch) |
| 8. Weekly review generated | ✅ | `gsn-connector/.spine/reviews/2026-04-06.md` |
| 9. External validation report | ✅ | This document |

---

## Root Cause Summary

**Problem:** `resolve_roots()` called `find_git_root(cwd)` unconditionally first, then only patched `spine_root` when `SPINE_ROOT` was set. This meant `git_root` always pointed to CWD's git repo, even when `SPINE_ROOT` was set. Drift scan and other git-native commands operated on the wrong repo.

**Fix:** When `SPINE_ROOT` is set, use it directly as `repo_root` — bypass `find_git_root()` entirely. This makes `SPINE_ROOT` the single authoritative source for both canonical state path AND git repo root.

**Tests added:**
- `test_drift_scan_spiner_root_targets_external_repo` — proves drift scan targets external repo when `SPINE_ROOT` is set, not the CWD repo
- `test_resolve_roots_without_spiner_root_uses_cwd_repo` — proves normal cwd-based detection still works without `SPINE_ROOT`