# CLAUDE.md — SPINE Governance

## Purpose

This repository uses SPINE for local-first, repo-native mission governance.
`.spine/` is the canonical source of truth for governance state.

## Rules

- Preserve `.spine/` as the canonical source of truth. Never rewrite its files
  silently.
- Read `.spine/mission.yaml` before making non-trivial changes.
- Do not silently expand scope beyond what is defined in `.spine/mission.yaml`.
- Do not add web UI, authentication, billing, or cloud sync unless explicitly
  in scope.
- Run `uv run spine doctor` to verify governance state is valid.
- Run `uv run pytest` before finishing any change session. Fix all failures.

## Governance State — What Is Durable vs Ephemeral

Generated outputs (briefs, reviews) are ephemeral and gitignored. Run `spine brief generate` or `spine review weekly` to produce them. They are not committed to git.

Canonical governance data is in durable JSONL files: decisions, evidence, drift, opportunities. These ARE committed to git and survive across sessions.

## Quick reference

```bash
uv sync                            # install dependencies
uv run spine doctor                # validate .spine/ governance state
uv run spine mission show          # view active mission
uv run spine evidence add ...      # log evidence
uv run spine decision add ...      # record a decision
uv run spine review weekly ...     # generate weekly review
uv run pytest                      # run tests
```
