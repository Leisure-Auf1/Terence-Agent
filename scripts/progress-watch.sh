#!/usr/bin/env bash
# HPP W2 — progress-watch.sh: generic sampling wrapper for black-box long tasks.
#
# Turns any observable numeric probe into live HPP telemetry
# (snapshot + progress.* events) without touching the watched tool.
#
# Usage:
#   bash scripts/progress-watch.sh \
#     --id exec-123 --kind docker_build --phase "Phase 4 build" \
#     --probe 'docker exec CID du -sm /tmp | cut -f1' \
#     --total 380 --unit MB [--interval 30] [--watch-pid 12345] [--stage pip]
#
# Probe contract: prints ONE number (progress units done). Non-numeric or
# failing probe output => heartbeat-only tick (liveness still reported).
# Exit: when --watch-pid dies (task over) the watcher emits a final
# heartbeat and exits 0 — terminal status (complete/block) belongs to the
# task owner, or to the watchdog if the owner vanished.
#
# ── Probe templates ──────────────────────────────────────────────
# docker_build : docker exec <CID> du -sm /tmp | cut -f1          (MB downloaded)
#                (post-download: du -sm /root/.local for install phase)
# pytest       : grep -c PASSED <logfile>                          (tests done; --total=N)
# migration    : cat <state-dir>/waves-done.count                  (waves done)
# download     : stat -c %s <file> (bytes)  or du -sm <dir> (MB)
# ─────────────────────────────────────────────────────────────────
set -uo pipefail

KERNEL="$HOME/.hermes/kernel"
CLI="$KERNEL/telemetry/progress_cli.py"
PY="${PY:-/usr/bin/python}"

ID="" KIND="generic" PHASE="long task" PROBE="" TOTAL="" UNIT="" INTERVAL=30
WATCH_PID="" STAGE="" SKILL="" NS=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --id) ID="$2"; shift 2;;
    --kind) KIND="$2"; shift 2;;
    --phase) PHASE="$2"; shift 2;;
    --probe) PROBE="$2"; shift 2;;
    --total) TOTAL="$2"; shift 2;;
    --unit) UNIT="$2"; shift 2;;
    --interval) INTERVAL="$2"; shift 2;;
    --watch-pid) WATCH_PID="$2"; shift 2;;
    --stage) STAGE="$2"; shift 2;;
    --skill) SKILL="$2"; shift 2;;
    --namespace) NS="$2"; shift 2;;
    *) echo "unknown arg: $1" >&2; exit 1;;
  esac
done

[[ -z "$ID" || -z "$PROBE" ]] && { echo "usage: --id ID --probe 'CMD' required" >&2; exit 1; }

# Register if no snapshot yet (idempotent attach)
if ! "$PY" "$CLI" snapshot --id "$ID" 2>/dev/null | grep -q '"execution_id"'; then
  START_ARGS=(start --id "$ID" --kind "$KIND" --phase "$PHASE" --interval "$INTERVAL")
  [[ -n "$TOTAL" ]] && START_ARGS+=(--total "$TOTAL")
  [[ -n "$UNIT"  ]] && START_ARGS+=(--unit "$UNIT")
  [[ -n "$SKILL" ]] && START_ARGS+=(--skill "$SKILL")
  [[ -n "$NS"    ]] && START_ARGS+=(--namespace "$NS")
  "$PY" "$CLI" "${START_ARGS[@]}" >/dev/null
fi

echo "progress-watch: id=$ID kind=$KIND interval=${INTERVAL}s probe=[$PROBE]"

while :; do
  if [[ -n "$WATCH_PID" ]] && ! kill -0 "$WATCH_PID" 2>/dev/null; then
    "$PY" "$CLI" heartbeat --id "$ID" --op "watched pid $WATCH_PID exited; watcher detaching" >/dev/null 2>&1
    echo "progress-watch: pid $WATCH_PID gone — exiting"
    exit 0
  fi
  VAL="$(bash -c "$PROBE" 2>/dev/null | tr -dc '0-9.\n' | head -1)"
  ARGS=(update --id "$ID")
  [[ -n "$STAGE" ]] && ARGS+=(--stage "$STAGE")
  if [[ -n "$VAL" ]]; then
    ARGS+=(--done "$VAL" --op "probe=$VAL ${UNIT:-units}")
  else
    ARGS=(heartbeat --id "$ID" --op "probe unreadable (task may be between phases)")
  fi
  "$PY" "$CLI" "${ARGS[@]}" >/dev/null 2>&1 || true
  sleep "$INTERVAL"
done
