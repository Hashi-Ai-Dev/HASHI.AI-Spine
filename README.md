<div align="center">

# SPINE

**Repo-native mission governance for AI-native builders.**

*Define your mission. Bound your scope. Catch drift before it ships.*

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![uv](https://img.shields.io/badge/built%20with-uv-blueviolet)](https://github.com/astral-sh/uv)
[![alpha](https://img.shields.io/badge/status-alpha-orange.svg)]()

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

## Current Alpha Capabilities

| Command | Description |
|---------|-------------|
| `spine init` | Scaffold `.spine/` governance state in a git repo |
| `spine mission show` | Display current mission (table or `--json`) |
| `spine mission set` | Update mission fields |
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

This alpha was validated against two repos before release:

- **Self-governance:** Full governance loop on SPINE's own repo — mission set, evidence logged, decisions recorded, drift scanned, weekly review and agent briefs generated. Test suite: **136+ passing** (CI active on every push and PR).
- **External repo (gsn-connector):** `--cwd` and `SPINE_ROOT` targeting verified end-to-end across all commands. Drift scan correctly read the external repo's git history. No state pollution between repos.

## Known Limitations

This is alpha software. Known rough edges:

1. `SPINE_ROOT` is process-global — if set in a shell profile, all commands are affected. Use `--cwd` per-command to target a specific repo.
2. No migration tooling yet — this is the first public release.
3. JSONL logs are append-only — no undo or rollback.
4. Single git repo per `.spine/` — cannot govern multiple repos from one state directory.
5. `spine mcp serve` is a local stdio server only — no remote MCP support.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 2 | Not in a git repo (`--allow-no-git` to override) |
| 3 | Conflicting existing files (`--force` to overwrite) |

## Documentation

**Start here:**
- [`docs/external-repo-onboarding.md`](docs/external-repo-onboarding.md) — how to use SPINE on an external repo (quickstart, walkthrough, targeting, verification, FAQ)
- [`docs/SPINE_OFFICIAL_SPEC_v0.1.md`](docs/SPINE_OFFICIAL_SPEC_v0.1.md) — authoritative design spec
- [`docs/SPINE_FEATURE_BACKLOG.md`](docs/SPINE_FEATURE_BACKLOG.md) — current and planned features
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — public product roadmap (alpha → beta → v1.0.0)

See [`docs/README.md`](docs/README.md) for the full documentation index.

## What's Next

Phase 3A implementation is nearly complete. The following are done:

- Explicit repo targeting contract + `--cwd` precedence normalization
- Repo/branch context visibility + deterministic default branch resolution
- Stable exit codes + `--json` output modes for CI workflows
- Bootstrap polish + discipline-tax ergonomics
- Artifact ergonomics contract (machine-readable manifest, canonical naming)
- External-repo onboarding docs ([`docs/external-repo-onboarding.md`](docs/external-repo-onboarding.md))

Remaining: alpha-exit validation gate (Issue #25).

Not planned: web UI, auth, billing, cloud sync, remote MCP, or multi-user support.

## Alpha Status

This is an **alpha release**. The core command surface is stable and validated, but breaking changes are possible before v1. Do not use in production without review.

---

<div align="center">
<sub>Built with <a href="https://claude.ai/code">Claude Code</a></sub>
</div>
