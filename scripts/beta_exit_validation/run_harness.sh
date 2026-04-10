#!/usr/bin/env bash
# SPINE beta-exit repeated-use proof harness.
#
# Exercises the full governed workflow on an ephemeral sandbox repo across
# multiple iterations (accumulating state), then runs a dedicated
# forbidden-scope probe. Local-first, deterministic, bounded.
#
# See scripts/beta_exit_validation/README.md for the rationale.
#
# Usage:
#   bash scripts/beta_exit_validation/run_harness.sh [--sandbox DIR] [--out FILE]
#
# Exit codes:
#   0  all steps passed
#   1  at least one step failed — sandbox is left on disk for inspection

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPINE_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

SANDBOX=""
OUT_FILE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --sandbox) SANDBOX="$2"; shift 2 ;;
    --out)     OUT_FILE="$2"; shift 2 ;;
    -h|--help) sed -n '1,20p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$SANDBOX" ]]; then
  SANDBOX="$(mktemp -d -t spine_beta_exit.XXXXXX)"
fi
if [[ -z "$OUT_FILE" ]]; then
  OUT_FILE="${SANDBOX}/harness_results.json"
fi

mkdir -p "$SANDBOX"
LOG_DIR="${SANDBOX}/logs"
mkdir -p "$LOG_DIR"
TARGET="${SANDBOX}/target"

declare -a RESULTS_JSON=()
STEP_INDEX=0
FAIL_COUNT=0
TOTAL_COUNT=0

# --- Helpers ------------------------------------------------------------------
json_escape() { python3 -c 'import json,sys; sys.stdout.write(json.dumps(sys.stdin.read()))'; }

record_step() {
  local iter="$1"; local name="$2"; local ec="$3"; local out="$4"; local expect="${5:-0}"
  local status="PASS"
  if [[ "$ec" != "$expect" ]]; then
    status="FAIL"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
  TOTAL_COUNT=$((TOTAL_COUNT + 1))
  STEP_INDEX=$((STEP_INDEX + 1))
  local tail_snippet esc
  tail_snippet="$(tail -c 512 "$out" 2>/dev/null || echo "")"
  esc="$(printf '%s' "$tail_snippet" | json_escape)"
  RESULTS_JSON+=("{\"step\":${STEP_INDEX},\"iter\":\"${iter}\",\"name\":\"${name}\",\"exit\":${ec},\"expected\":${expect},\"status\":\"${status}\",\"tail\":${esc}}")
  printf "  [%s] iter=%s step=%-32s exit=%d (expected %d)\n" \
    "$status" "$iter" "$name" "$ec" "$expect"
}

run_step() {
  local iter="$1"; local name="$2"; local expect="$3"; shift 3
  local out="${LOG_DIR}/iter${iter}_${name}.log"
  "$@" >"$out" 2>&1
  local ec=$?
  record_step "$iter" "$name" "$ec" "$out" "$expect"
}

spine() {
  ( cd "$SPINE_DIR" && uv run spine "$@" )
}

# --- Phase 0: seed sandbox repo ----------------------------------------------
seed_sandbox() {
  rm -rf "$TARGET"
  mkdir -p "$TARGET"
  (
    cd "$TARGET"
    git init -q
    git config user.email "harness@spine.local"
    git config user.name "SPINE Harness"
    # Local-only signing off — scoped to this sandbox repo, matching the
    # SPINE test suite pattern (tests/test_operator_output_modes.py).
    git config commit.gpgsign false
    echo "# harness target" > README.md
    git add README.md
    git commit -qm "init"
  )
}

# --- Phase 1: one-time setup (init + mission) --------------------------------
run_setup() {
  echo ""
  echo "=== Phase: setup (one-time) ==="
  run_step "setup" "init" 0 spine init --cwd "$TARGET"
  run_step "setup" "doctor_json" 0 spine doctor --cwd "$TARGET" --json
  run_step "setup" "mission_set" 0 spine mission set --cwd "$TARGET" \
    --title "Harness mission" \
    --status active \
    --target-user "beta-exit harness" \
    --user-problem "prove repeated governed workflow" \
    --promise "validate the full loop deterministically" \
    --metric-type milestone \
    --metric-value "harness validated" \
    --scope "governance,validation" \
    --forbid "ui,billing"
  run_step "setup" "mission_show_json" 0 spine mission show --cwd "$TARGET" --json
}

