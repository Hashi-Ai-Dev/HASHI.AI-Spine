# Contributing to SPINE

Thank you for your interest in contributing to SPINE.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/Hashi-Ai-Dev/SPINE.git
cd SPINE

# Install dependencies
uv sync

# Run tests
uv run pytest
```

## Branch Naming

- `stabilization/issueNNN-description` — for bug fixes and stability work
- `feature/description` — for new features

Examples:
- `stabilization/issue42-fix-log-rotation`
- `feature/add-json-output`

## PR Process

1. Fork the repository and create a branch from `main`
2. Make your changes — ensure CI passes
3. Open a PR against `main`
4. In the PR description, explain **what** changed and **why**
5. Link any related issues with `Closes #XX` or `Relates to #XX`

CI must pass before merge. All tests must pass, and the PR description must describe the change.

## Commit Conventions

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation only
- `chore:` — maintenance, dependency updates, tooling
- `test:` — adding or updating tests

Examples:
- `feat: add JSON output format`
- `fix: correct vote tally in plurality method`
- `docs: update README with installation steps`

## What Is In Scope

SPINE is a **governance tool**, not an AI agent. It is a CLI/Python library for running ranked-choice and delegated voting systems.

In scope:
- Voting methods: plurality, approval, STAR, Borda, Condorcet, delegated voting
- CLI entry points for running votes
- Config/file parsing for ballot formats
- Vote aggregation and winner determination
- Tabulation output (text, JSON)
- Tests for vote tabulation logic

## What Is NOT In Scope

- Web UI / frontend
- Cloud hosting or cloud-native deployment
- Authentication or user management
- Persistent web services or APIs
- AI/ML model integration

## Filing Issues

**Before filing a bug report:**

1. Search existing issues — your bug may already be reported
2. Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
3. Include the version (`pyproject.toml` or `uv run python -m spine --version`)

**For feature requests:** open a discussion or issue describing the voting method you'd like to see added and why it fits SPINE's scope.
