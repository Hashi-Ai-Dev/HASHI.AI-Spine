# SPINE Integrations and Compatibility Guide

**Status:** Public — Stable  
**Last updated:** 2026-04-14

---

## Contents

1. [What SPINE is and what it is not](#1-what-spine-is-and-what-it-is-not)
2. [Compatibility rule](#2-compatibility-rule)
3. [Integration surfaces](#3-integration-surfaces)
4. [Workflow examples](#4-workflow-examples)
   - [Claude Code](#41-claude-code)
   - [oh-my-claudecode](#42-oh-my-claudecode)
   - [Superpowers](#43-superpowers)
   - [OpenClaw](#44-openclaw)
5. [Anti-drift guidance](#5-anti-drift-guidance)

---

## 1. What SPINE is and what it is not

SPINE is a **repo-native governance layer**. It defines what you are building, bounds the scope, records decisions and evidence, and generates briefing artifacts that agents can load. All state is plain YAML and JSONL files committed alongside your code in `.spine/`.

**Claude Code**, **oh-my-claudecode**, **Superpowers**, and **OpenClaw** are **execution and workflow surfaces**. They manage how AI sessions run, how prompts are structured, how tool calls execute, and how agent sessions are configured and extended.

These roles do not overlap. The correct layering is:

```
┌──────────────────────────────────┐
│         SPINE (.spine/)          │  ← governance layer (mission, scope, decisions, drift)
└──────────────────────────────────┘
         ↓ briefing artifacts
┌─────────────────────────────────────────────┐
│  Claude Code / OMC / Superpowers / OpenClaw │  ← execution layer (sessions, tools, prompts)
└─────────────────────────────────────────────┘
         ↓ code changes, commits
┌──────────────────────────────────┐
│            Your repo             │
└──────────────────────────────────┘
```

SPINE contributes: bounded mission, artifact outputs (briefs, reviews, handoffs), decision/evidence log, drift detection.

The execution tools contribute: running agent sessions, managing tool calls, structuring prompts, configuring Claude behavior.

Neither replaces the other.

---

## 2. Compatibility rule

**SPINE must not require you to abandon your current stack.**

SPINE integrates through stable, local contracts:

- **CLI commands** — all commands are stable, predictable, and exit-code-safe
- **`--json` output** — `mission show`, `doctor`, and `review weekly` support machine-readable output
- **`.spine/` directory** — all governance state is plain YAML and JSONL; any tool can read it
- **Artifact files** — briefs are written to `.spine/briefs/<target>/`, reviews to `.spine/reviews/`
- **No runtime dependency** — SPINE has no daemon, no cloud connection, no model calls at runtime

SPINE avoids:
- Duplicating execution or orchestration features these tools already handle
- Requiring changes to how your agent sessions are run
- Locking you into any specific agent runtime or model provider

If your workflow uses Claude Code, oh-my-claudecode, Superpowers, or a combination — SPINE adds a governance layer on top without changing how those tools work.

---

## 3. Integration surfaces

These are the stable surfaces SPINE exposes for tools to read and build on.

### CLI commands

All commands support `--cwd <path>` to target any repo. Exit codes are stable:

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Validation failure |
| 2 | Context failure (missing repo, missing `.spine/`) |

### JSON output

```bash
uv run spine mission show --json
uv run spine doctor --json
uv run spine review weekly --json
```

Machine-readable output for CI scripts, hooks, and automated workflows.

### `.spine/` canonical state

```
.spine/
├── mission.yaml       ← active mission (title, scope, forbidden expansions)
├── constraints.yaml   ← operational constraints
├── evidence.jsonl     ← append-only evidence log
├── decisions.jsonl    ← append-only decision record
├── drift.jsonl        ← drift scan results
├── briefs/            ← generated agent briefing files
│   ├── claude/        ← Claude Code briefing
│   ├── codex/         ← Codex briefing
│   └── openclaw/      ← OpenClaw briefing
└── reviews/           ← generated weekly review files
```

Any tool that can read files can consume SPINE's state directly. SPINE never locks state behind a service or API.

### Artifact files

```
.spine/briefs/claude/latest.md        ← load in Claude Code with @.spine/briefs/claude/latest.md
.spine/briefs/codex/latest.md         ← Codex brief
.spine/briefs/openclaw/latest.md      ← load in OpenClaw at session start
.spine/briefs/<target>/YYYY-MM-DD.md  ← point-in-time brief (any target)
.spine/reviews/YYYY-MM-DD.md          ← weekly governance review
```

Briefs are plain markdown. Load them directly into your agent session.

### Repo root files

`spine init` writes these to the governed repo root:

- `AGENTS.md` — agent guidance for any agent reading the repo
- `CLAUDE.md` — Claude Code-specific governance rules
- `.claude/settings.json` — Claude Code settings
- `.codex/config.toml` — Codex configuration
- `.openclaw/spine.yaml` — OpenClaw startup and integration settings

These files are how SPINE communicates governance rules to agents without requiring them to call SPINE directly.

---

## 4. Workflow examples

### 4.1 Claude Code

**What Claude Code contributes:** interactive coding sessions, tool calls (file edits, bash, search), conversation context management.

**What SPINE contributes:** bounded mission definition, drift detection, decision and evidence logging, mission briefs that ground the session.

#### Setup

```bash
# In the SPINE directory, initialize governance on your project
uv run spine init --cwd /path/to/your-project

# Set a bounded mission
uv run spine mission set --cwd /path/to/your-project \
  --title "Auth service v1" \
  --status active \
  --scope "auth,jwt,middleware" \
  --forbid "ui,billing,background-workers"

# Generate a brief for Claude Code
uv run spine brief --target claude --cwd /path/to/your-project
```

#### Starting a session

Inside your project, load the brief when starting a Claude Code session:

```
@.spine/briefs/claude/latest.md
```

Or reference CLAUDE.md, which `spine init` writes with governance rules Claude Code will read automatically.

#### During a session

After committing work, log evidence:

```bash
uv run spine evidence add --cwd /path/to/your-project \
  --kind commit \
  --description "Implemented JWT verification middleware"
```

Before opening a PR, run a preflight check:

```bash
uv run spine check before-pr --cwd /path/to/your-project
```

This runs `spine doctor` and `spine drift scan` together. If drift is flagged:

```
Severity  Path          Reason
HIGH      ui/dashboard  Matches forbidden scope: ui
```

Resolve the drift before proceeding.

#### End of session

```bash
uv run spine review weekly --cwd /path/to/your-project \
  --recommendation continue \
  --notes "JWT middleware complete, token refresh next"
```

The review is written to `.spine/reviews/YYYY-MM-DD.md` — a clean record of what happened this session.

---

### 4.2 oh-my-claudecode

**What oh-my-claudecode contributes:** Claude Code configuration management, prompt templates, plugin definitions, session customization.

**What SPINE contributes:** governance layer that sits above session configuration — mission scope, drift detection, evidence and decision logging.

oh-my-claudecode controls *how* your Claude Code sessions are configured. SPINE governs *what* those sessions are allowed to work on.

#### Using SPINE alongside oh-my-claudecode

SPINE does not require changes to your oh-my-claudecode configuration. Add SPINE initialization to any project you are already governing with oh-my-claudecode:

```bash
uv run spine init --cwd /path/to/your-project
uv run spine mission set --cwd /path/to/your-project \
  --title "Your project" \
  --status active \
  --scope "..." \
  --forbid "..."
```

The `CLAUDE.md` file that `spine init` creates works naturally alongside any Claude Code configuration oh-my-claudecode manages. Claude Code reads `CLAUDE.md` for project rules automatically.

#### Before a session

Generate a brief:

```bash
uv run spine brief --target claude --cwd /path/to/your-project
```

Load it in your session:

```
@.spine/briefs/claude/latest.md
```

#### Drift and preflight

After your oh-my-claudecode session produces commits:

```bash
uv run spine drift scan --cwd /path/to/your-project
```

If you are using SPINE's hook integration (`spine hooks install`), the preflight check runs automatically before `git push`.

---

### 4.3 Superpowers

**What Superpowers contributes:** extended tool surfaces, enhanced capabilities for Claude Code sessions, workflow acceleration.

**What SPINE contributes:** mission-level governance that constrains what those extended capabilities are applied to.

Superpowers extends *what Claude Code can do in a session*. SPINE defines *what that session should be working on*.

#### Layering SPINE on a Superpowers project

SPINE governance state lives entirely in `.spine/` and `CLAUDE.md` at the repo root. It does not interfere with Superpowers tooling.

```bash
uv run spine init --cwd /path/to/your-project
uv run spine mission set --cwd /path/to/your-project \
  --title "Your project" \
  --status active \
  --scope "..." \
  --forbid "..."
uv run spine brief --target claude --cwd /path/to/your-project
```

Load the brief at the start of any Superpowers-enhanced session. The brief grounds the session in the mission before any extended tooling runs.

#### Weekly governance loop

At the end of a Superpowers session:

```bash
# Log any significant decisions made during the session
uv run spine decision add --cwd /path/to/your-project \
  --title "..." \
  --why "..." \
  --decision "..."

# Scan for drift
uv run spine drift scan --cwd /path/to/your-project

# Generate a review
uv run spine review weekly --cwd /path/to/your-project \
  --recommendation continue \
  --notes "..."
```

The review file captures what happened and is version-controlled with the code.

---

### 4.4 OpenClaw

**What OpenClaw contributes:** AI agent sessions with structured skill loading, repo-aware startup, and file-based context management.

**What SPINE contributes:** bounded mission definition, drift detection, decision and evidence logging, mission briefs that ground the session.

OpenClaw reads `.spine/` state directly as files. SPINE does not require OpenClaw to call any API — all governance state is in plain YAML and JSONL.

#### Setup

```bash
# Initialize SPINE governance on your project
uv run spine init --cwd /path/to/your-project

# Set a bounded mission
uv run spine mission set --cwd /path/to/your-project \
  --title "Auth service v1" \
  --status active \
  --scope "auth,jwt,middleware" \
  --forbid "ui,billing,background-workers"

# Generate an OpenClaw brief
uv run spine brief --target openclaw --cwd /path/to/your-project
```

`spine init` writes `.openclaw/spine.yaml` to your repo root. This file tells OpenClaw:
- where SPINE state lives (`.spine/`)
- which brief to load at startup (`.spine/briefs/openclaw/latest.md`)
- which startup commands to run

#### Starting a session

OpenClaw reads `.openclaw/spine.yaml` at startup. The config instructs it to:

1. Run `uv run spine check before-work` — governance health check
2. Run `uv run spine brief --target openclaw` — generate a fresh brief
3. Load `.spine/briefs/openclaw/latest.md` — grounds the session in the mission

You can also load the brief manually by pointing OpenClaw at the file:

```
.spine/briefs/openclaw/latest.md
```

#### During a session

```bash
# Log evidence after completing work
uv run spine log commit "Implemented JWT verification middleware"

# Check for scope drift
uv run spine drift scan

# Record a decision
uv run spine decision add \
  --title "Used HS256 over RS256" \
  --why "Simpler for single-service deployment" \
  --decision "HS256 for JWT signing"
```

#### Before PR

```bash
uv run spine check before-pr
```

This runs `spine doctor` and `spine drift scan` together. Resolve any drift before opening the PR.

#### End of session

```bash
uv run spine review weekly --cwd /path/to/your-project \
  --recommendation continue \
  --notes "JWT middleware complete, token refresh next"
```

#### OpenClaw + SPINE compatibility summary

| Capability | Status |
|---|---|
| Read `.spine/mission.yaml` directly | ✅ First-class |
| `spine brief --target openclaw` | ✅ First-class |
| `.openclaw/spine.yaml` startup config | ✅ First-class (written by `spine init`) |
| `AGENTS.md` governance rules | ✅ First-class (runtime-agnostic) |
| `spine check before-work` / `before-pr` | ✅ Works |
| Drift detection, evidence, decisions | ✅ Works |

SPINE remains runtime-agnostic. The OpenClaw startup path is explicit and file-based — no daemon, no cloud connection, no hidden behavior.

---

## 5. Anti-drift guidance

SPINE is not trying to become any of the following:

**Not a dashboard.** SPINE has no web UI. All output is CLI, markdown files, or JSON. If you want a dashboard view of governance state, build it on top of `.spine/` YAML/JSONL — the files are stable and readable.

**Not a cloud control plane.** SPINE is entirely local. There is no remote service, no sync, no telemetry. Everything lives in the repo.

**Not a multi-agent orchestration system.** SPINE governs one active mission for one repo. It does not coordinate agents, schedule tasks, or manage concurrent sessions. Those responsibilities belong to the execution tools.

**Not a replacement for execution tools.** SPINE does not run code, make tool calls, or manage agent sessions. Claude Code, oh-my-claudecode, Superpowers, and similar tools do that. SPINE provides the governance context they operate within.

**Not a feature-comparison platform.** SPINE does not try to replace or out-feature the tools above. The goal is explicit, stable complementarity — not competition.

If SPINE starts accumulating execution, orchestration, or platform features, that is scope drift. Use `spine mission show` to check the mission, and file it against the backlog if there is a real use case.

---

## Summary

| Layer | Tool | Role |
|-------|------|------|
| Governance | SPINE | Mission, scope, drift, decisions, evidence, briefs |
| Execution | Claude Code | Interactive coding sessions, tool calls |
| Execution | OpenClaw | AI agent sessions with skill-based startup and repo awareness |
| Configuration | oh-my-claudecode | Claude Code session setup, prompts, plugins |
| Extension | Superpowers | Enhanced tool surfaces for Claude Code |
| Code | Your repo | The work |

SPINE connects to the execution layer through `.spine/briefs/`, `CLAUDE.md`, `AGENTS.md`, `.openclaw/spine.yaml`, and `--json` outputs. The integration is file-based and requires no runtime coupling.

---

*See [`external-repo-onboarding.md`](external-repo-onboarding.md) for the full quickstart guide.*  
*See [`SPINE_SPEC.md`](SPINE_SPEC.md) for the authoritative command reference.*