# --- Phase 2: iterate the standard working loop ------------------------------
# State accumulates across iterations — evidence and decisions are appended.
run_iteration() {
  local iter="$1"

  echo ""
  echo "=== Phase: iteration ${iter} (standard working loop) ==="

  run_step "$iter" "brief_claude"      0 spine brief --cwd "$TARGET" --target claude
  run_step "$iter" "brief_codex"       0 spine brief --cwd "$TARGET" --target codex
  run_step "$iter" "before_work_json"  0 spine check before-work --cwd "$TARGET" --json

  run_step "$iter" "evidence_add" 0 spine evidence add --cwd "$TARGET" \
    --kind brief_generated \
    --description "harness iter ${iter} brief generated"
  run_step "$iter" "evidence_list" 0 spine evidence list --cwd "$TARGET"

  run_step "$iter" "decision_add" 0 spine decision add --cwd "$TARGET" \
    --title "Harness iter ${iter} decision" \
    --why "exercise decision surface" \
    --decision "recorded deterministic harness decision"
  run_step "$iter" "decision_list" 0 spine decision list --cwd "$TARGET"

  # Simulate in-scope change, stage it so drift scan sees working tree state.
  mkdir -p "${TARGET}/governance"
  echo "iter ${iter}" > "${TARGET}/governance/note_${iter}.md"
  ( cd "$TARGET" && git add -A )

  run_step "$iter" "drift_scan_json" 0 spine drift scan --cwd "$TARGET" --json
  run_step "$iter" "before_pr_json"  0 spine check before-pr --cwd "$TARGET" --json
  run_step "$iter" "review_weekly_json" 0 spine review weekly --cwd "$TARGET" \
    --days 7 --recommendation continue --notes "harness iter ${iter}" --json

  # Commit the in-scope change so the next iteration starts with a clean tree.
  ( cd "$TARGET" && git commit -qm "iter ${iter}: in-scope note" )

  local ev_count dec_count
  ev_count="$(wc -l < "${TARGET}/.spine/evidence.jsonl" 2>/dev/null || echo 0)"
  dec_count="$(wc -l < "${TARGET}/.spine/decisions.jsonl" 2>/dev/null || echo 0)"
  echo "  iter${iter} accumulated: evidence=${ev_count} decisions=${dec_count}"
  RESULTS_JSON+=("{\"step\":0,\"iter\":\"${iter}\",\"name\":\"counts\",\"evidence\":${ev_count},\"decisions\":${dec_count}}")
}

# --- Phase 3: forbidden-scope probe ------------------------------------------
# Introduces a forbidden-scope file, verifies drift scan flags it HIGH,
# verifies before-pr fails. Does NOT try to "clean" the drift log afterward —
# drift.jsonl is intentionally append-only in SPINE's design.
run_forbidden_probe() {
  echo ""
  echo "=== Phase: forbidden-scope probe ==="

  mkdir -p "${TARGET}/ui"
  echo "forbidden" > "${TARGET}/ui/dashboard.tsx"
  ( cd "$TARGET" && git add -A )

  run_step "probe" "drift_scan_dirty_json" 0 spine drift scan --cwd "$TARGET" --json

  if command -v jq >/dev/null 2>&1; then
    local dirty_log="${LOG_DIR}/iterprobe_drift_scan_dirty_json.log"
    local high_count
    high_count="$(jq '.severity_summary.high // 0' "$dirty_log" 2>/dev/null || echo 0)"
    local verify_ec=1
    if [[ "${high_count:-0}" -ge 1 ]]; then verify_ec=0; fi
    record_step "probe" "drift_scan_flags_forbidden" "$verify_ec" "$dirty_log" 0
  fi

  # before-pr should exit 1 because drift is now present.
  run_step "probe" "before_pr_json_blocked" 1 spine check before-pr --cwd "$TARGET" --json

  # Remove the forbidden file (cleanup of the working tree).
  rm -rf "${TARGET}/ui"
  ( cd "$TARGET" && git add -A )
}

