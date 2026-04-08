# External Repo Onboarding Guide

This guide covers how to use SPINE on a repo that is not the SPINE repo itself.

SPINE is installed once and governs any number of target repos via the `--cwd` flag or `SPINE_ROOT` env var.

---

## Contents

1. [Quickstart](#quickstart)
2. [Governance Walkthrough](#governance-walkthrough)
3. [Targeting: `--cwd` vs `SPINE_ROOT`](#targeting---cwd-vs-spine_root)
4. [Verification](#verification)
5. [Common Friction / FAQ](#common-friction--faq)

---

## Quickstart

**Prerequisites:** Python 3.12+, [uv](https://github.com/astral-sh/uv), a git repository to govern.

### Step 1: Install SPINE

```bash
git clone https://github.com/Hashi-Ai-Dev/SPINE
cd SPINE
uv sync
```

You do not need to install SPINE into your target repo. SPINE lives in its own directory and targets other repos from there.

### Step 2: Initialize governance state

```bash
uv run spine init --cwd /path/to/your-repo
```

This creates a `.spine/` directory inside your target repo with all required governance files.

### Step 3: Set your mission

```bash
uv run spine mission set --cwd /path/to/your-repo \
  --title "My Project" \
  --status active \
  --scope "api,backend" \
  --forbid "ui,auth,billing"
```

### Step 4: Verify governance state

```bash
uv run spine doctor --cwd /path/to/your-repo
```

A clean pass looks like:

```
Doctor check passed.
```

Warnings about missing subdirectories (reviews, briefs, skills, checks) are expected on a fresh init — those directories are created on first use.

### Step 5: Generate a mission brief

```bash
uv run spine brief --target claude --cwd /path/to/your-repo
```

The brief is written to `.spine/briefs/claude/` inside your target repo. Load it into your agent session to ground it in the mission.

That's the minimal setup. Your target repo now has a bounded mission and a governance layer your agents can read.

---

## Governance Walkthrough

This section shows a realistic governance loop for an active project.

Assume SPINE is installed at `/home/you/SPINE` and you are governing a project at `/home/you/my-api`.

### Initialize and set mission

```bash
uv run spine init --cwd /home/you/my-api

uv run spine mission set --cwd /home/you/my-api \
  --title "my-api v1" \
  --status active \
  --target-user "internal platform team" \
  --user-problem "no stable internal API contract" \
  --promise "deliver a stable, versioned REST API for internal consumers" \
  --scope "rest-api,openapi,auth-middleware" \
  --forbid "ui,billing,background-workers" \
  --metric-type milestone \
  --metric-value "first consumer integrated"
```

### Inspect the mission

```bash
uv run spine mission show --cwd /home/you/my-api
```

### Generate a brief before an agent session

```bash
uv run spine brief --target claude --cwd /home/you/my-api
```

Brief is written to `/home/you/my-api/.spine/briefs/claude/`. Load it in Claude Code as `@.spine/briefs/claude/latest.md`.

### Log evidence during work

After committing meaningful work:

```bash
uv run spine evidence add --cwd /home/you/my-api \
  --kind commit \
  --description "Implemented /users endpoint with OpenAPI schema"

uv run spine evidence add --cwd /home/you/my-api \
  --kind test_pass \
  --description "All endpoint tests passing, 42 tests"
```

### Log a decision

When a significant architectural choice is made:

```bash
uv run spine decision add --cwd /home/you/my-api \
  --title "Use JWT for auth middleware" \
  --why "Existing infra already has a JWT issuer; reduces integration cost" \
  --decision "Adopt JWT verification middleware, no new auth service" \
  --alternatives "OAuth2 server, API key table"
```

### Scan for drift

Before opening a PR, check whether your work is inside the mission boundary:

```bash
uv run spine drift scan --cwd /home/you/my-api
```

To compare your branch against main explicitly:

```bash
uv run spine drift scan --cwd /home/you/my-api --against main
```

Clean output means no forbidden changes were detected. If drift is flagged:

```
Severity  Path          Reason
HIGH      ui/dashboard  Matches forbidden scope: ui
```

Address the drift before proceeding.

### Generate a weekly review

At the end of a work session or week:

```bash
uv run spine review weekly --cwd /home/you/my-api \
  --recommendation continue \
  --notes "Endpoints on track, auth middleware next"
```

The review is written to `/home/you/my-api/.spine/reviews/YYYY-MM-DD.md`. It aggregates evidence, decisions, and drift from the last 7 days.

---

## Targeting: `--cwd` vs `SPINE_ROOT`

Every SPINE command accepts a target repo. If you do not specify one, SPINE defaults to the current working directory — usually the SPINE repo itself, which is probably not what you want.

### Option A: `--cwd` per command

Pass `--cwd <path>` on every command to explicitly target a repo.

```bash
uv run spine doctor       --cwd /home/you/my-api
uv run spine mission show --cwd /home/you/my-api
uv run spine drift scan   --cwd /home/you/my-api
```

**When to use:** Whenever you are running commands interactively and want clarity about which repo is targeted. Preferred for one-off commands and CI scripts.

### Option B: `SPINE_ROOT` env var

Set `SPINE_ROOT` for your shell session to avoid repeating `--cwd` on every command.

```bash
export SPINE_ROOT=/home/you/my-api

uv run spine doctor
uv run spine mission show
uv run spine drift scan
```

**When to use:** When running many commands against the same repo in a single shell session, or when scripting a governance loop for one target.

**Important:** `SPINE_ROOT` is process-global. If it is set in your shell profile, every SPINE command you run is affected. Unset it before switching to a different target repo.

```bash
unset SPINE_ROOT
```

### Precedence order

When SPINE resolves the target repo, it checks in this order:

1. `--cwd <path>` — explicit per-command flag (highest priority)
2. `SPINE_ROOT` — environment variable
3. Current working directory — fallback

`--cwd` always wins over `SPINE_ROOT`. There is no way for `SPINE_ROOT` to override an explicit `--cwd`.

### Avoiding targeting confusion

Common mistakes:

- Running `uv run spine doctor` from the SPINE directory without `--cwd` — this governs the SPINE repo, not your project.
- Setting `SPINE_ROOT` in `~/.bashrc` and forgetting it — all commands target the wrong repo.
- Using a relative path with `--cwd` — use absolute paths to avoid ambiguity.

Best practice: always use `--cwd` with an absolute path unless you are running a long governance session against one repo.

---

## Verification

After running `spine init`, here is how to confirm SPINE is working correctly in your target repo.

### Expected files

After `spine init --cwd /path/to/your-repo`, the following must exist inside your target repo:

```
/path/to/your-repo/
├── .spine/
│   ├── mission.yaml        ← mission definition (required)
│   ├── constraints.yaml    ← operational constraints (required)
│   ├── evidence.jsonl      ← append-only evidence log
│   ├── decisions.jsonl     ← append-only decision record
│   ├── drift.jsonl         ← drift scan log
│   ├── runs.jsonl          ← agent run log
│   ├── opportunities.jsonl ← opportunity scores
│   └── not_now.jsonl       ← deferred ideas
├── AGENTS.md               ← agent guidance (all agents)
├── CLAUDE.md               ← Claude Code-specific rules
├── .claude/
│   └── settings.json
└── .codex/
    └── config.toml
```

### Doctor output

Run:

```bash
uv run spine doctor --cwd /path/to/your-repo
```

A healthy repo produces:

```
Doctor check passed.
```

Warnings about missing subdirectories (`reviews/`, `briefs/`, `skills/`, `checks/`) are expected on a fresh init. These subdirectories are created on first use and do not affect governance correctness.

A **failed** doctor indicates a required file is missing or malformed. The output names the specific file and issue. Fix the file or re-run `spine init`.

### Confirming the mission is set

```bash
uv run spine mission show --cwd /path/to/your-repo
```

If `title` and `status` are populated, the mission is set. If `status` is still the default placeholder, run `spine mission set`.

### What "healthy enough to proceed" looks like

- `spine doctor` passes (with or without subdirectory warnings)
- `spine mission show` returns a populated title and `active` status
- `spine brief --target claude` writes a file without error
- `.spine/` directory is committed to version control

You do not need a clean drift scan to proceed. Drift scanning is a check — it does not block work.

---

## Common Friction / FAQ

### "spine init says 'not a git repository'"

SPINE requires the target repo to be a git repository. Initialize git first:

```bash
cd /path/to/your-project
git init
git add .
git commit -m "initial commit"
```

Then run `spine init --cwd /path/to/your-project`.

If you genuinely need to initialize SPINE in a non-git directory, pass `--allow-no-git`. Note that drift scanning will not work without git.

### "`.spine/` directory is missing after init"

Check that `--cwd` pointed to the correct path. Run:

```bash
ls /path/to/your-repo/.spine/
```

If missing, re-run `spine init --cwd /path/to/your-repo`. Existing files are not overwritten by default.

### "mission.yaml exists but mission fields are empty"

`spine init` creates a minimal `mission.yaml` with placeholder values. You must explicitly set the mission:

```bash
uv run spine mission set --cwd /path/to/your-repo \
  --title "Your Project Name" \
  --status active \
  --scope "comma,separated,scope" \
  --forbid "comma,separated,forbidden"
```

### "spine doctor says mission is missing"

The `.spine/mission.yaml` file is missing or does not parse. Check:

```bash
cat /path/to/your-repo/.spine/mission.yaml
```

If the file is missing, re-run `spine init`. If the YAML is malformed, edit it directly to correct the syntax.

### "I'm targeting the wrong repo"

If commands are operating on the SPINE repo instead of your project, you have a targeting issue. Confirm the target:

```bash
uv run spine mission show --cwd /path/to/your-repo
```

If this shows SPINE's own mission, `--cwd` is not pointing where you expect. Check the path:

```bash
ls /path/to/your-repo/.spine/
```

If `SPINE_ROOT` is set in your environment, it may be overriding your intent. Check:

```bash
echo $SPINE_ROOT
```

Unset it if necessary: `unset SPINE_ROOT`.

### "Using SPINE on another repo vs using SPINE on itself"

When you run SPINE on the SPINE repo (no `--cwd`), you are using SPINE for self-governance — the same pattern used during SPINE's own development. This is valid but distinct from external-repo use.

For external repos, always use `--cwd`. The `.spine/` directory belongs to and lives inside the repo being governed. SPINE itself has no shared state between repos — each `.spine/` is fully isolated.

### "drift scan shows no output"

A clean drift scan with no output means no forbidden changes were detected in the working tree or on the current branch relative to the default branch. That is the expected output when governance is healthy.

If you expected drift to be flagged:
- Confirm forbidden scope is set: `spine mission show --cwd ...` and check `forbidden_expansions`
- Confirm the changes are staged or committed: `git status` in the target repo
- Untracked files are intentionally not flagged — they must be staged or committed first

---

*For the full command reference, see [`SPINE_OFFICIAL_SPEC_v0.1.md`](SPINE_OFFICIAL_SPEC_v0.1.md).*
*For the current implementation status, see [`SPINE_STATUS.md`](SPINE_STATUS.md).*
*For guidance on layering SPINE with Claude Code, oh-my-claudecode, or Superpowers, see [`SPINE_INTEGRATIONS.md`](SPINE_INTEGRATIONS.md).*
