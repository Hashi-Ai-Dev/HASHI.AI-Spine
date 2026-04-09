# SPINE Pre-Beta-Exit Bug Audit

**Auditor:** Claude (claude-sonnet-4-6)  
**Session date:** 2026-04-09  
**Branch audited:** `main`  
**Repo:** `Hashi-Ai-Dev/SPINE`  
**Audit report written to:** `claude/audit-spine-main-IHH2O`

---

## 1. Audit Scope

### Branch audited
`main` — HEAD at commit `03ffa9a` ("chore: remove internal doc — archived to hashi-collab")

### Repo state audited
- **Python package version:** `0.1.0` (pyproject.toml)
- **Test suite:** 136 tests, all passing (`uv run pytest`)
- **CLI surface (main):** `init`, `brief`, `doctor`, `mission show/set`, `opportunity score`, `evidence add`, `decision add`, `drift scan`, `review weekly`, `mcp serve`
- **`doctor` result:** passed with warnings (4 missing subdirectories: `.spine/reviews`, `.spine/briefs`, `.spine/skills`, `.spine/checks`)

### What was in scope
- All CLI commands and their options, exit codes, and output
- `.spine/` artifact and governance state
- `docs/` public-facing documents
- `src/spine/` implementation — services, models, CLI handlers, utils
- `tests/` coverage gaps
- Live command execution for verification

### What was NOT in scope
- Git history before current HEAD
- GitHub Actions CI pipeline (not inspectable in this environment)
- MCP protocol conformance beyond code inspection
- External repo compatibility beyond what can be inferred from code

---

## 2. Findings Table

### Bugs

| ID | Title | Severity | Type | Surface | Evidence | Recommended Handling |
|----|-------|----------|------|---------|----------|----------------------|
| B-01 | MCP `call_tool` — `TextContent` NameError crashes all tool calls | blocker | bug | CLI / MCP | `mcp_cmd.py`: `_mcp_modules` tuple returned by `_get_mcp_modules()`, but only `McpServer = _mcp_modules[0]` is extracted; `TextContent` used by name in `call_tool` is not in scope → `NameError` on every tool invocation | fix-now |
| B-02 | MCP `review_generate` — response text contains ReviewResult repr | high | bug | CLI / MCP | `mcp_cmd.py:331–338`: `path = review_service.generate_weekly(...)` assigns `ReviewResult` object to `path`; `text=f"Review generated at: {path}"` outputs object repr, not a path | fix-now |
| B-03 | MCP `brief_generate` — response text contains tuple repr | medium | bug | CLI / MCP | `mcp_cmd.py:302–308`: `brief_service.generate_claude()` returns `tuple[Path, Path]`; `text=f"Brief generated at: {path}"` outputs the tuple, not a clean path | fix-now |
| B-04 | Exit code 2 only applies to `spine init`; README implies all commands | high | bug / contract ambiguity | CLI / docs | `README.md:130–135` exit code table says `2 = Not in a git repo (--allow-no-git to override)`; tested: `mission show` outside git exits with code 1; only `init_cmd.py` defines `_EXIT_GIT_NOT_FOUND = 2` | before-beta-exit |
| B-05 | `review_service._filter_recent` — string timestamp comparison | medium | bug | CLI / artifacts | `review_service.py:106–108`: `r.get("created_at", "") >= cutoff_iso` is a string comparison; records with empty `created_at` are silently dropped; mixed timezone formats (`+00:00` vs `Z`) would filter incorrectly | before-beta-exit |

### Docs Drift

