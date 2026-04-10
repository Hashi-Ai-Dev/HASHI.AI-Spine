# SPINE Agent Guidance

This repository uses `.spine/` as canonical governance state.

## Rules for all agents

- Read `.spine/mission.yaml` before making non-trivial changes.
- Read `.spine/constraints.yaml` to understand work schedule and budget limits.
- Never silently expand scope beyond `allowed_scope` in `mission.yaml`.
- Never add UI, auth, billing, cloud sync, or autonomous background loops unless
  they appear explicitly in `allowed_scope`.
- After any change session: run `uv run pytest` and fix all failures before finishing.

## Governance workflow (common commands)

```bash
uv run spine mission show            # view active mission
uv run spine doctor                  # validate .spine/ state
uv run spine opportunity score ...   # score a candidate opportunity
uv run spine evidence add ...        # log evidence
uv run spine decision add ...        # record a decision
uv run spine drift scan              # detect scope drift
uv run spine review weekly ...       # generate weekly review
uv run spine brief --target claude   # generate agent brief (or --target codex)
```

## Governance files

| File | Purpose |
|------|---------|
| `.spine/mission.yaml` | Active mission definition |
| `.spine/constraints.yaml` | Work schedule, budget, routing rules |
| `.spine/opportunities.jsonl` | Candidate opportunities log |
| `.spine/evidence.jsonl` | Evidence collected for review |
| `.spine/decisions.jsonl` | Decision record |
| `.spine/drift.jsonl` | Detected scope drift log |
| `.spine/runs.jsonl` | Agent run log |
| `.spine/reviews/` | Weekly review documents |
| `.spine/briefs/` | Agent brief documents |
