# SPINE Public Alpha Release Notes — Draft

**Version:** v0.1.1-alpha
**Status:** ALPHA — not production-ready
**Date:** 2026-04-06

---

## What is SPINE?

SPINE (Structured Project Intelligence for Narrative Execution) is a **local-first, repo-native mission governor** for AI coding agents. It runs as a CLI tool inside any git repository and uses `.spine/` as the canonical source of truth for governance state.

SPINE is designed to help a single developer (or small team) maintain clarity about:
- What the current mission is and isn't
- What scope is allowed vs forbidden
- What evidence has been collected
- What decisions have been made and why
- Whether the project is drifting from its stated scope

---

## What's Implemented in Alpha v0.1.1

### Core Commands

| Command | Description |
|---------|-------------|
| `spine init` | Scaffold `.spine/` governance state |
| `spine mission show` | Display current mission (table or `--json`) |
| `spine mission set` | Update mission fields |
| `spine opportunity score` | Score an opportunity (1-5 rubric) |
| `spine evidence add` | Log evidence (brief_generated, commit, pr, test_pass, etc.) |
| `spine decision add` | Log a decision record |
| `spine drift scan` | Scan for scope drift (git-native) |
| `spine brief --target claude\|codex` | Generate mission brief for specific agent |
| `spine review weekly` | Generate weekly review document (`--json` supported) |
| `spine doctor` | Validate `.spine/` state and repo contract (`--json` supported) |
| `spine mcp serve` | Start MCP server (blocking stdio mode) |

### Key Design Properties

- **Local-first:** No cloud, no auth, no daemon required
- **Git-native:** Drift detection uses only `git diff` — no semantic scanning
- **YAML + JSONL:** Human-readable canonical state (`.spine/mission.yaml`) + append-only logs
- **Deterministic:** Opportunity scoring and drift detection are formulaic — no model calls
- **Single-file state:** Phase 1 uses `.spine/state.db` as an empty placeholder (no SQLite in alpha)

### Phase 2 Features (since v0.1)

- Mission show/set with Rich table output and `--json` machine-readable output
- Opportunity scoring with weighted 6-factor rubric
- Evidence and decision JSONL logging
- Drift scan with Mode A (working tree) + Mode B (branch vs default)
- Brief generation for Claude and Codex with `latest.md` alias
- Weekly review with aggregation of evidence/decisions/drift
- Doctor validation of `.spine/` state
- MCP server exposing resources and tools via stdio

---

## What Was Validated

### Self-dogfood (on SPINE's own repo)
- Full governance loop: mission set, opportunity scored, briefs generated, evidence/decisions logged, drift scanned, weekly review produced
- 120 tests pass (1 skipped due to Windows SIGINT platform issue — not a real failure)

### External repo validation (gsn-connector)
- `spine init --cwd <path>` creates `.spine/` at target repo root
- `SPINE_ROOT` env var correctly binds both canonical state AND git operations to external repo
- Drift scan correctly diffs external repo's git, not the operator's CWD repo
- Mission show/set, opportunity score, evidence add, decision add, brief generate, doctor, review weekly all work on external repo
- No SPINE repo files pollute external target's `.spine/` state

---

## What's Intentionally Out of Scope for Alpha

- **Dashboard UI** — CLI only, no web interface
- **Auth / billing** — local-first means no user accounts
- **Cloud sync** — state lives in `.spine/` in the repo itself
- **Remote MCP** — `spine mcp serve` is a local stdio server only
- **Background workers / daemon** — blocking commands only
- **Multi-user collaboration** — single-operator design
- **Live model dependency** — all scoring/detection is deterministic
- **Broad architecture refactors** — Phase 3 not started

---

## Known Rough Edges

1. **No `--cwd` on Phase 2 commands** — Only `spine init` accepts `--cwd`. All other commands use `SPINE_ROOT` env var for external targeting.

2. **`SPINE_ROOT` is process-global** — if inherited from shell profile, all spine commands change behavior unexpectedly.

3. **`spine brief` subcommand naming** — `spine brief --target claude` not `spine brief generate`. Minor spec inconsistency.

4. **`spine init --cwd <path>` conflict check** — compares against git-root's existing files. Workaround: unset `SPINE_ROOT` before running `spine init --cwd`.

5. **Doctor `get_open_drift()`** uses `self.repo_root / C.SPINE_DIR` instead of `self._spine_root` — minor inconsistency.

6. **Windows `.git` as file** — On some Windows setups, `.git` is a file (not directory), which can cause `git rev-parse --show-toplevel` to walk up to the parent repo. The `SPINE_ROOT` approach bypasses this.

---

## Alpha Limitations

- **No upgrade path** — v0.1.1 is the first public alpha. No migration tooling yet.
- **Single git repo per `.spine/`** — Cannot govern multiple git repos from one `.spine/` state.
- **No undo/rollback** — JSONL logs are append-only. No revert command.
- **Timezone-aware only** — All timestamps in UTC. No localization.

---

## Getting Started

```bash
# Install (requires uv)
cd /your/project
git init
uv run spine init

# Set your mission
uv run spine mission set --title "My Project" --status active \
  --scope "backend,api" --forbid "ui,billing"

# Generate a brief for Claude
uv run spine brief --target claude

# Run the MCP server (separate terminal)
uv run spine mcp serve
```

---

## Links

- Repository: https://github.com/LucielAI/HASHI.AI-Spine
- Phase 3A Planning Spec: `docs/SPINE_PHASE3A_v0.2_SPEC.md`
- Official Spec: `docs/SPINE_OFFICIAL_SPEC_v0.1.md`
- Product Thesis: `docs/SPINE_ORIGIN_AND_PRODUCT_THESIS_v0.1.md`

---

*This is an ALPHA release. Expect rough edges. Do not use in production without review.*