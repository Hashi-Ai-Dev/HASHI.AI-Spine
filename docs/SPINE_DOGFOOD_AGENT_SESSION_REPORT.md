# SPINE Dogfood Agent Session Report

**Session date:** 2026-04-09  
**Evaluator:** Claude (claude-sonnet-4-6), simulating an external coding agent  
**Branch:** `eval/spine-dogfood-agent-session`  
**Base branch:** `claude/eval-spine-agent-workflow-kNUqa`

---

## A. Session Context

### Branch Used
`eval/spine-dogfood-agent-session` — created at session start from the assigned evaluation branch.

### Task Chosen
**Add `spine doctor` warnings for blank critical mission fields.**

Specifically: when `mission.yaml` has empty `target_user`, `user_problem`, `one_sentence_promise`, or `success_metric.value`, `doctor` should emit a WARNING and suggest running `spine mission set`.

### Why It Was a Good Test

1. **Real gap**: The active SPINE self-governance mission had all four critical fields blank. `doctor` passed PASS anyway. The generated brief was nearly useless boilerplate.
2. **Bounded but non-trivial**: Required reading the doctor service, understanding the model, writing tests, and fixing a secondary bug found in the process (`--quiet` mode).
3. **Genuine drift temptation**: While implementing, there was constant pull toward adding `--fix` interactive mode, a completeness score, a `mission check` subcommand, `allowed_scope` checks, constraints warnings, etc. The governance log captured the decision to resist all of these.
4. **Dogfood-appropriate**: The fix directly improves the experience for the next agent to use SPINE on a fresh repo.

### Known Blockers Encountered
None blocking. One secondary bug found and fixed: `--quiet` mode printed the warnings table unconditionally even on success, violating its documented contract.

---

## B. Workflow Trace

### Command sequence used

```
# Initial orientation
uv run spine doctor
uv run spine mission show
uv run spine check before-work      # → EXIT 1 (REVIEW RECOMMENDED — no brief)

# Create eval branch
git checkout -b eval/spine-dogfood-agent-session

# Generate brief
uv run spine brief --target claude  # → brief generated (mostly empty)

# Re-check orientation
uv run spine check before-work      # → PASS now

# Record decision before coding
uv run spine decision add --title ... --why ... --decision ... --alternatives ...

# Implement task (doctor_service.py + doctor_cmd.py + tests)
uv run pytest tests/test_doctor.py  # → 12 passed
uv run pytest                       # → found 1 failure (--quiet bug)
# Fix --quiet issue
uv run pytest                       # → 505 passed

# Log evidence
uv run spine evidence add --kind commit --description ...

# Pre-PR check
uv run spine check before-pr        # → PASS
```

### Where the Workflow Felt Smooth

- `check before-work` → `brief` → `check before-work again` is a logical loop that makes sense once you understand it.
- `decision add` before coding felt natural and the log entry was useful — it captured the scope boundary explicitly, which genuinely affected behavior (I resisted adding `--fix` because I had already written out why that would be drift).
- `check before-pr` as a final step felt like a real CI-style gate, not just noise.
- `doctor` running cleanly with actionable output felt professional.

### Where the Workflow Felt Awkward

1. **Initial `check before-work` exits 1** — before generating a brief, the check fails with "REVIEW RECOMMENDED." For a first-run agent with no prior context, this is disorienting. The message should say "PASS WITH NOTE: no brief exists yet — run `spine brief --target claude`" rather than exit 1.
2. **Mission is silently blank** — the active SPINE self-governance mission had an empty `target_user`, `user_problem`, and `one_sentence_promise`. Neither `doctor` nor `mission show` called this out before my fix. The brief then generated a document that looked official but contained no real guidance.
3. **The brief from a blank mission is misleading** — it says "Mission Summary" with blank fields and acceptance criteria about evidence logging, but doesn't say "warning: this mission is not configured." An agent loading this brief gets no real context.
4. **Command sequencing is undocumented in CLAUDE.md** — CLAUDE.md lists commands but doesn't give a recommended session flow. A new agent has to infer: doctor → mission show → brief → check before-work → work → decision add → evidence add → check before-pr.
5. **`before-pr` truncates doctor warnings**: the check showed "(and 1 more)" — lossy. A machine parsing this JSON output would get truncated strings.

---

## C. Discipline-Tax Review

### Did SPINE reduce chaos or add ceremony?

Both, unevenly. It reduced chaos by forcing me to write out the decision rationale before touching code — that genuinely influenced behavior. It added ceremony by requiring specific flags on every `evidence add` and `decision add` invocation.

### Where did it feel worth it?

- `decision add` before coding: the act of writing `--alternatives` made me notice I was tempted by scope expansion and name it explicitly. That's real value.
- `check before-pr` as a gate: the checklist feeling is useful. If anything fails, you have a forcing function to investigate.
- `doctor` giving a clear table of issues: actionable output is good.

### Where did it feel annoying?