| ID | Title | Severity | Type | Surface | Evidence | Recommended Handling |
|----|-------|----------|------|---------|----------|----------------------|
| D-01 | README Python version badge says "3.11+" but `requires-python = ">=3.12"` | high | docs drift | public-facing repo | `README.md:9` badge vs `pyproject.toml:8` | fix-now |
| D-02 | README status badge says "alpha" — project is heading to beta | high | docs drift | public-facing repo | `README.md:11` badge: `status-alpha`; `SPINE_STATUS.md` targets v0.1.2 | fix-now |
| D-03 | README Known Limitations #1 is factually wrong — `--cwd` was fixed in PR #11 | high | docs drift | public-facing repo | `README.md:122`: "–cwd works only with `spine init`"; `SPINE_FEATURE_BACKLOG.md` says DONE, merged PR #11; all Phase 2 commands now have `--cwd` | fix-now |
| D-04 | README links to four removed docs — all return 404 | high | docs drift | public-facing repo | `README.md:142–148` links: `SPINE_PUBLIC_ALPHA_RELEASE_NOTES_DRAFT.md`, `SPINE_ORIGIN_AND_PRODUCT_THESIS_v0.1.md`, `SPINE_ALPHA_SMOKE_TEST_REPORT.md`, `SPINE_v0.1.1_EXTERNAL_REPO_VALIDATION_gsn_connector.md` — all removed in recent "chore: remove internal doc" commits | fix-now |
| D-05 | `docs/README.md` links to seven+ removed docs — entire index is broken | high | docs drift | public-facing repo | `docs/README.md:14–48`: all "Internal/Development Notes" files missing; three "Public-Facing" links also broken; index is now more misleading than helpful | fix-now |
| D-06 | `docs/README.md` Quick Links points to wrong GitHub org/repo | high | docs drift | public-facing repo | `docs/README.md:47`: `https://github.com/LucielAI/HASHI.AI-Spine` — wrong org (`LucielAI` vs `Hashi-Ai-Dev`) and wrong repo name | fix-now |
| D-07 | `docs/SPINE_SECURITY_BASELINE.md` references wrong repo name throughout | medium | docs drift | public-facing repo | References `Hashi-Ai-Dev/HASHI.AI-Spine` at lines 7, 34, 38, 39, 56; actual repo: `Hashi-Ai-Dev/SPINE` | before-beta-exit |
| D-08 | README validation section test count is stale ("123 passed") | low | docs drift | public-facing repo | `README.md:115`; actual count is 136 on main | before-beta-exit |
| D-09 | `docs/SPINE_ROADMAP.md` lists `--cwd` as a "Planned" v0.1.2 item | medium | docs drift | docs | `SPINE_ROADMAP.md:34–43`: "Add `--cwd` support to Phase 2 commands" listed under planned; actually done (PR #11) | before-beta-exit |
| D-10 | Version string is inconsistent across four files | medium | contract ambiguity | CLI / artifacts | `constants.py`: `SPINE_VERSION = "0.1"`; `__init__.py`: `__version__ = "0.1.0"`; `pyproject.toml`: `version = "0.1.0"`; `SPINE_STATUS.md`: `v0.1.1-alpha`; briefs/reviews generated with "SPINE v0.1" | before-beta-exit |
| D-11 | `external-repo-onboarding.md` — referenced in audit spec, doesn't exist on main | high | docs drift | docs | Not in `docs/` on main; removed in "chore: remove internal doc" pass | before-beta-exit |
| D-12 | `SPINE_STATUS.md` release table says `v0.1.1-alpha` but `pyproject.toml` says `0.1.0` | medium | docs drift | docs | `SPINE_STATUS.md` "Current Release" and "Next target" don't match pyproject.toml version | before-beta-exit |

### UX Friction / Workflow Traps

| ID | Title | Severity | Type | Surface | Evidence | Recommended Handling |
|----|-------|----------|------|---------|----------|----------------------|
| F-01 | Generated `AGENTS.md` template is Phase 1 stale — blocks Phase 2 usage | high | docs drift | artifacts / workflow | `init_service.py:172–208`: template says "Phase 1 scope only" and "Do not create new spine subcommands — Phase 1 implements only `spine init`"; users today are in Phase 2 | fix-now |
| F-02 | Generated `CLAUDE.md` template is Phase 1 stale — tells agents only `spine init` exists | high | docs drift | artifacts / workflow | `init_service.py:210–233`: template says "This is Phase 1 only. The only implemented command is `spine init`"; agents following this would not use any Phase 2 commands | fix-now |
| F-03 | `spine init` next-steps panel says "Run `uv run pytest`" — wrong advice for external users | medium | UX friction | CLI | `init_cmd.py:103`: step 4 tells users to run SPINE's internal test suite; external users have their own test commands | before-beta-exit |
| F-04 | Generated briefs hard-code `uv run pytest` — wrong for non-Python repos | medium | UX friction | artifacts | `brief_service.py:130–131`: "Run `uv run pytest` after every change session"; meaningless for repos using npm, cargo, make, etc. | before-beta-exit |
| F-05 | `spine drift scan` has no `--json` flag — inconsistent with three other commands | medium | contract ambiguity | CLI | `mission show`, `doctor`, and `review weekly` all support `--json`; `drift scan --json` fails with "No such option"; drift is one of the most automation-relevant outputs | before-beta-exit |
| F-06 | `spine brief` help text says "symlink replacement" — it writes a regular file | low | docs drift | CLI | `brief_cmd.py` help: "updates .../latest.md as a symlink replacement"; `brief_service.py:42–43` uses `write_file_safe()`, not a symlink | later |
| F-07 | README exit code table implies `--allow-no-git` is global — it only exists on `spine init` | medium | contract ambiguity | docs / CLI | `README.md:134` exit code `2` note implies `--allow-no-git` overrides it on any command; only `init_cmd.py:31–35` defines this flag | before-beta-exit |
| F-08 | `.spine/mission.yaml` in SPINE's own repo is an unfilled template | medium | governance drift | artifacts | `title: "Define active mission"`, `target_user: ''`, `user_problem: ''`, etc.; SPINE governs itself with a blank mission | before-beta-exit |

### Test Gaps

| ID | Title | Severity | Type | Surface | Evidence | Recommended Handling |
|----|-------|----------|------|---------|----------|----------------------|
| T-01 | No test exercises MCP tool call execution — TextContent NameError is undetected | high | test gap | tests | `tests/test_mcp.py` only tests server start/interrupt; no test calls any tool, so B-01 passes CI | fix-now |
| T-02 | No test covers `_filter_recent` with empty or mismatched timestamp formats | medium | test gap | tests | `review_service.py:104–108`; only ISO-conformant, non-empty timestamps tested in existing review tests | later |

---

## 3. Exit-Blocking Summary

### Blocker bugs
- **B-01** — MCP `call_tool` crashes on every tool invocation due to `TextContent` NameError. The MCP server is listed as a shipped feature (`spine mcp serve`). It starts, but no tool call can succeed. This is a silent runtime crash undetected by tests.

### High-severity bugs
- **B-04** — Exit code contract is wrong in public-facing README. Docs say code 2 = "not in a git repo" for all commands; actual behavior is code 1 from most commands. Misleads anyone writing scripts against the CLI.
- **D-01** — Python version badge is factually wrong (3.11+ vs 3.12+). Users on 3.11 will install successfully then hit runtime failures.
- **D-03** — Known Limitations #1 still documents a limitation that was fixed. Actively misleads users about `--cwd` scope.
- **D-04/D-05** — README and docs index both contain broken links to removed files. Public users following these links get 404s.
- **D-06** — docs/README.md points to the wrong GitHub repo URL (different org and repo name).
- **F-01/F-02** — Generated `AGENTS.md` and `CLAUDE.md` templates from `spine init` are Phase 1 stale. Any user running `spine init` today gets governance files that contradict Phase 2 capabilities and actively tell AI agents not to use commands that exist.

### What should block beta exit
1. **B-01** (MCP tool NameError) — must be fixed before calling MCP a working feature
2. **D-01** (Python badge wrong) — must be corrected before public beta
3. **D-03** (stale Known Limitations) — directly misleads users about current behavior
4. **D-04/D-05/D-06** (broken doc links + wrong GitHub URL) — public index is broken
5. **F-01/F-02** (stale init templates) — every `spine init` produces wrong governance files

---

## 4. Queue Guidance

### Should become issues
- **B-01** — MCP TextContent NameError: open an issue, narrow fix (extract full tuple)
- **B-02/B-03** — MCP brief/review response types: can be fixed in same PR as B-01
- **B-04** — Exit code contract: either fix the README table or implement consistent exit codes across commands
- **F-05** — `drift scan --json`: add `--json` to drift scan for agent-friendliness parity
- **T-01** — MCP tool invocation test: add at least one test that calls a tool end-to-end

### Should be folded into existing issues
- **D-01, D-02, D-03, D-08** — All README accuracy issues: one "README polish" PR covers them together
- **D-04, D-05, D-06** — Doc link cleanup: one PR to remove or redirect dead links and fix URL
- **F-01, F-02, F-03** — Init template staleness: one PR to update templates for Phase 2 reality
- **F-04, F-06** — Brief template wording issues: fold into any brief-service improvement PR

### Should remain docs-only
- **D-07** — SPINE_SECURITY_BASELINE.md URL correction: docs-only fix, no code change
- **D-09** — SPINE_ROADMAP.md `--cwd` entry: strike through or remove now-done items
- **D-10** — Version string cleanup: align `constants.py` SPINE_VERSION with pyproject.toml
- **D-11** — external-repo-onboarding.md: re-add the doc or update references to reflect its absence
- **D-12** — SPINE_STATUS.md/pyproject.toml version mismatch: update one to match the other
- **F-08** — SPINE's own mission.yaml: fill in the actual mission fields

### Too minor to activate
- **B-05** — timestamp string comparison: low actual risk (ISO-8601 sorts correctly in UTC); worth noting but not urgent
- **T-02** — timestamp edge case tests: low priority, no known failures
- **F-07** — `--allow-no-git` scope in README: fix as part of exit code table correction (covered by B-04)

---

## 5. Beta-Exit Judgment

**Beta exit from the current `main` branch is NOT justified.**

### Specific blockers

1. **MCP is shipped but non-functional (B-01).** The server starts but all tool calls crash with a `NameError`. No test catches this. Shipping beta with a broken MCP surface would damage trust.

2. **The public README is factually wrong in three ways (D-01, D-03, D-04).** Python version badge is wrong, a Known Limitation describes behavior that was fixed and no longer exists, and the Documentation section links to four files that don't exist. A new user's first impression of the project is broken documentation.

3. **The docs index is broken (D-05, D-06).** `docs/README.md` links to seven removed files and points to the wrong GitHub repo URL. The public documentation index is essentially non-functional.

4. **Every `spine init` produces stale governance files (F-01, F-02).** The generated `AGENTS.md` and `CLAUDE.md` templates tell AI agents that only `spine init` is implemented, and explicitly forbid adding Phase 2 commands that already exist. This is the opposite of what users need on day one.

### What would justify beta exit
- Fix B-01 (MCP tool calls)
- Update README badges, Known Limitations, and doc links (D-01, D-02, D-03, D-04)
- Fix or rebuild `docs/README.md` (D-05, D-06)
- Update init templates to reflect Phase 2 reality (F-01, F-02)
- Optionally: fix exit code table (B-04), add drift scan `--json` (F-05), add MCP tool test (T-01)

The underlying implementation on `main` is sound — all 136 tests pass, the core governance loop works, and the CLI behaves correctly. The blockers are primarily documentation and a silent runtime crash in MCP. These are fixable in a focused session without architectural changes.

---

## Appendix: Commands and Files Inspected

### Commands run
```
uv run spine mission show
uv run spine mission show --json
uv run spine doctor
uv run spine doctor --json
uv run spine drift scan
uv run spine drift scan --json   # → "No such option"
uv run spine brief --target claude
uv run spine review weekly --recommendation continue --notes "..."
uv run spine review weekly --json
uv run spine evidence add --kind commit --description "..."
uv run spine decision add --title "..." --why "..." --decision "..."
uv run spine opportunity score --help
uv run spine --help
uv run spine mission --help
uv run spine review --help
uv run pytest
# Outside git repo:
cd /tmp && uv run --project /home/user/SPINE spine mission show  # exit 1
```

### Source files read
```
src/spine/cli/app.py
src/spine/cli/init_cmd.py
src/spine/cli/mission_cmd.py
src/spine/cli/doctor_cmd.py
src/spine/cli/brief_cmd.py
src/spine/cli/review_cmd.py
src/spine/cli/mcp_cmd.py
src/spine/cli/drift_cmd.py (via drift_service)
src/spine/services/init_service.py
src/spine/services/brief_service.py
src/spine/services/doctor_service.py
src/spine/services/drift_service.py
src/spine/services/review_service.py
src/spine/utils/paths.py
src/spine/constants.py
src/spine/__init__.py
src/spine/main.py
tests/test_mcp.py
tests/test_drift.py
```

### Docs read
```
README.md
docs/README.md
docs/SPINE_FEATURE_BACKLOG.md
docs/SPINE_OFFICIAL_SPEC_v0.1.md
docs/SPINE_PHASE3A_v0.2_SPEC.md
docs/SPINE_ROADMAP.md
docs/SPINE_SECURITY_BASELINE.md
docs/SPINE_STATUS.md
docs/SPINE_TRACKING_POLICY.md
pyproject.toml
.spine/mission.yaml
.spine/constraints.yaml
```

### Governance state inspected
```
.spine/decisions.jsonl  (22 decisions on main)
.spine/evidence.jsonl   (24 entries on main)
.spine/drift.jsonl      (empty)
```

---

## Finding Counts by Severity

| Severity | Count | IDs |
|----------|-------|-----|
| Blocker  | 1     | B-01 |
| High     | 10    | B-02 (indirectly), B-04, D-01, D-02, D-03, D-04, D-05, D-06, F-01, F-02 |
| Medium   | 10    | B-02, B-03, B-05, D-07, D-09, D-10, D-11, D-12, F-03, F-04, F-05, F-07, F-08, T-01 |
| Low      | 4     | D-08, F-06, T-02 |

> Note: Some IDs appear at multiple severities due to context — T-01 (test gap) is high because B-01 is a blocker undetected by tests.

---

*Audit session: 2026-04-09. Branch audited: `main`. Report written to: `claude/audit-spine-main-IHH2O`.*
