# SPINE Roadmap

SPINE is a repo-native mission governor for AI coding workflows.
It sits above coding agents and helps keep work:

- focused
- bounded
- reviewable
- evidence-backed
- resistant to drift

This roadmap explains:

- where SPINE is today
- what must happen before it exits alpha
- what beta is for
- what "v1.0.0" should actually mean

---

## Current Status

SPINE is currently in **public beta** (`v0.2.0-beta`).

Alpha exit is complete. Phase 3A delivered:

- explicit repo targeting + `--cwd` precedence normalization
- repo/branch context visibility + deterministic default branch resolution
- stable exit codes + `--json` output modes
- bootstrap polish + discipline-tax ergonomics
- artifact ergonomics contract
- external-repo onboarding docs

The current active stage is:

> **Beta — Repeated-use proof, discipline-tax reduction, agent-executable governance**

Beta is focused on making SPINE sustainable in repeated real workflows — reducing governance overhead for agents and operators without hiding what happens.

---

## Product Direction

SPINE is not trying to become another coding agent, a dashboard product, or a cloud control plane.

Its direction is:

- governance above generation
- repo-native truth
- deterministic, inspectable behavior
- clear human authority
- agent-friendly execution surfaces

A core product rule guides this roadmap:

> **Agents may execute governance mechanics. Operators retain governance authority.**

That means SPINE should reduce operational friction without hiding what happened, silently mutating repo truth, or replacing operator judgment.

---

## Alpha Exit

**Complete.** Alpha exit criteria were met and `v0.2.0-beta` was released on 2026-04-07.

All Phase 3A goals delivered:

- [x] repo targeting is explicit and predictable
- [x] repo / branch / compare-context visibility is trustworthy
- [x] machine-readable output exists where justified
- [x] exit behavior is stable and documented
- [x] artifact references are easy to inspect and automate against
- [x] bootstrap/install guidance is clear for non-SPINE repos
- [x] external-repo docs/examples are strong
- [x] no unwanted scope drift crept in

---

## Beta

### Goal

Beta is where SPINE proves it can be used repeatedly in real workflows **without turning governance into exhausting ceremony**.

This is where SPINE should more seriously reduce **discipline tax**.

### What "discipline tax" means

Discipline tax is the accumulated effort cost of using governance consistently over time.

If governance requires too much manual repetition, people will:

- agree with it
- admire it
- then skip parts of it in real work

Beta should attack that problem directly.

### Beta Direction

SPINE should reduce discipline tax **not** by hiding governance, but by making governance easier for agents and tools to execute explicitly.

That means "agent-friendly" should look like:

- stable command contracts
- machine-readable outputs
- deterministic repo targeting
- visible context
- predictable artifact locations
- auditable state changes
- easy handoff between tools

It should **not** look like:

- hidden background behavior
- silent auto-logging
- invisible scope changes
- automation that obscures authority or truth

### Beta Workstreams

#### Task-scoped governance lanes

Make it easier to govern bounded work without polluting canonical mission state.

Possible outcomes:

- issue-scoped brief generation
- task-scoped governance lanes
- clearer branch-local workflows

#### Handoff and PR-prep primitives

Reduce discipline tax where real work changes hands.

Possible outcomes:

- PR governance summaries
- evidence rollups
- handoff summaries
- "what changed against mission" reports

#### Preflight / checkpoint commands

Turn governance into explicit checkpoints.

Possible outcomes:

- before-work checks
- before-PR checks
- after-test checks

#### Draftable evidence / decision workflows

Let agents draft governance records without becoming the final authority.

Possible outcomes:

- draft evidence helpers
- draft decision helpers
- clearer proposed-vs-canonical distinction

#### Stronger local tool-consumption surfaces

Improve local agent/tool consumption of SPINE state without drifting into cloud/platform territory.

Possible outcomes:

- richer local MCP resources
- stable schemas for current mission, latest brief, open drift, latest review, recent evidence/decisions

#### Branch-local governance hygiene

Make branch-local governance safer and less error-prone.

Possible outcomes:

- keep-local vs promote-canonical flows
- protections against accidental canonical churn

### Beta Success Criteria

Beta is working if:

- agents can execute governance mechanics reliably
- humans still control mission and scope authority
- repeat use feels lighter, not heavier
- governance remains repo-native and inspectable
- SPINE is clearly useful on repos beyond SPINE itself