- `evidence add` requires `--kind` from a fixed enum and a `--description`. The enum values (`brief_generated`, `commit`, `pr`, `test_pass`, `review_done`, `demo`, `user_feedback`, `payment`, `kill`, `narrow`) feel incomplete and oddly curated — `test_pass` and `payment` coexist? For a brief note like "ran tests, all green," this feels over-structured.
- There is no `spine evidence list` or `spine decision list`. You can append records but cannot easily review them from the CLI without reading the JSONL file directly. This makes the log feel write-only.
- `doctor` producing 4 warnings on every fresh repo (missing subdirectories + now blank mission) means operators habituate to warning noise immediately. Warning fatigue on day zero.

### What steps were most likely to be skipped by a real agent?

1. `brief` generation — takes an extra step, generates output that looks official but may be empty. An agent under pressure skips this.
2. `decision add` — verbose flags required, easy to justify skipping ("I'll log it after").
3. `evidence add` — same problem. Under time pressure, the output side of SPINE collapses first.
4. `check before-work` re-run after brief generation — the two-step process (check → warn → generate brief → check again) is non-obvious and likely to be short-circuited.

---

## D. Agent-Usability Review

### Did SPINE feel agent-friendly?

Partially. The `--json` output mode on most commands is good. The exit codes are well-defined. The `brief` generation targeting (`--target claude`) is the right abstraction.

But there are gaps:

### Were the command contracts/tooling surfaces good enough?

- `--json` is not consistently documented. The README says it's only available on `mission show`, `doctor`, `review weekly` — this is wrong. `check before-work`, `check before-pr`, `brief`, `evidence add`, `decision add` all support `--json`. This is a real documentation gap.
- `check before-work` exits 1 for "review recommended" situations (e.g., no brief). A CI pipeline treating exit 1 as "do not proceed" would be blocked unnecessarily on a fresh repo.
- The `doctor` check embedded inside `check before-pr` shows a truncated warning summary: "(and 1 more)". The JSON output of `before-pr` is not affected, but the human output loses information.

### Where was machine-readable behavior weak?

1. **`brief` has no `--json` output for the generated content itself** — it outputs a file path but the brief content isn't surfaced in a machine-readable way. An agent wanting to read the brief programmatically must parse the file path from stdout and then read the file. The `--json` flag for `brief` is not documented.
2. **Evidence kinds are not queryable** — there's no way to ask "how many `commit` evidences in the last week?" from the CLI. The records exist but are opaque unless you parse the JSONL directly.
3. **`check before-pr` doctor detail is a prose string** — the nested doctor output inside `before-pr --json` is a freeform string, not a structured list of issues. An agent parsing this cannot programmatically distinguish warnings from errors.

### What would make repeated use easier?

1. A `spine status` command that summarizes everything: mission completeness, evidence count, decisions count, last brief date, last review date, drift status. One stop for orientation.
2. `spine evidence list` and `spine decision list` — the record is write-only right now.
3. A `--session` concept — begin a session, track all adds/changes, close the session. Reduces the per-command ceremony.

---

## E. Drift-Resistance Review

### Did SPINE actually keep the task bounded?

Yes, meaningfully. Writing the `decision add` entry with explicit alternatives forced me to name the scope-expanding options before implementing. The act of writing "Do NOT add --fix flag, interactive prompts, or auto-fill" in the decision record created a visible constraint I could reference.

### Where could drift still slip through?

1. **The mission is blank** — if `allowed_scope` and `forbidden_expansions` are both empty, `drift scan` has nothing to check against. The governance structure exists but enforces nothing.
2. **`drift scan` is not integrated into `check before-pr`** — there's a `drift` check in `before-pr` but it checks `drift.jsonl` for logged entries, not whether actual git changes are in scope. An agent that never runs `drift scan` will always get `drift: PASS`.
3. **No mechanism prevents ignoring governance entirely** — SPINE works on the honor system. An agent that doesn't run `check before-work` faces no consequence.

### Did the governance model influence your behavior meaningfully?

Yes, once. The `decision add` step influenced my implementation choices. The `check before-pr` step made me confirm the session was complete. Beyond those two moments, the governance model was mostly background.

The biggest influence was `decision add` before coding. That is SPINE's highest-value single workflow.

---

## F. Product Judgment

### As an agent/operator, would you actually want to use SPINE again?

Yes, but with conditions. The `decision add` → code → `evidence add` → `check before-pr` loop is worth keeping. It creates a real audit trail with no cloud dependency.

The blank mission problem is the biggest barrier to reuse. If a new agent encounters SPINE with a blank mission.yaml and generates a brief that says "Target User: (blank)", they will immediately lose trust in the tool and stop using it.

### Why or why not?

**Would use again:**
- Lightweight — no daemon, no cloud, plain YAML/JSONL
- The decision log with `--alternatives` is genuinely valuable
- `check before-pr` as a gate ritual has low cost and high signal
- Agent brief generation is the right idea

