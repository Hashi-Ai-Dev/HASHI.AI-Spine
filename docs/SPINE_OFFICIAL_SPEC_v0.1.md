# SPINE Official Specification v0.1

## What SPINE Is

SPINE (Strategic Proof & Intelligent Navigation Engine) is a repo-native mission governor for AI-native solo builders. It is the governance layer above coding agents—not another coding agent itself. SPINE exists to turn repo chaos, project sprawl, and agent drift into: one active mission, one bounded execution lane, one proof ledger, one review loop, and one anti-drift governance layer.

## v0.1 Scope

Phase 1 established the repo bootstrap contract: `spine init` scaffolds the `.spine/` directory with canonical state files and agent guidance.

Phase 2 (current) implements the core command surface:

| Command | Purpose |
|---------|---------|
| `spine mission show` | Read and validate mission.yaml, display title/status/target/success metric/allowed scope/forbidden expansions |
| `spine mission set` | Update mission.yaml with validation, refresh updated_at, reject invalid transitions |
| `spine opportunity score` | Deterministic weighted scoring of opportunities, append JSONL to opportunities.jsonl |
| `spine brief --target claude` | Generate markdown brief under .spine/briefs/claude/ |
| `spine brief --target codex` | Generate markdown brief under .spine/briefs/codex/ |
| `spine evidence add` | Append validated evidence record to evidence.jsonl |
| `spine decision add` | Append validated decision record to decisions.jsonl |
| `spine drift scan` | Git-native deterministic drift scanning, append to drift.jsonl, print severity summary |
| `spine review weekly` | Aggregate last 7 days of evidence/decisions/drift/mission, write markdown to .spine/reviews/YYYY-MM-DD.md |
| `spine doctor` | Validate required files exist, YAML/JSONL parse cleanly, projection rebuild works |
| `spine mcp serve` | Blocking stdio MCP server exposing resources and tools |

## Non-Goals (v0.1)

- No web UI or dashboard
- No authentication or billing
- No cloud sync or remote daemon
- No background workers or autonomous long-running orchestration
- No required external APIs or live model dependency
- No multi-user collaboration

## Core Design Rules

1. **Repo first, UI second.** All state lives in the repo under `.spine/`.
2. **One active mission by default.** SPINE enforces bounded execution lanes.
3. **Canonical state lives in files under `.spine/`** — never in memory or external stores.
4. **JSONL + YAML are the only source of truth in v0.1.**
5. **SQLite is a rebuildable projection only.** Never a dual-write source.
6. **Deterministic heuristics first; model integration later.**
7. **Git-native evidence and git-native drift logic where possible.**
8. **No speculative architecture unless tiny and inert.**
9. **Agents consume SPINE; SPINE does not depend on agent memory.**
10. **Public CLI contract matters more than internal implementation excuses.**

## Canonical State Rules

Canonical in v0.1:
- `.spine/mission.yaml` — active mission definition
- `.spine/constraints.yaml` — operational constraints
- `.spine/*.jsonl` — append-only event logs

`.spine/state.db` is optional and projection-only. Allowed:
- Rebuild projection at command start
- Rebuild projection at `spine doctor`
- Rebuild projection at `spine mcp serve` startup
- Skip projection entirely if not needed yet

Forbidden:
- Dual-write canonical files and SQLite
- Reconciliation engine
- Background sync service
- Incremental sync complexity

## Repo Contract

The repo must contain:
- `AGENTS.md` — agent guidance at repo root
- `CLAUDE.md` — Claude Code rules at repo root
- `.claude/settings.json` — Claude Code settings
- `.codex/config.toml` — Codex configuration
- `.spine/mission.yaml` — mission definition
- `.spine/constraints.yaml` — constraints definition
- `.spine/opportunities.jsonl` — opportunity log
- `.spine/not_now.jsonl` — deferred ideas log
- `.spine/evidence.jsonl` — evidence log
- `.spine/decisions.jsonl` — decisions log
- `.spine/drift.jsonl` — drift detection log
- `.spine/runs.jsonl` — run metadata log
- `.spine/reviews/` — generated weekly reviews
- `.spine/briefs/claude/` — Claude-targeted briefs
- `.spine/briefs/codex/` — Codex-targeted briefs
- `.spine/skills/` — agent skill definitions
- `.spine/checks/` — automated check scripts

## Command Contracts

### `spine mission show`
Read and validate `mission.yaml`. Show title, status, target user, success metric, allowed scope, forbidden expansions.

### `spine mission set`
Validate input, update `mission.yaml`, refresh `updated_at`, reject invalid transitions.

### `spine opportunity score`
Deterministic weighted scoring only. Append JSON line to `opportunities.jsonl`. No model call required.

Inputs: pain, founder_fit, time_to_proof, monetization, sprawl_risk, maintenance_burden.

