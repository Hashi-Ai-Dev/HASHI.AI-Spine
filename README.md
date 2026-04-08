<div align="center">

# SPINE

**Keep your AI coding agents on target — mission governance for AI-native builders.**

*Define your mission. Bound your scope. Catch drift before it ships.*

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![uv](https://img.shields.io/badge/built%20with-uv-blueviolet)](https://github.com/astral-sh/uv)
[![beta](https://img.shields.io/badge/status-beta-blue.svg)]()
[![Stars](https://img.shields.io/github/stars/Hashi-Ai-Dev/SPINE?style=flat&logo=github)]()
[![Forks](https://img.shields.io/github/forks/Hashi-Ai-Dev/SPINE?style=flat&logo=github)]()

</div>

---

SPINE is a CLI tool that sits **above** your coding agents, not inside them. It uses a `.spine/` directory — plain YAML and JSONL, version-controlled alongside your code — as the canonical source of truth for what you're building, what's in scope, and what's been decided.

No daemons. No cloud. No model calls.

## Who is this for?

Solo developers and small teams building with AI coding agents (Claude Code, Codex, Cursor, etc.) who want a lightweight governance layer to:

- Maintain a clear, bounded mission while agents work
- Prevent scope creep from accumulating invisibly
- Keep an auditable log of decisions and evidence
- Generate mission briefs that ground agent sessions

SPINE is strongest today with **Claude Code** and **Codex** — it generates briefing files those tools can load automatically.

## Why SPINE?

SPINE solves three problems AI coding agents create:

- **Drift** — agents accumulate scope without you noticing until the codebase is a mess
- **Black boxes** — you forget what you decided and why by the next session
- **No ground truth** — agents work from memory, not from agreed-upon direction

SPINE is the explicit layer that keeps you and your agents aligned.



## Installation

Requires Python 3.12+ and [uv](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/Hashi-Ai-Dev/SPINE
cd SPINE
uv sync
```

That's it. All `spine` commands are now available via `uv run spine`.

## Quickstart — Use SPINE on any repo

SPINE governs a **target repo** that you point it at. You don't need to `cd` into the target repo.

```bash
# (From the SPINE directory)

# 1. Initialize .spine/ governance state in your project
uv run spine init --cwd /path/to/your-project

# 2. Define your mission
uv run spine mission set --cwd /path/to/your-project \
  --title "My Project" \
  --status active \
  --scope "backend,api" \
  --forbid "ui,billing"

# 3. Generate a mission brief for Claude
uv run spine brief --cwd /path/to/your-project --target claude

# 4. Run the governance health check
uv run spine doctor --cwd /path/to/your-project
```

`.spine/` is version-controlled inside your target repo alongside your code.

## Current Capabilities

| Command | Description |
|---------|-------------|
| `spine init` | Scaffold `.spine/` governance state in a git repo |
| `spine mission show` | Display current mission (table or `--json`) |
| `spine mission set` | Update mission fields |
| `spine mission refine` | Create a mission draft (does not mutate canonical mission.yaml) |
| `spine mission confirm <draft_id>` | Promote a mission draft to canonical |
| `spine mission drafts` | List pending mission drafts |
| `spine opportunity score` | Score an opportunity with a weighted 6-factor rubric |
| `spine evidence add` | Append a typed evidence record |
| `spine decision add` | Append a decision record with rationale |
| `spine drift scan` | Detect scope drift using git-native diff (staged + committed) |
| `spine brief --target claude\|codex` | Generate a mission brief for a specific agent |
| `spine review weekly` | Aggregate evidence/decisions/drift into a weekly review |
| `spine doctor` | Validate `.spine/` state and repo contract |
| `spine mcp serve` | Start a local MCP server (stdio mode) |

`--json` output is available on `mission show`, `doctor`, and `review weekly`.

## What `spine init` Creates

```
.spine/
├── mission.yaml        ← Active mission definition
├── constraints.yaml    ← Work schedule, budget, routing rules
├── opportunities.jsonl ← Scored opportunity log
├── not_now.jsonl       ← Deferred ideas
├── evidence.jsonl      ← Evidence log
├── decisions.jsonl     ← Decision record
├── drift.jsonl         ← Drift scan results
├── runs.jsonl          ← Agent run log
├── reviews/            ← Generated weekly reviews
├── briefs/             ← Agent mission briefs
├── skills/             ← Agent skill definitions
└── checks/             ← Automated checks
AGENTS.md               ← Guidance for AI agents in this repo
CLAUDE.md               ← Claude-specific governance rules
```

## Using SPINE on any repo

Every SPINE command accepts `--cwd` to target a repo other than the current directory. This is the recommended pattern when running SPINE from its own directory to govern another project.

```bash
# All commands support --cwd
uv run spine doctor         --cwd /path/to/other-repo
uv run spine mission show   --cwd /path/to/other-repo
uv run spine drift scan     --cwd /path/to/other-repo
uv run spine evidence add   --cwd /path/to/other-repo --kind commit --description "..."
uv run spine decision add   --cwd /path/to/other-repo --title "..." --why "..." --decision "..."
```

**Alternative: `SPINE_ROOT` env var**

If you prefer not to pass `--cwd` on every command, set `SPINE_ROOT` for your shell session:

```bash
export SPINE_ROOT=/path/to/other-repo
uv run spine doctor
uv run spine mission show
```

`SPINE_ROOT` is process-global — unset it when switching repos.

**Targeting contract**

SPINE resolves the target repository in this order (highest priority first):

1. `--cwd <path>` — if explicitly provided (overrides `SPINE_ROOT`)
2. `SPINE_ROOT` — if set in the environment
3. Current working directory — fallback default

Commands that require a git repo fail fast with a clear message when the resolved path is not a git repository.

## Validation

Validated against two repos before the v0.2.0-beta release:

- **Self-governance:** Full governance loop on SPINE's own repo — mission set, evidence logged, decisions recorded, drift scanned, weekly review and agent briefs generated. Test suite: **300+ passing** (15 test files, CI active on every push and PR).
- **External repo (gsn-connector):** `--cwd` and `SPINE_ROOT` targeting verified end-to-end across all commands. Drift scan correctly read the external repo's git history. No state pollution between repos.

## Known Limitations

This is beta software. Known rough edges:

1. `SPINE_ROOT` is process-global — if set in a shell profile, all commands are affected. Use `--cwd` per-command to target a specific repo.
2. No migration tooling yet — this is the first public release.
3. JSONL logs are append-only — no undo or rollback.
4. Single git repo per `.spine/` — cannot govern multiple repos from one state directory.
5. `spine mcp serve` is a local stdio server only — no remote MCP support.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Validation failure (invalid arguments, constraint violations) |
| 2 | Context failure (missing git repo, missing .spine/, invalid paths) |

## Documentation

**Start here:**
- [`docs/external-repo-onboarding.md`](docs/external-repo-onboarding.md) — how to use SPINE on an external repo (quickstart, walkthrough, targeting, verification, FAQ)
- [`docs/SPINE_INTEGRATIONS.md`](docs/SPINE_INTEGRATIONS.md) — compatibility and integration guide for Claude Code, oh-my-claudecode, and Superpowers
- [`docs/SPINE_OFFICIAL_SPEC_v0.1.md`](docs/SPINE_OFFICIAL_SPEC_v0.1.md) — authoritative design spec
- [`docs/SPINE_FEATURE_BACKLOG.md`](docs/SPINE_FEATURE_BACKLOG.md) — current and planned features
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — public product roadmap (alpha → beta → v1.0.0)

See [`docs/README.md`](docs/README.md) for the full documentation index.

## What's Next

SPINE is now in **beta** (`v0.2.0-beta`). Phase 3A is complete:

- Explicit repo targeting contract + `--cwd` precedence normalization
- Repo/branch context visibility + deterministic default branch resolution
- Stable exit codes + `--json` output modes for CI workflows
- Bootstrap polish + discipline-tax ergonomics
- Artifact ergonomics contract (machine-readable manifest, canonical naming)
- External-repo onboarding docs ([`docs/external-repo-onboarding.md`](docs/external-repo-onboarding.md))

Beta work focuses on reducing discipline tax and making governance mechanics more executable for agents and tools. See [`docs/ROADMAP.md`](docs/ROADMAP.md) for the beta direction.

Not planned: web UI, auth, billing, cloud sync, remote MCP, or multi-user support.

## Beta Status

This is a **beta release** (`v0.2.0-beta`). The core command surface is stable and validated. Breaking changes are possible before v1. Do not use in production without review.

---

## Authors

- **HASHI.AI** — SPINE Agent / Repo Manager
- **Hashi** — Project Lead

*SPINE is built and maintained by the HASHI.AI agent system.*
