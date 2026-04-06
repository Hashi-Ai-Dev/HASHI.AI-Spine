# SPINE: Origin and Product Thesis v0.1

## What SPINE Is

SPINE (Strategic Proof & Intelligent Navigation Engine) is a repo-native mission governor for solo builders who work with AI coding agents. It sits above the agent layer and provides governance: bounding execution, tracking evidence, detecting drift, and forcing regular review.

## The Real Problem SPINE Targets

The problem is not lack of coding power. Modern AI coding agents can generate enormous amounts of code quickly. The problem is:

- **Too many serious project lanes.** Solo builders juggle multiple projects or multiple directions within a project. Context switching silently expands scope.
- **Silent scope expansion.** Agents, eager to help, add features that were never requested. The codebase grows but the mission doesn't advance.
- **Repo drift away from the actual mission.** After weeks of work, the repo looks nothing like what was originally intended. The mission was killed months ago but the code keeps growing.
- **Confusing activity for proof.** Lots of commits and lots of code feel like progress. They are not proof of progress.
- **Weak continuity between planning, execution, evidence, and review.** These four activities are usually disconnected. Plans live in one place, execution in another, evidence is scattered, and review is either skipped or done from memory.

## Founder-Market Fit

Solo builders who use AI coding agents are SPINE's target user. They:
- Have more coding capacity than before (AI amplifies their output)
- Lack the structure that larger teams provide naturally (code review, PMs, standups)
- Need to stay focused on one mission long enough to actually ship something
- Need visibility into whether they're making real progress or just producing code

SPINE is not for teams. It is not for enterprises. It is for the individual builder who has been burned by scope expansion and wants a forcing function that keeps them honest.

## Inspirations

SPINE is inspired by:

- **Repo-native agent workflows** — agents that read repo state and respect repo-level governance
- **AGENTS.md style shared repo instructions** — explicit agent guidance living alongside code
- **Claude Code and Codex worktree and planning discipline** — bounded execution with explicit planning
- **Obra/superpowers for skills-first workflow discipline** — explicit skill definitions that constrain what agents can do
- **Oh-my-claudecode for operator-grade orchestration and visibility** — CLI-first control surfaces

## What SPINE Borrows

SPINE intentionally adopts proven patterns:
- Repo-native instructions (AGENTS.md pattern)
- Skill-driven execution (explicit capabilities, not general intelligence)
- Worktree discipline (bounded execution contexts)
- Plan-before-code logic (explicit planning before non-trivial work)
- Explicit acceptance criteria (what "done" looks like)
- Source-controlled checks (governance rules in git)
- Staged execution flow (init → plan → execute → evidence → review)
- Structured brief generation (explicit context for agents)
- Local-first control surfaces (CLI, not web)
- MCP-readable state exposure (machine-readable governance state)

## What SPINE Improves

SPINE does not just copy these patterns—it connects them:

- AGENTS.md is advisory; SPINE makes it contractual (forbidden expansions are enforced)
- Briefs exist in isolation; SPINE generates them from the mission state
- Evidence is usually in someone's head; SPINE requires it to be logged
- Review is usually skipped; SPINE makes it weekly and structured
- Drift is usually discovered too late; SPINE scans for it deterministically after every session

## What SPINE Rejects

SPINE intentionally does NOT become:
- **Another chat wrapper.** SPINE is not a better conversational interface. It is a governance layer.
- **Dashboard-first theater.** Visibility is for agents and humans reading files, not for showing stakeholders charts.
- **Autonomous swarm fantasy in v0.1.** In v0.1, SPINE does not run agents autonomously. It governs them.
- **Life-OS creep.** SPINE manages the repo and the mission. It does not manage your calendar, email, or life.
- **Abstract architecture worship.** SPINE is concrete. It uses files. It has a CLI. It does not need a diagram to explain.
- **Required live model dependency in v0.1.** All scoring and drift detection are deterministic. No API calls required.

## The Core Warning: Against Becoming the Sprawl Machine

SPINE exists to cure the sprawl machine. The core danger is that SPINE itself becomes the sprawl machine it set out to cure.

Signs this is happening:
- SPINE grows new commands that aren't in the spec
- SPINE starts tracking things that don't directly relate to the active mission
- SPINE adds dashboards, charts, or "insights" that nobody asked for
- SPINE acquires a database before it has proven the file-based approach fails
- SPINE starts depending on live model access before that is strictly necessary
- SPINE adds multi-user or collaboration features before a single-user workflow is solid

The discipline is: **everything new must pass through the mission filter.** If it doesn't advance the active mission or enforce its boundaries, it doesn't belong in SPINE.

## Long-Term Direction

Phase 1 (done): Bootstrap. `spine init` establishes the contract.

Phase 2 (current): Core governance. Commands that read/write mission state, generate briefs, track evidence, detect drift, run weekly reviews, and expose state via MCP.

Phase 3 (future): SQLite projection and optional model-assisted scoring for opportunity identification.

Phase 4 (future): Multi-mission support, web-based mission dashboard.

The long-term bet is that the file-based approach is sufficient for most solo builders, and that model integration (Phase 3+) remains optional. The MCP server is the integration point when model assistance is desired, not a required dependency.

## Product Thesis

**The solo builder's problem is not coding capacity. It is focus, evidence, and continuity.**

SPINE provides:
- **Focus** through bounded scope (forbidden_expansions are enforced, not advisory)
- **Evidence** through mandatory logging (evidence.jsonl, decisions.jsonl)
- **Continuity** through weekly reviews that aggregate evidence and force a recommendation

Without these three things, solo builders ship code but not products. SPINE is the forcing function that keeps the mission alive through the noise of execution.