### `spine brief --target claude`
Generate markdown under `.spine/briefs/claude/` including: mission summary, allowed scope, forbidden expansions, acceptance criteria, testing expectations, evidence requirements, instruction to plan first for non-trivial work.

### `spine brief --target codex`
Same core sections plus: worktree recommendation, repo-discipline wording.

### `spine evidence add`
Allowed kinds: brief_generated, commit, pr, test_pass, review_done, demo, user_feedback, payment, kill, narrow. Append validated JSON line to `evidence.jsonl`.

### `spine decision add`
Append validated JSON line to `decisions.jsonl`. Require: title, why, decision. Optional: alternatives.

### `spine drift scan`
Git-native and deterministic first. Uses two detection modes:
- **Mode A (working tree):** `git diff --name-only HEAD` — detects forbidden uncommitted/staged changes
- **Mode B (branch drift):** `git diff --name-only <default_branch>...HEAD` — detects forbidden committed changes on the current branch relative to the default branch

Default branch detection tries: `git symbolic-ref refs/remotes/origin/HEAD`, then `main` if it exists locally, then `master` if it exists locally. Falls back to working-tree-only if no default branch can be resolved.

Inspect changed paths and diff hunks only. Flag: new UI/dashboard when forbidden, auth or billing code when forbidden, excessive dependency expansion, service additions without tests. Append structured events to `drift.jsonl`. Print severity summary.

`--against <branch>` can be passed to explicitly compare against a named branch instead of auto-detecting the default.

### `spine review weekly`
Aggregate last 7 days of: evidence, decisions, drift, mission state. Write markdown to `.spine/reviews/YYYY-MM-DD.md`.

Allowed recommendations: continue, narrow, pivot, kill, ship_as_is.

### `spine doctor`
Validate: required files exist, YAML parses and conforms, JSONL lines parse cleanly, projection rebuild works, AGENTS.md/CLAUDE.md/.claude/settings.json/.codex/config.toml exist.

### `spine mcp serve`
Separate blocking command. stdio only in v0.1. No daemon. No background threads. No hidden launch from other commands.

Expose resources: active mission, current constraints, recent evidence, recent decisions, open drift, latest review.

Expose tools: mission_get, mission_update, brief_generate, evidence_add, decision_add, drift_scan, review_generate, opportunity_score.

## Deterministic Scoring Rules

Opportunity scoring uses weighted factors with no model calls:
- pain (1-5)
- founder_fit (1-5)
- time_to_proof (1-5, inverse: lower is faster)
- monetization (1-5)
- sprawl_risk (1-5, inverse: lower is riskier)
- maintenance_burden (1-5, inverse: lower is heavier burden)

Weights are defined in mission.yaml or constraints.yaml. Default weights favor speed-to-proof and founder fit.

## Drift Detection Rules

Drift is detected by scanning git diff output across two modes:
- **Working tree:** `git diff HEAD` — catches uncommitted/staged forbidden changes
- **Branch drift:** `git diff <default_branch>...HEAD` — catches forbidden changes committed on the current branch

Patterns that trigger drift flags:
- New directories or files matching forbidden scope (e.g., `/ui/`, `/dashboard/`, `/auth/`, `/billing/`) — HIGH severity
- Dependencies added to pyproject.toml or package.json that imply forbidden capabilities — LOW severity
- Service files (e.g., server.py, api.py) added without corresponding test files — LOW severity

Severity levels:
- HIGH: matches forbidden_expansions directly
- MEDIUM: likely sprawl (new top-level module without clear mission alignment)
- LOW: worth noting but not clearly drift

Untracked files are NOT flagged as drift — they must be staged/committed to be detected.

Severity levels:
- HIGH: matches forbidden_expansions directly
- MEDIUM: likely sprawl (new top-level module without clear mission alignment)
- LOW: worth noting but not clearly drift

## MCP Process Model

`spine mcp serve` is a stdio-only MCP server. It:
- Runs as a separate blocking process
- Does not daemonize
- Exposes typed resources and tools via MCP protocol
- Reads canonical state from `.spine/` files on each request
- Never writes to canonical state directly (all writes go through CLI commands)

## Development Phases

| Phase | Status | Scope |
|-------|--------|-------|
| Phase 1 | Complete | `spine init` bootstrap only |
| Phase 2 | Current | Core CLI commands, MCP server |
| Phase 3 | Future | SQLite projection, model-assisted scoring |
| Phase 4 | Future | Multi-mission support, web UI |

## Acceptance Criteria

- All Phase 2 commands pass their contract tests
- `uv run pytest` passes with zero failures
- `spine doctor` passes on a clean init
- `spine drift scan` correctly identifies known drift patterns
- `spine brief --target claude` and `--target codex` produce valid markdown
- MCP server starts and responds to resource/tool requests over stdio
- No new dependencies beyond pyproject.toml without explicit approval
