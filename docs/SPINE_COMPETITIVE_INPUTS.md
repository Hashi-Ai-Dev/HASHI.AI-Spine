# SPINE Competitive Inputs

> Product and design inputs from external project review. Preserved for planning, not activated as scope.
> Source: review of `ultraworkers/claw-code` and `Yeachan-Heo/oh-my-claudecode` (2026-04-08).
> Reviewer: Hashi.

---

## Core Interpretation Rule

> **SPINE should borrow workflow discipline, explicit contracts, and trust-preserving ergonomics — not orchestration spectacle, hidden automation, or platform sprawl.**

> **SPINE should become more useful by making governance explicit, stable, agent-executable, inspectable, and lightweight enough to repeat.**

---

## Strong Fits

These align with SPINE's identity and existing Beta direction. They reinforce — not expand — what SPINE is already doing.

### Doctor-first / preflight culture
SPINE's `spine doctor` is the preflight check. The instinct from external projects — check health before doing work — is already embodied in SPINE. Keep it prominent. The Beta `spine check before-pr` (Issue #31) is this direction.

### Deterministic machine-readable command contracts
Stable exit codes, `--json` output, deterministic behavior. These projects reinforce that agent-executable governance needs stable contracts. SPINE's Phase 3A work here was correct. Continue prioritizing this in Beta.

### Clear runtime / docs / surface map
Clean separation between what the tool does, what it outputs, and what the human needs to know. SPINE's docs hierarchy (README → external-repo-onboarding → SPEC) is already moving this direction. Keep docs clarity as a discipline.

### Handoff / PR-prep summary primitives
Generative handoff context that the next agent or reviewer can use without reading raw state. Already in Beta queue as Issue #32. These inputs strengthen the case for it.

### Mission interview / mission refinement as draft generation only
Draft mission generation — operator refines, confirms, it becomes canonical. Strong fit. Do NOT build mission generation that silently overwrites canonical truth. Already preserved in product direction.

### Deterministic validation harnesses
Structured gate checks that produce consistent results. SPINE's alpha-exit validation gate matrix (Issue #25) was this. Keep the validation-first mindset for Beta milestones too.

---

## Useful Later — But Constrained

Good ideas that fit SPINE's identity but belong after the current Beta queue or with strict boundaries.

### Local opt-in hooks
`spine hooks install` — already in Beta as Issue #34. Keep it bounded to pre-PR, opt-in, visible, removable. Not a background daemon. Good constrained fit.

### Narrow reusable governance patterns / recipes
Reusable templates for common governance scenarios (e.g., "govern this type of PR"). Phase 3B+. Keep it narrow — not a marketplace, not a library. Just a small set of operator-defined patterns.

### Explicit config / path resolution clarity
`SPINE_ROOT`, `--cwd`, and how they interact needs to be crystal clear. Not a new feature — hygiene. Worth documenting more explicitly in the spec and onboarding.

---

## Likely Drift / Not For Now

These ideas push SPINE away from its identity. Flag and reject.

### HUD / live observability
Dashboard-style live monitoring of governance state. Easy to drift into product scope that SPINE is not. The value is in governance, not observability. Reject unless a specific bounded use case emerges.

### Notifications / webhooks / remote alerts
A governance tool that pings you about things is no longer purely local. "Zero notification" is part of SPINE's identity. Not for now.

### Team orchestration / tmux worker runtime / autopilot surfaces
SPINE governs a single agent. Multi-agent coordination is a different product. Reject.

### "Zero learning curve / everything automatic"
Automatic mission generation, automatic governance without operator input — this destroys the trust model. SPINE's operator must always be in the loop. Reject.

---

## Connection to Current Beta Queue

| External input | SPINE connection |
|---|---|
| Preflight / doctor-first | Issue #31 — `spine check before-pr` |
| Handoff / PR-prep summaries | Issue #32 — handoff primitive |
| Draft mission generation | Issue #33 — draftable records (partial) |
| Local opt-in hooks | Issue #34 — hook integration |
| Machine-readable contracts | Reinforced by Issues #31–#34 |

---

## Anti-Drift Rules

These inputs were evaluated against SPINE's identity:

**What they confirm SPINE should NOT become:**
- A live dashboard or monitoring tool
- A notification or alert system
- A team collaboration platform
- An "auto-governing" agent with no operator review
- A platform with plugins, marketplace, or extension ecosystem

**What they confirm SPINE should be:**
- Local, repo-native, explicit
- Governed by stable command contracts
- Operator-controlled with clear authority boundaries
- Lightweight enough to sustain repeated use without friction
- Agent-executable without being agent-authoritative

---

*Preserved for Beta planning and future Phase 3B reference. Not active scope.*
