---
name: spine-agent
description: Use SPINE governance commands inside any repo with a .spine/ directory. Triggers when: working in a SPINE-governed repo and need to record decisions, evidence, drift, or mission context; a brief or review is needed; a governance checkpoint (before-pr, before-work) is relevant. Also use when: adding a decision or evidence record, checking governance health (doctor), generating a brief for agent context, or running a drift scan. Do NOT trigger for general coding tasks unrelated to governance.
---

# SPINE Agent Skill

Agent-facing SPINE governance commands for repos with a `.spine/` directory.

## What SPINE Is

SPINE keeps agents aligned to a defined mission. It provides:
- **Mission context** — what the project is trying to do
- **Scope boundaries** — what is and is not in scope
- **Proof trail** — evidence and decisions that were made
- **Drift detection** — git-native scope drift scanning

Governance data lives in `.spine/*.jsonl` files (committed to git where repo policy allows) and generated outputs in `.spine/briefs/`, `.spine/reviews/` (gitignored — run `uv run spine brief --target claude` or `uv run spine review weekly` to produce them).

**Cross-repo targeting:** SPINE can target a different repo via `--cwd /path/to/repo` or `SPINE_ROOT=/path/to/other/repo`. Use this when governing a sub-repo or a repo that is not the current working directory.

Targeting resolution order: `--cwd` > `SPINE_ROOT` > current working directory.

```bash
# Long-running shell: set a session default once
export SPINE_ROOT=/path/to/repo

# One-shot: target a repo for a single command only (no shell pollution)
SPINE_ROOT=/path/to/repo spine doctor

# Verify what SPINE is currently targeting
uv run spine target
uv run spine target --json
```

## When to Use This Skill

Use SPINE when:
- Starting work in a new or unfamiliar repo
- A decision was made that should be recorded
- Evidence of work was produced that should be logged
- Unsure whether something is in scope — run `uv run spine drift scan`
- Before opening a PR — run `uv run spine check before-pr`
- Starting a session — run `uv run spine check before-work`

## First-Contact Flow

```bash
# 1. Check governance health
uv run spine doctor

# 2. Read the current mission
uv run spine mission show

# 3. If no mission exists, ask the operator to run:
uv run spine mission set --title "..." --goal "..."
```

## Standard Working Loop

```bash
# At start of session
uv run spine check before-work
uv run spine brief --target claude      # generate context brief (Claude Code)
# uv run spine brief --target openclaw  # or OpenClaw
# uv run spine brief --target codex     # or Codex

# During work — record decisions and evidence
uv run spine decision add --title "Chose X over Y" --why "..." --decision "..."
uv run spine evidence add --kind commit --description "Implemented X"

# Short-form evidence add (fewer flags, same canonical record)
uv run spine log commit "Implemented X"
uv run spine log test_pass "All tests green"
uv run spine log pr "https://github.com/.../pull/42"

# When unsure about scope
uv run spine drift scan
uv run spine drift scan --json    # machine-readable

# Before PR
uv run spine check before-pr
```

## When to Add a Decision

Record a decision when:
- A technical choice was made that future agents need to understand
- A trade-off was weighed and a direction was chosen
- Something was deliberately excluded from scope

Do not record every minor choice — record anything that would confuse a future agent or operator.

## When to Add Evidence

Record evidence when:
- A significant piece of work is complete
- A proof artifact exists (commit SHA, PR URL, test result)
- A design choice was validated or invalidated

## What to Do If SPINE State Is Weak

If `uv run spine doctor` shows warnings or the mission is thin:

1. Ask the operator to refine the mission: `uv run spine mission refine`
2. If no brief exists, generate one: `uv run spine brief --target claude`
3. Record any known decisions or context as evidence

Do not proceed with significant work in a governance vacuum. A thin mission is better than no mission — but both are signals to the operator.

## What to Do If Persistence Is Blocked

If a governance write fails because of `.gitignore`, repo policy, or workspace rules:

1. Record the intent explicitly in the work being done (commit message, PR description, inline comment)
2. Do not pretend the write succeeded
3. Note the block in the session context so the operator can resolve it

**Ephemeral outputs** (`.spine/briefs/`, `.spine/reviews/`) are gitignored by design. Governance data (decisions, evidence, drift) is in durable JSONL files and is committed to git where repo policy allows.

## Anti-Patterns

- **Do not** run `uv run spine init` in an already-governed repo — it may reset draft state
- **Do not** use `uv run spine mission set` to silently overwrite a mission without operator confirmation
- **Do not** treat generated briefs/reviews as durable records — they are ephemeral and gitignored
- **Do not** skip `uv run spine check before-pr` because it feels like overhead — it catches drift before it accumulates
- **Do not** add decisions or evidence retroactively with false timestamps — record what was done, when it was actually done

## Command Cheatsheet

| Command | When to Use |
|---------|-------------|
| `uv run spine doctor` | Check governance health |
| `uv run spine mission show` | Read current mission |
| `uv run spine mission show --json` | Machine-readable mission |
| `uv run spine mission set --title "..." --goal "..."` | Set or update mission |
| `uv run spine brief --target claude` | Generate agent context brief (Claude Code) |
| `uv run spine brief --target openclaw` | Generate agent context brief (OpenClaw) |
| `uv run spine brief --target codex` | Generate agent context brief (Codex) |
| `uv run spine check before-work` | Start-session checkpoint |
| `uv run spine check before-pr` | Pre-PR checkpoint |
| `uv run spine drift scan` | Check for scope drift |
| `uv run spine drift scan --json` | Machine-readable drift |
| `uv run spine decision add --title "..." --why "..." --decision "..."` | Record a decision |
| `uv run spine decision list` | List recorded decisions |
| `uv run spine log <kind> "<description>"` | Record evidence (short form) |
| `uv run spine evidence add --kind <kind> --description "..."` | Record evidence (full form) |
| `uv run spine evidence list` | List recorded evidence |
| `uv run spine drafts list` | List pending drafts |
| `uv run spine drafts confirm <id>` | Promote a draft to canonical |
| `uv run spine target` | Show currently resolved target repo + source |
| `uv run spine target --json` | Machine-readable target info |

---

Use SPINE where it genuinely fits. If governance writes are blocked by `.gitignore`, repo policy, or workspace rules, record that explicitly and do not pretend persistence succeeded.
