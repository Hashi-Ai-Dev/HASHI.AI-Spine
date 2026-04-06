# SPINE

**Local-first, repo-native mission governor for AI-native builders.**

SPINE governs repositories through a `.spine/` contract directory that captures your active mission, constraints, evidence, decisions, and run history as plain YAML and JSONL files — version-controlled alongside your code.

## What SPINE does

SPINE is the governance layer *above* your coding agents. It enforces:
- One active mission with explicit allowed scope and forbidden expansions
- Bounded execution lanes so agents can't silently drift
- Append-only evidence and decision logs for weekly review
- Git-native drift detection against your mission constraints
- Machine-readable briefs for Claude, Codex, and compatible agents
- An MCP server so agents can read and write governance state over stdio

## Setup

```bash
# Install dependencies
uv sync

# Bootstrap .spine/ in this repo
uv run spine init

# Validate the installation
uv run spine doctor

# Run tests
uv run pytest
```

## What `spine init` creates

```
.spine/
├── mission.yaml        ← Active mission definition
├── constraints.yaml    ← Work schedule, budget, routing rules
├── opportunities.jsonl ← Candidate opportunities log
├── not_now.jsonl       ← Deferred ideas
├── evidence.jsonl      ← Evidence for weekly review
├── decisions.jsonl     ← Decision record
├── drift.jsonl         ← Drift detection log
├── runs.jsonl          ← Agent run log
├── state.db            ← Future projection target (placeholder)
├── reviews/            ← Generated review documents
├── briefs/             ← Mission briefs (claude/, codex/)
├── skills/             ← Agent skill definitions
└── checks/             ← Automated check scripts
AGENTS.md               ← Guidance for all AI agents
CLAUDE.md               ← Claude-specific rules
.claude/settings.json   ← Claude Code permissions
.codex/config.toml      ← Codex sandbox config
```

## CLI

```
spine --help
```

### Mission

```bash
spine mission show                          # Display current mission
spine mission show --json                   # Machine-readable output
spine mission set --title "My mission"      # Update mission fields
spine mission set --status active
spine mission set --scope "cli,tests" --forbid "ui,auth,billing"
```

### Opportunities

```bash
spine opportunity score \
  --pain 4 --founder-fit 5 --time-to-proof 2 \
  --monetization 3 --sprawl-risk 4 --maintenance-burden 3
```

### Briefs

```bash
spine brief --target claude     # Generate Claude-targeted brief
spine brief --target codex      # Generate Codex-targeted brief
```

### Evidence & Decisions

```bash
spine evidence add --kind commit --summary "Added drift scan"
spine decision add --title "Use JSONL" --why "Append-only" --decision "Use JSONL for all event logs"
```

### Drift

```bash
spine drift scan                    # Scan uncommitted/staged changes
spine drift scan --against main     # Compare current branch to main
```

### Review

```bash
spine review weekly                         # Generate weekly review
spine review weekly --recommendation narrow # With explicit recommendation
spine review weekly --days 14               # Extend window to 14 days
```

### Doctor

```bash
spine doctor    # Validate .spine/ state and repo contract
```

### MCP server

```bash
spine mcp serve     # Blocking stdio MCP server (run as subprocess)
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Runtime or validation error |
| 2 | Not in a git repo (use `--allow-no-git` to override for `init`) |
| 3 | Conflicting existing files (use `--force` to overwrite for `init`) |

## State files

All state is plain text, version-controlled, and human-readable.

| File | Format | Purpose |
|------|--------|---------|
| `.spine/mission.yaml` | YAML | Active mission definition |
| `.spine/constraints.yaml` | YAML | Work schedule, budget, routing |
| `.spine/opportunities.jsonl` | JSONL | Scored opportunity log |
| `.spine/evidence.jsonl` | JSONL | Evidence collected for review |
| `.spine/decisions.jsonl` | JSONL | Decision record |
| `.spine/drift.jsonl` | JSONL | Drift detection events |
| `.spine/runs.jsonl` | JSONL | Agent run log |
| `.spine/reviews/YYYY-MM-DD.md` | Markdown | Weekly review docs |
| `.spine/reviews/latest.md` | Markdown | Stable alias to latest review |
| `.spine/briefs/claude/` | Markdown | Claude-targeted briefs |
| `.spine/briefs/codex/` | Markdown | Codex-targeted briefs |

## Design principles

- **Repo first.** All state lives in `.spine/` under version control.
- **One active mission.** SPINE enforces a single bounded execution lane.
- **YAML + JSONL are canonical.** SQLite (if present) is a rebuildable projection only.
- **Deterministic heuristics.** No required live-model dependency.
- **Agents consume SPINE; SPINE does not depend on agent memory.**
