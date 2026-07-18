"""HPP W1 — Progress Watchdog: stale-heartbeat supervision.

Scans progress snapshots and escalates liveness failures:
  age > 2 x heartbeat_interval  -> status WARNING + progress.warning(STALE_HEARTBEAT)
  age > 5 x heartbeat_interval  -> status BLOCKED + progress.blocked(HEARTBEAT_LOST)

The watchdog is a SUPERVISOR: it mutates snapshots directly (the owning
process may be dead, so tracker lifecycle guards do not apply to it).
Driven externally (production-monitor.sh or a timer); not a daemon.
"""

import json
import os
import time

from telemetry.progress_tracker import (  # type: ignore
    PROGRESS_DIR, EVENTS_DIR, TERMINAL_STATUSES,
    _append_event, _iso, _parse_iso,
)

WARN_FACTOR = 2
BLOCK_FACTOR = 5


def scan(store_dir=None, events_dir=None, now=None):
    """Check every non-terminal snapshot; escalate stale ones.

    Returns a summary: {"checked": N, "healthy": N, "warned": [...], "blocked": [...]}
    """
    store = store_dir or PROGRESS_DIR
    events = events_dir or EVENTS_DIR
    now = now if now is not None else time.time()
    summary = {"checked": 0, "healthy": 0, "warned": [], "blocked": []}
    if not os.path.isdir(store):
        return summary

    for fname in sorted(os.listdir(store)):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(store, fname)
        try:
            with open(path) as f:
                snap = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        if snap.get("status") in TERMINAL_STATUSES:
            continue
        summary["checked"] += 1
        interval = int(snap.get("heartbeat_interval_s") or 60)
        try:
            age = now - _parse_iso(snap["last_heartbeat"])
        except (KeyError, ValueError):
            age = float("inf")

        if age > BLOCK_FACTOR * interval:
            snap["status"] = "BLOCKED"
            snap["current_operation"] = (
                f"BLOCKED: heartbeat lost ({int(age)}s > {BLOCK_FACTOR}x{interval}s)")
            _write(path, snap)
            _append_event(_event(snap, "progress.blocked",
                                 reason="HEARTBEAT_LOST", age_s=int(age)), events)
            summary["blocked"].append(snap["execution_id"])
        elif age > WARN_FACTOR * interval:
            if snap.get("status") != "WARNING":
                snap["status"] = "WARNING"
                snap.setdefault("warnings", []).append(
                    {"at": _iso(), "code": "STALE_HEARTBEAT",
                     "detail": f"no heartbeat for {int(age)}s (interval {interval}s)"})
                _write(path, snap)
                _append_event(_event(snap, "progress.warning",
                                     code="STALE_HEARTBEAT", age_s=int(age)), events)
            summary["warned"].append(snap["execution_id"])
        else:
            summary["healthy"] += 1
    return summary


def _write(path, snap):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(snap, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def _event(snap, event_type, **extra):
    ev = {
        "event_type": event_type,
        "execution_id": snap.get("execution_id"),
        "skill_id": snap.get("skill_id", ""),
        "namespace": snap.get("namespace", ""),
        "task_kind": snap.get("task_kind"),
        "phase": snap.get("phase"),
        "stage": snap.get("stage"),
        "status": snap.get("status"),
        "progress_pct": snap.get("progress_pct"),
        "current_operation": snap.get("current_operation"),
        "speed": snap.get("speed"),
        "eta": snap.get("eta"),
        "last_heartbeat": snap.get("last_heartbeat"),
        "timestamp": _iso(),
        "emitted_by": "progress_watchdog",
        "body_truncated": True,
    }
    ev.update(extra)
    return ev


if __name__ == "__main__":
    print(json.dumps(scan(), ensure_ascii=False, indent=2))