# --- Phase 4: state coherence assertion --------------------------------------
# After two iterations, evidence and decisions should have 2 records each
# (at minimum). drift.jsonl should contain the HIGH event logged by the probe.
assert_state_coherence() {
  echo ""
  echo "=== Phase: state coherence assertion ==="
  local ev_count dec_count drift_count fail=0

  ev_count="$(wc -l < "${TARGET}/.spine/evidence.jsonl" 2>/dev/null || echo 0)"
  dec_count="$(wc -l < "${TARGET}/.spine/decisions.jsonl" 2>/dev/null || echo 0)"
  drift_count="$(wc -l < "${TARGET}/.spine/drift.jsonl" 2>/dev/null || echo 0)"

  if [[ "$ev_count" -lt 2 ]]; then
    echo "  [FAIL] evidence accumulation: expected >=2 got ${ev_count}"
    fail=1
  else
    echo "  [PASS] evidence accumulation: ${ev_count} records"
  fi

  if [[ "$dec_count" -lt 2 ]]; then
    echo "  [FAIL] decision accumulation: expected >=2 got ${dec_count}"
    fail=1
  else
    echo "  [PASS] decision accumulation: ${dec_count} records"
  fi

  if [[ "$drift_count" -lt 1 ]]; then
    echo "  [FAIL] drift persistence: expected >=1 got ${drift_count}"
    fail=1
  else
    echo "  [PASS] drift persistence: ${drift_count} records"
  fi

  TOTAL_COUNT=$((TOTAL_COUNT + 1))
  if [[ "$fail" -ne 0 ]]; then
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
  local status="PASS"
  if [[ "$fail" -ne 0 ]]; then status="FAIL"; fi
  RESULTS_JSON+=("{\"step\":0,\"iter\":\"assert\",\"name\":\"state_coherence\",\"evidence\":${ev_count},\"decisions\":${dec_count},\"drift\":${drift_count},\"status\":\"${status}\"}")
}

# --- JSON shape check --------------------------------------------------------
check_json_shapes() {
  echo ""
  echo "=== JSON shape checks ==="
  python3 "${SCRIPT_DIR}/check_json_shapes.py" "${LOG_DIR}"
  local ec=$?
  TOTAL_COUNT=$((TOTAL_COUNT + 1))
  if [[ "$ec" -ne 0 ]]; then
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
  local status="PASS"
  if [[ "$ec" -ne 0 ]]; then status="FAIL"; fi
  RESULTS_JSON+=("{\"step\":0,\"iter\":\"shape\",\"name\":\"json_shape_check\",\"exit\":${ec},\"status\":\"${status}\"}")
}

# --- Write results -----------------------------------------------------------
write_results() {
  local n=${#RESULTS_JSON[@]}
  {
    printf '{\n'
    printf '  "spine_dir": "%s",\n' "$SPINE_DIR"
    printf '  "sandbox": "%s",\n' "$SANDBOX"
    printf '  "total": %d,\n' "$TOTAL_COUNT"
    printf '  "failures": %d,\n' "$FAIL_COUNT"
    printf '  "status": "%s",\n' "$([[ $FAIL_COUNT -eq 0 ]] && echo PASS || echo FAIL)"
    printf '  "records": [\n'
    local i
    for i in "${!RESULTS_JSON[@]}"; do
      if [[ $i -lt $((n - 1)) ]]; then
        printf '    %s,\n' "${RESULTS_JSON[$i]}"
      else
        printf '    %s\n' "${RESULTS_JSON[$i]}"
      fi
    done
    printf '  ]\n'
    printf '}\n'
  } > "$OUT_FILE"
}

# --- Main --------------------------------------------------------------------
echo "SPINE beta-exit repeated-use proof harness"
echo "  spine dir : ${SPINE_DIR}"
echo "  sandbox   : ${SANDBOX}"
echo "  out file  : ${OUT_FILE}"

seed_sandbox
run_setup
run_iteration 1
run_iteration 2
run_forbidden_probe
assert_state_coherence
check_json_shapes
write_results

echo ""
echo "=== Summary ==="
echo "  total steps : ${TOTAL_COUNT}"
echo "  failures    : ${FAIL_COUNT}"
echo "  results     : ${OUT_FILE}"
if [[ $FAIL_COUNT -eq 0 ]]; then
  echo "  status      : PASS"
  exit 0
else
  echo "  status      : FAIL"
  exit 1
fi
