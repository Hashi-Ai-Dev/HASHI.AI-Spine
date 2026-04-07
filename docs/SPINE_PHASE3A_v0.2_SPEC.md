# SPINE Phase 3A Specification v0.2

## Portability + Operator Polish

**Status:** In progress. Implementation queue: issues #15–#18, #23–#25.  
**Implementation state:** Issues #15, #16, #17, #18, and #23 (artifact ergonomics contract) **complete** (2026-04-07). Alpha-exit items #24, #25 are next.  
**Next required step:** Alpha-exit items #24 (external-repo docs), #25 (validation gate matrix).

---

## 1) Why Phase 3A Exists

SPINE v0.1 established and validated the core governance loop: mission control, bounded scope, opportunity scoring, brief generation, evidence and decision logging, drift scanning, and weekly review. Internal use and self-dogfooding confirmed this loop is real and useful.

v0.1.2 stabilization is now complete (CI, `--cwd` support, security settings, onboarding polish). SPINE is in public alpha with 136+ passing tests and branch protection active.

However, Phase 1–2 success does not yet guarantee smooth adoption on arbitrary repositories. Practical operator friction remains: repo targeting ambiguity, branch context confusion, output ergonomics, and artifact discoverability. There is also a meaningful **discipline tax** — the accumulated effort cost of sustained governance use — that must be reduced before the product earns repeat adoption.

Phase 3A exists to solve those practical portability and operations gaps **before** any higher-surface expansion. This keeps SPINE aligned with its product thesis: governance reliability first, novelty later.

This phase is intentionally positioned before dashboard/cloud/swarm directions to avoid repeating the same scope drift SPINE is designed to prevent.

---

## 2) Goals

Phase 3A goals are narrow and operational:

1. **Make SPINE portable across arbitrary repos** with explicit, predictable targeting semantics.
2. **Reduce git-context ambiguity** by making active repo and branch context visible and reliable.
3. **Increase operator confidence** through clear run-time context and deterministic command behavior.
4. **Improve CI/automation friendliness** with machine-readable output and stable exit behavior where appropriate.
5. **Tighten artifact ergonomics** with stable naming and path conventions that simplify inspection and automation.
6. **Improve bootstrap clarity** for first use in non-SPINE repos.
7. **Publish practical docs/examples** for adoption outside SPINE’s own repository.

---

## 3) Non-Goals

Phase 3A explicitly excludes:

- Dashboards, web UIs, or TUI visualization layers
- Remote MCP transport/hosting
- Hosted/cloud sync features
- Authentication, billing, or account systems
- Multi-user collaboration features
- Autonomous orchestration/background agent loops
- Broad adapter expansion or plugin matrix growth
- Model-based scoring, model-based drift classification, or required live-model dependencies
- Any Phase 4/5 roadmap work presented as active scope

---

## 4) Discipline Tax Lens

**Discipline tax** is the accumulated effort cost that makes governance harder to sustain over time. SPINE only has value if operators actually continue using it. Phase 3A must treat discipline tax reduction as a major design lens alongside portability.

This means:

- **Reduce mandatory ceremony** — every governance step that requires unnecessary friction is a step operators will eventually skip.
- **Improve default flows** — the shortest reasonable path to a correct governance action should be clear and immediate.
- **Preserve auditability** — reducing tax does not mean hiding state or papering over governance gaps. The `.spine/` files remain canonical, readable, and version-controlled.
- **No fake automation theater** — do not invent magic workflows that appear to reduce tax but actually obscure what is happening. Operators need to trust the tool, not be surprised by it.
- **Smooth the rough edges** — error messages, context reporting, and bootstrap guidance are all discipline tax vectors. Clear output reduces the cognitive overhead of sustained use.

Phase 3A scope items in sections 5.1–5.6 should each be evaluated against this lens: does it reduce or eliminate a real discipline tax friction point without creating new opacity?

---

## 5) Proposed Scope

### 5.1 Explicit repo targeting

**Why it matters**  
Ambiguous working-directory behavior undermines trust and causes accidental writes to the wrong repo.