**Would be annoyed by:**
- Blank mission silently producing useless briefs (fixed by this session, but the init flow doesn't guide the user to fill it in)
- No list commands — the log is append-only, write-only from CLI perspective
- First-run sequencing non-obvious and somewhat alarming (exit 1 before brief)
- Warning fatigue from day-zero warning noise (4 warnings on fresh init)

### What are the top improvements needed before beta exit?

1. **Guided `init` flow** — after `spine init`, prompt "Run `spine mission set` to define your mission before generating briefs." The current init creates a placeholder that looks complete but is empty.
2. **`spine status` command** — single-command orientation covering mission completeness, brief freshness, evidence/decision counts, drift status.
3. **`spine evidence list` / `spine decision list`** — even read-only is enough. The log must be queryable from CLI.
4. **Fix README `--json` coverage** — currently claims only 3 commands; actually 7+ support it.
5. **`check before-work` exit code calibration** — "no brief yet" should be exit 0 with a note, not exit 1. Exit 1 should be reserved for real problems.
6. **`drift scan` integration** — `check before-pr` should optionally run `drift scan` inline, not just check whether past scan results were logged.

---

## G. Findings List

| # | Severity | Category | Finding |
|---|----------|----------|---------|
| 1 | high | workflow | Blank mission.yaml silently passes doctor and produces useless briefs. `doctor` never warned about empty `target_user`, `user_problem`, `one_sentence_promise`. **Fixed in this session.** |
| 2 | high | bug | `--quiet` mode on `doctor` printed warnings table on success, violating documented contract. **Fixed in this session.** |
| 3 | high | docs | README states `--json` is available only on `mission show`, `doctor`, `review weekly`. Actually 7+ commands support it. |
| 4 | high | workflow | `check before-work` exits 1 when no brief exists. This is alarming and counterproductive for first-run agents. |
| 5 | high | workflow | No `spine evidence list` or `spine decision list` commands. Records are append-only, write-only from CLI. |
| 6 | medium | workflow | Session start sequence (doctor → mission show → brief → check before-work) is undocumented. CLAUDE.md lists commands but no recommended flow. |
| 7 | medium | workflow | `check before-pr` doctor detail uses "(and 1 more)" truncation in human output. |
| 8 | medium | tooling | `check before-pr --json` embeds doctor warnings as a prose string, not structured data. Agent cannot programmatically distinguish warning types. |
| 9 | medium | workflow | Warning fatigue on fresh init: 4 warnings (missing subdirs + blank mission). New users see noise immediately. |
| 10 | medium | workflow | No `spine status` command for single-command orientation. |
| 11 | medium | workflow | `drift scan` not integrated into `check before-pr` inline — only checks for pre-logged drift events. An agent that skips `drift scan` always passes drift check. |
| 12 | low | workflow | `evidence add` kind enum includes `payment` and `kill` alongside `commit` and `test_pass`. Feels like category mismatches at the usage tier where most agents operate. |
| 13 | low | docs | `brief` command does not document `--json` flag behavior or mention it surfaces a file path. |
| 14 | low | workflow | `spine init` creates placeholder mission titled "Define active mission" but does not guide the user to fill it in. |
| 15 | blocker | — | None encountered. |

---

## H. Recommended Handling

| Finding | Recommended Action |
|---------|-------------------|
| 1 (blank mission, no warning) | ~~GitHub issue~~ — **fixed in this session** |
| 2 (--quiet bug) | ~~GitHub issue~~ — **fixed in this session** |
| 3 (README --json coverage) | **docs fix** — update README "Current Capabilities" section |
| 4 (before-work exit 1 on no brief) | **GitHub issue** — change to exit 0 with advisory note |
| 5 (no list commands) | **GitHub issue** — `spine evidence list` + `spine decision list` |
| 6 (undocumented session flow) | **docs fix** — add recommended agent workflow to CLAUDE.md quick reference |
| 7 (truncated doctor detail) | **GitHub issue** — truncation should not lose information |
| 8 (before-pr JSON not structured) | **GitHub issue** — nested doctor output should be structured |
| 9 (warning fatigue on init) | **later product note** — consider deduplicating subdirectory warnings |
| 10 (no status command) | **GitHub issue** — `spine status` for single-command orientation |
| 11 (drift scan not inline) | **later product note** — consider optional inline scan in before-pr |
| 12 (evidence kind enum) | **later product note** — review kind taxonomy for clarity |
| 13 (brief --json undocumented) | **docs fix** — minor README/help text update |
| 14 (init guidance) | **docs fix** — add `spine mission set` prompt to init output |

---

## SPINE Usage During Session

**Commands used (non-ceremonial):**

| Command | Purpose |
|---------|---------|
| `spine doctor` | Initial orientation, confirmed warnings |
| `spine mission show` | Read active mission, discovered blank fields |
| `spine check before-work` | Pre-work gate (failed first, passed after brief) |
| `spine brief --target claude` | Generated orientation brief |
| `spine decision add` | Recorded task decision with alternatives before coding |
| `spine evidence add` | Logged completed work |
| `spine check before-pr` | Pre-commit gate |

**Governance records added:**
- 1 decision record (task choice + scope boundary)
- 1 evidence record (commit summary)

---

_Generated by: Claude (claude-sonnet-4-6) — dogfood evaluation session 2026-04-09_  
_Branch: `eval/spine-dogfood-agent-session`_