---

## v1.0.0

### Goal

v1.0.0 does not mean "finished forever."

It means:

- the core governance model is stable
- the trust model is stable
- the file/state contracts are stable
- the tool is dependable enough for repeated real use

### What v1.0.0 should lock down

#### 1. Stable command contracts

The core CLI should feel settled and dependable.

#### 2. Stable file/state contracts

The `.spine/` model should be documented, durable, and migratable.

#### 3. Stable authority boundaries

The line between:

- agent-executable governance mechanics
- operator-authorized governance decisions

must be clear and trustworthy.

#### 4. Stable automation-facing surfaces

Machine-readable outputs, exit codes, artifact conventions, and local tool-consumption surfaces should be stable enough for real tooling to rely on.

#### 5. Real-world usage proof

SPINE should reach 1.0 when there is evidence of repeated use:

- on SPINE itself
- on unrelated repos
- across real AI-assisted development workflows

#### 6. Documentation maturity

By v1, docs should cleanly cover:

- quickstart
- external-repo usage
- command reference
- governance model
- architecture/spec
- troubleshooting
- migration/versioning
- advanced workflows

#### 7. Maintenance maturity

By v1, the repo and release process should feel normal, boring, and dependable:

- clean milestones
- versioned releases
- issue hygiene
- release-note discipline
- contribution/security/community docs
- solid CI

### v1.0.0 Success Criteria

SPINE is ready for 1.0.0 when:

- the governance model is stable
- the authority boundaries are stable
- the repo-native trust model is stable
- the automation-facing surfaces are stable
- repeated use on real repos is demonstrated
- the open-source maintenance story is credible

---

## Open-source / GitHub Maturity

### Alpha

Minimum credible baseline:

- public repo
- clean default branch
- branch protection
- release tags
- `LICENSE`
- `SECURITY.md`
- CI
- roadmap/backlog/status docs
- milestone and issue tracking

### Beta

Expected improvements:

- issue templates
- PR template
- contribution guide
- changelog discipline
- stronger CI coverage
- better docs index and contributor guidance
- clearer maintenance expectations

### v1.0.0

Expected maturity:

- dependable release cadence
- documented migration/versioning expectations
- durable issue/milestone hygiene
- strong community and security surfaces
- repo/org state that looks normal and trustworthy

---

## Discipline-tax Strategy

SPINE should reduce discipline tax by making governance **easier to execute explicitly**, especially for agents and tools, while keeping authority, truth, and auditability in the repo.

### Optimize for

- less repeated manual ceremony
- less ambiguity about operating context
- less repeated re-explanation
- easier-to-find governance artifacts
- easier handoff and PR preparation
- clearer CI usage

### Do not optimize for

- hidden state
- silent canonical mutation
- fake automation theater
- invisible scope changes
- replacing human judgment with opaque behavior

### Practical roadmap shape

**In Alpha** — reduce obvious friction:

- targeting
- context visibility
- structured output
- bootstrap clarity
- examples
- artifact discoverability

**In Beta** — make governance mechanics more executable for agents:

- task lanes
- handoff/PR-prep
- draftable records
- preflight/checkpoint flows
- stronger local tool surfaces

**In v1** — stabilize these behaviors so they are predictable, inspectable, and dependable.

---

## Out-of-scope Guardrails

These remain **out of scope** unless a future spec explicitly changes direction:

- dashboard-first control surfaces
- cloud sync / cloud control plane
- remote MCP hosting
- account systems
- billing
- multi-user collaboration
- autonomous multi-agent orchestration
- hidden background governance daemons
- model-required core governance logic
- silent canonical state mutation
- broad platform sprawl disguised as "ergonomics"

> SPINE should reduce friction without reducing visibility.

---

## Immediate Next Priorities

1. Define the first bounded beta implementation slice(s)
2. Open the Beta milestone on GitHub with scoped, workable issues
3. Begin Beta execution — discipline-tax reduction, agent-executable mechanics, handoff primitives

---

## Positioning Summary

SPINE is not trying to become another coding agent or an orchestration platform.

It is trying to become the **trustworthy governance layer above AI coding tools**:

- repo-native
- explicit
- inspectable
- auditable
- sustainable in repeated real use