**Problem solved**  
Operators and CI need to intentionally direct SPINE at a specific repository path every time semantics matter.

**Narrow acceptable implementation shape**  
- Introduce and standardize explicit repo-targeting semantics (e.g., canonical path flag behavior) across Phase 3A-touched commands.
- Normalize and display resolved target path during execution.
- Fail fast with clear errors for invalid or non-repo targets when command requires git context.

**Standardized contract (implemented in Issue #15)**  
Target resolution precedence: `--cwd` > `SPINE_ROOT` > current working directory.  
Errors state the resolved target, its source, and the corrective action.  
`--cwd` help text on all commands now documents the precedence explicitly.

**Deferred**  
- Repo discovery “magic” across arbitrary parent directories.
- Multi-repo orchestration from one command invocation.

### 5.2 Repo context and default-branch visibility

**Why it matters**  
Drift and review trust depend on operators knowing exactly which branch and comparison base are active.

**Problem solved**  
Implicit default-branch inference is useful but opaque without explicit reporting.

**Narrow acceptable implementation shape**  
- Standard context reporting format for relevant commands: target repo path, current HEAD branch/detached state, resolved default branch or explicit compare target.
- Clear warning path when default branch cannot be resolved.
- Keep behavior deterministic; prioritize transparent reporting over smart heuristics.

**Deferred**  
- Automatic branch remediation or branch-switching flows.
- Advanced branch graph analytics.

### 5.3 Operator/CI output modes (`--json`, `--quiet`, stable exits)

**Why it matters**  
Human-readable output is not sufficient for CI and scripts.

**Problem solved**  
Operators need parseable output and predictable exit codes.

**Narrow acceptable implementation shape**  
- Add machine-readable output mode where operationally justified.
- Add reduced-noise output mode for healthy-path checks.
- Define and document stable exit behavior for success, validation failures, and runtime/context failures.
- Preserve deterministic semantics and backward-safe defaults.

**Deferred**  
- Event streaming, remote telemetry, or observability platforms.
- Complex output formatting families beyond practical operator use.

### 5.4 Artifact naming and path conventions

**Why it matters**  
Timestamp-only naming is difficult for quick navigation and scripting.

**Problem solved**  
Operators need both stable references and historical records.

**Narrow acceptable implementation shape**  
- Define canonical stable artifact aliases (for “current” assets) alongside history retention.
- Standardize naming pattern(s) and directory layout expectations in docs.
- Keep compatibility with existing artifact history where possible.

**Deferred**  
- Large artifact indexing systems.
- Database-backed artifact catalogs.

### 5.5 Bootstrap/install polish

**Why it matters**  
First-run experience determines adoption in non-SPINE repos.

**Problem solved**  
Initial setup should clearly communicate prerequisites, side effects, and resulting repo contract.

**Narrow acceptable implementation shape**  
- Improve bootstrap/install messaging and guidance for zero-context operators.
- Clarify expected files, minimal workflow, and verification steps.
- Keep install/bootstrap local-first and deterministic.

**Deferred**  
- Hosted installers, managed agents, or background services.

### 5.6 Docs and examples for external repo usage

**Why it matters**  
v0.1 documents SPINE itself well, but operators need direct examples for adopting SPINE in unrelated repos.

**Problem solved**  
Reduce onboarding ambiguity and prevent misuse.

**Narrow acceptable implementation shape**  
- Add concise operator-grade examples for new/adopted repo flow.
- Document explicit targeting patterns, branch context interpretation, and CI usage patterns.
- Include anti-patterns and failure-mode examples.

**Deferred**  
- Broad cookbook ecosystems.
- Framework-specific integration matrices.

---

## 6) Risks and Anti-Drift Notes

Phase 3A drift risks and required guardrails:

1. **Overbuilding operator UX**  
   Risk: adding complex presentation layers instead of reliability improvements.  
   Guardrail: prioritize explicit context and deterministic behavior over interface novelty.

2. **Dashboard creep**  
   Risk: introducing UI ambitions under the label of “visibility.”  
   Guardrail: retain CLI + file-native governance as the core control surface.

3. **Magical targeting**  
   Risk: clever repo detection that surprises operators.  
   Guardrail: explicit target resolution and clear reporting; avoid hidden fallbacks.

4. **Surface growth before hygiene**  
   Risk: adding new capability area before portability and release ergonomics are stable.  
   Guardrail: phase gate requires operator-grade stability outcomes first.

5. **Implicit Phase 4 pull-forward**  
   Risk: “small” additions that become cloud/auth/collaboration foundations.  
   Guardrail: enforce Non-Goals as hard exclusions for Phase 3A.

---

## 7) Acceptance Criteria

Phase 3A is successful only if all of the following are true:

1. **Explicit external repo targeting is operationally clear** and materially less ambiguous than v0.1 behavior.
2. **Operators can always tell active context** (repo path, current branch state, comparison/default branch for relevant commands).
3. **Machine-readable output is available where justified** and documented for CI use.
4. **Exit behavior is stable and documented** for normal, validation, and context failures.
5. **Artifact references become easier to inspect and automate** via stable naming/path conventions.
6. **Bootstrap/install guidance is clearer for non-SPINE repos** with practical first-run expectations.
7. **Documentation includes concrete external-repo examples** and anti-pattern warnings.
8. **No prohibited surface expansion occurred** (dashboard/cloud/auth/billing/autonomous/multi-user/model-required scope).

---

## 8) Milestone Breakdown (Planning Sequence)

### Phase 3A.1 — Spec normalization + explicit targeting design ✅ In progress
- Normalize Phase 3A planning spec and align all docs to current reality. (This pass — Issue #10.)
- Finalize Phase 3A boundaries and command-level targeting contract.
- Define context-reporting contract fields and error semantics.
- Lock non-goals and drift guardrails.

### Phase 3A.2 — Repo-context clarity
- Implement and validate consistent repo/branch/default-branch visibility on relevant commands.
- Ensure deterministic handling of unresolved default branch states.

### Phase 3A.3 — Operator/CI output polish
- Add machine-readable and quiet output modes where justified.
- Publish stable exit-code behavior and update operator docs.
- Validate scripting reliability in representative local/CI scenarios.

### Phase 3A.4 — Artifact + docs completion
- Finalize stable artifact naming/path conventions.
- Publish external-repo onboarding and usage examples.
- Run final portability validation pass before Phase 3A closeout.

---

## 9) Recommended First Slice (when implementation is approved)

**Recommended first implementation slice:**  
**Explicit repo targeting + clear repo/branch/default-branch context reporting.**

**Why first:**
- Highest risk-reduction per unit effort.
- Directly addresses correctness and operator trust issues identified in dogfooding.
- Creates the foundation required for meaningful `--json`, CI integration, and artifact ergonomics.
- Prevents follow-on work from inheriting ambiguous targeting behavior.

This first slice should remain narrow: no new product surfaces, no remote capabilities, and no speculative architecture.

---

## 10) Relation to Current State

This Phase 3A planning spec reflects the state of SPINE as of v0.1.2 stabilization (2026-04-07):

- **SPINE Official Spec v0.1** (normalized 2026-04-07): establishes the core governance contract. Phase 1 + 2 are complete. Phase 3A is the next planned phase.
- **SPINE v0.1.2 Stabilization Report**: confirms all stabilization items done — CI, `--cwd` support, security settings, onboarding polish, 136+ tests passing.
- **SPINE v0.1.1 Self-Dogfood Cleanup and External Validation**: surface practical operator friction (targeting ambiguity, branch context confusion, output ergonomics) that directly motivates Phase 3A portability/polish scope.
- **SPINE Roadmap and Backlog** (aligned 2026-04-07): `v0.2 / Phase 3A` is the explicit next active planning phase.

---

## 11) Planning Status Note

Phase 3A is **approved for implementation** (2026-04-07). Implementation queue is live.  
The planning spec normalization pass (Issue #10) is complete as of 2026-04-07.  
Implementation may proceed issue by issue — see issues #15–#18.
