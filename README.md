# SPINE

**Local-first, repo-native mission governor for AI-native builders.**

SPINE governs repositories through a `.spine/` contract directory that captures your active mission, constraints, evidence, decisions, and run history as plain YAML and JSONL files — version-controlled alongside your code.

## Phase 1 + Phase 2 (Alpha)

Alpha implements the full Phase 1 + Phase 2 command surface. No daemons, no network, no model inference.

## Quickstart

```bash
# Install dependencies
uv sync

# Bootstrap .spine/ in this repo
uv run spine init

# Set your mission
uv run spine mission set --title "My Project" --status active --scope "backend,api" --forbid "ui,billing"

# Generate a brief for Claude
uv run spine brief --target claude

# Run tests
uv run pytest
```

## Full Command Reference

```
spine --help
spine init [--force] [--allow-no-git] [--cwd <path>]
spine mission show [--json]
spine mission set [--title] [--status] [--scope] [--forbid] ...
spine opportunity score <title> [--description] [--pain] [--founder-fit] ...
spine evidence add --kind <kind> [--description]
spine decision add --title <title> --why <why> --decision <decision>
spine drift scan [--against <branch>]
spine brief --target claude|codex
spine review weekly [--days N] [--recommendation continue|narrow|pivot|kill|ship_as_is] [--notes]
spine doctor [--json]
spine mcp serve
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
├── briefs/             ← Mission briefs
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
spine init [--force] [--allow-no-git]
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 2 | Not in a git repo (use `--allow-no-git` to override) |
| 3 | Conflicting existing files (use `--force` to overwrite) |

## Alpha Posture

This is an **alpha** release. The core command surface is validated and stable, but rough edges remain:

- `SPINE_ROOT` env var enables governing an external repo (for commands without `--cwd`)
- `--json` output available on `mission show`, `doctor`, `review weekly`
- Briefs and reviews update `latest.md` aliases on every generation
- Drift scan uses git-native detection (Mode A: working tree + Mode B: branch vs default)
