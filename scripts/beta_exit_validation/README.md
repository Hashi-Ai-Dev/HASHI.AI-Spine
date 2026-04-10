# SPINE Beta-Exit Validation Harness

This directory holds the bounded, repeatable validation harness used to
produce the beta-exit proof artifact at
[`docs/SPINE_BETA_EXIT_VALIDATION.md`](../../docs/SPINE_BETA_EXIT_VALIDATION.md).

It exists to answer one question:

> **Is the full SPINE governed workflow coherent, inspectable, and repeatable
> in practice — not just on a single happy-path demo?**

## Files

| File | Purpose |
|------|---------|
| `run_harness.sh` | Main bash entry point. Creates an ephemeral sandbox repo, runs the full governed workflow twice, verifies JSON surface shapes, writes a JSON results file, and exits non-zero on any failure. |
| `check_json_shapes.py` | Narrow JSON-shape checker. Asserts contract-level required keys on `--json` outputs captured by the harness. |
| `README.md` | This file. |

## What it does

For each iteration (the harness runs two iterations), the sandbox exercises:

1. `spine init` (force-overwrite on repeat iterations)
2. `spine doctor --json`
3. `spine mission set` (bounds scope explicitly with `--scope` and `--forbid`)
4. `spine mission show --json`
5. `spine brief --target claude`
6. `spine brief --target codex`
7. `spine check before-work --json`
8. `spine evidence add`
9. `spine evidence list`
10. `spine decision add`
11. `spine decision list`
12. Simulate an in-scope change → `spine drift scan --json` (should be clean)
13. Simulate an out-of-scope change in `ui/` → `spine drift scan --json` (should flag HIGH)
14. `spine check before-pr --json` (should exit 1 because drift is present)
15. Clean the forbidden file → `spine check before-pr --json` (should now pass)
16. `spine review weekly --json`
17. `spine doctor --json` (round-trip sanity)

After both iterations, a narrow JSON shape check verifies that
`--json` surfaces contain the expected contract keys
(see `check_json_shapes.py` for the exact list).

## Design constraints

- **Local-first.** No network. No daemons. No external services.
- **Deterministic.** Sandbox is a fresh `mktemp -d` on every run. No shared
  state between runs.
- **Inspectable.** Per-step stdout/stderr is captured under
  `<sandbox>/logs/iterN_<step>.log`. A JSON results blob is written to
  `<sandbox>/harness_results.json`.
- **Bounded.** The harness is a single shell script and a narrow Python
  helper. No framework. No config. No test runner layer.
- **Non-destructive.** The sandbox is scoped to `mktemp -d` and the real
  SPINE repo is never mutated by the harness.
- **Signing-aware.** The sandbox repo sets `commit.gpgsign=false` **locally**
  inside the sandbox only (same pattern the SPINE test suite uses in
  `tests/test_operator_output_modes.py`). The real SPINE repo's git config
  is not touched.

## Usage

```bash
# Default: sandbox is mktemp'd under /tmp, results left on disk for inspection
bash scripts/beta_exit_validation/run_harness.sh

# Explicit sandbox location
bash scripts/beta_exit_validation/run_harness.sh --sandbox /tmp/my-harness

# Explicit results file
bash scripts/beta_exit_validation/run_harness.sh \
  --sandbox /tmp/my-harness \
  --out /tmp/my-harness/results.json
```

Exit 0 means all iterations and shape checks passed. Exit 1 means at least
one step failed; the sandbox is left on disk so the per-step logs can be
inspected.

## What this harness is NOT

- **Not a test replacement.** The normal pytest suite (`uv run pytest`,
  currently 544 passing) remains the primary correctness gate.
- **Not a benchmark.** It does not measure latency or stress behavior.
- **Not a CI runner.** It is deliberately a single shell script so any
  operator can re-run it locally by hand.
- **Not a linter.** It exercises the CLI as an operator would; it does not
  read SPINE's source code.

## Why this harness exists

Issue #51 is the beta-exit repeated-use proof pass. The existing pytest
suite proves the *units* work. The harness proves the *workflow* works —
end-to-end, twice, with all JSON surfaces, on a throwaway target repo — so
the beta-exit judgment is grounded in actually-run evidence instead of
docs-only claims.
