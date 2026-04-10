#!/usr/bin/env python3
"""Validate SPINE --json surface shapes captured by run_harness.sh.

Reads the per-step log files from a harness log directory and checks that
the JSON produced by `spine ... --json` commands has the required keys.

This is intentionally narrow: it only asserts contract-level keys so the
harness stays a cheap, deterministic health check — not a schema test.

Exit 0 on all-clear, 1 on any shape violation.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# name_suffix -> set of required keys
REQUIRED_KEYS = {
    "doctor_json": {"passed", "repo", "branch", "issues", "error_count", "warning_count"},
    "mission_show_json": {"id", "title", "status", "allowed_scope", "forbidden_expansions"},
    "before_work_json": {"passed", "checks"},
    "before_pr_json": {"passed", "checks"},
    "before_pr_json_blocked": {"passed", "checks"},
    "drift_scan_json": {"clean", "events", "severity_summary"},
    "drift_scan_dirty_json": {"clean", "events", "severity_summary"},
    "review_weekly_json": set(),  # presence-only; shape not locked yet
}


def _load_json_tail(path: Path) -> dict | None:
    """SPINE prints context lines before the JSON blob on some commands.
    Extract the trailing JSON object from the log file.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    # Find the first '{' that begins a balanced JSON object that reaches EOF
    brace = text.rfind("\n{")
    if brace == -1 and text.lstrip().startswith("{"):
        brace = text.find("{")
    elif brace != -1:
        brace += 1  # skip newline
    if brace == -1:
        return None
    snippet = text[brace:]
    try:
        return json.loads(snippet)
    except json.JSONDecodeError:
        # Try progressively smaller tails — the first '{' may have been inside
        # a context preamble.
        for i, ch in enumerate(text):
            if ch == "{":
                try:
                    return json.loads(text[i:])
                except json.JSONDecodeError:
                    continue
        return None


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: check_json_shapes.py <log_dir>", file=sys.stderr)
        return 2
    log_dir = Path(argv[1])
    if not log_dir.is_dir():
        print(f"log dir not found: {log_dir}", file=sys.stderr)
        return 2

    failures: list[str] = []
    checked = 0

    for log in sorted(log_dir.glob("iter*_*.log")):
        # derive the step name suffix (strip iterN_ prefix, strip .log)
        stem = log.stem
        try:
            _, name = stem.split("_", 1)
        except ValueError:
            continue
        required = REQUIRED_KEYS.get(name)
        if required is None:
            continue

        data = _load_json_tail(log)
        if data is None:
            failures.append(f"{log.name}: no JSON object found")
            continue
        if not isinstance(data, dict):
            failures.append(f"{log.name}: JSON root is not an object")
            continue
        missing = required - set(data.keys())
        if missing:
            failures.append(f"{log.name}: missing keys {sorted(missing)}")
            continue
        checked += 1
        print(f"  [OK] {log.name}: keys {sorted(required)} present")

    print()
    if failures:
        print(f"  {len(failures)} shape failure(s):")
        for f in failures:
            print(f"    - {f}")
        return 1
    print(f"  {checked} JSON surface check(s) passed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
