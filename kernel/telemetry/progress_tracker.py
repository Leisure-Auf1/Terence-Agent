"""HPP W1 — Execution Progress Tracker (capability: hermes.core.telemetry.progress).

Solves the black-box execution problem: long-running tasks (docker build,
test suites, deployments, migrations) emit live progress telemetry instead
of a single post-hoc ExecutionRecord.

Design contract (HPP v0.1, Human-Gate approved 2026-07-18):
- Snapshot (atomic overwrite): ~/.hermes/runtime/telemetry/progress/<execution_id>.json
- Events (append-only JSONL):  ~/.hermes/runtime/telemetry/progress-events/YYYY-MM-DD.jsonl
- Event types: progress.started / progress.updated / progress.warning /
               progress.completed / progress.blocked
- Lifecycle validation: started -> updated* -> terminal(COMPLETED|FAILED|BLOCKED)
  Violations raise ProgressLifecycleError.

Compatibility notes:
- progress events live in a SEPARATE stream (progress-events/), never in
  telemetry/events/, so metrics_aggregator success-rate statistics and the
  daily integrity checks are untouched.
- No PII / task content is stored: metrics only (mirrors collector.py's
  body_truncated policy).
"""

import json
import os
import time

PROGRESS_DIR = os.path.expanduser("~/.hermes/runtime/telemetry/progress")
EVENTS_DIR = os.path.expanduser("~/.hermes/runtime/telemetry/progress-events")

TERMINAL_STATUSES = {"COMPLETED", "FAILED", "BLOCKED"}
VALID_STATUSES = {"PENDING", "RUNNING", "WARNING"} | TERMINAL_STATUSES
EVENT_TYPES = {
    "progress.started", "progress.updated", "progress.warning",
    "progress.completed", "progress.blocked",
}
MAX_SPEED_SAMPLES = 10
DEFAULT_HEARTBEAT_INTERVAL_S = 60
LONG_TASK_THRESHOLD_S = 300  # >5 min => heartbeat expected (HPP default rule)

# W3 read-side defaults for skill registry `observability` field
DEFAULT_OBSERVABILITY = {"heartbeat": "auto", "progress": False, "eta": False}


class ProgressLifecycleError(Exception):
    """Raised on invalid lifecycle transitions (start twice, update before
    start, any emission after a terminal event, ...)."""


def _iso(ts=None):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))


def _parse_iso(s):
    return time.mktime(time.strptime(s, "%Y-%m-%dT%H:%M:%SZ")) - time.timezone


def get_observability(skill_entry: dict) -> dict:
    """W3 read-side helper: return observability config with defaults.

    Registry schema v1.2 adds an OPTIONAL `observability` field; the 149
    existing entries omit it, so every consumer must go through this helper.
    """
    obs = dict(DEFAULT_OBSERVABILITY)
    declared = skill_entry.get("observability")
    if isinstance(declared, dict):
        for k in ("heartbeat", "progress", "eta"):
            if k in declared:
                obs[k] = declared[k]
    return obs


def _append_event(event: dict, events_dir: str) -> dict:
    """Append-only JSONL, one file per day (same pattern as event_store.py,
    separate stream for compatibility)."""
    os.makedirs(events_dir, exist_ok=True)
    event["_written_at"] = _iso()
    fname = os.path.join(events_dir, f"{time.strftime('%Y-%m-%d')}.jsonl")
    with open(fname, "a") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    return {"stored": True, "file": fname}


class ProgressTracker:
    """Per-execution progress emitter with strict lifecycle validation."""

    def __init__(self, execution_id, task_kind, phase, skill_id="",
                 namespace="", heartbeat_interval_s=DEFAULT_HEARTBEAT_INTERVAL_S,
                 store_dir=None, events_dir=None):
        if not execution_id:
            raise ValueError("execution_id is required")
        self.execution_id = str(execution_id)
        self.task_kind = task_kind
        self.phase = phase
        self.skill_id = skill_id
        self.namespace = namespace
        self.heartbeat_interval_s = int(heartbeat_interval_s)
        self.store_dir = store_dir or PROGRESS_DIR
        self.events_dir = events_dir or EVENTS_DIR
        self._snapshot = None  # dict once started

    # ── lifecycle guards ────────────────────────────────
    def _require_started(self, action):
        if self._snapshot is None:
            raise ProgressLifecycleError(
                f"{action} before start() — lifecycle is started -> updated* -> terminal")

    def _require_not_terminal(self, action):
        if self._snapshot and self._snapshot["status"] in TERMINAL_STATUSES:
            raise ProgressLifecycleError(
                f"{action} after terminal status {self._snapshot['status']}")

    # ── lifecycle API ───────────────────────────────────
    def start(self, total=None, unit="", stages=None, op="registered"):
        if self._snapshot is not None:
            raise ProgressLifecycleError("start() called twice for the same execution_id")
        now = time.time()
        self._snapshot = {
            "execution_id": self.execution_id,
            "skill_id": self.skill_id,
            "namespace": self.namespace,
            "task_kind": self.task_kind,
            "phase": self.phase,
            "stage": (stages[0] if stages else ""),
            "status": "RUNNING",
            "progress_pct": 0.0 if total else None,
            "progress_basis": unit or None,
            "current_operation": op,
            "speed": None,
            "eta": None,
            "started_at": _iso(now),
            "last_heartbeat": _iso(now),
            "heartbeat_interval_s": self.heartbeat_interval_s,
            "warnings": [],
            "meta": {
                "total": total, "unit": unit, "stages": stages or [],
                "samples": [[round(now, 2), 0.0]],
            },
        }
        self._write_snapshot()
        self._emit("progress.started")
        return dict(self._snapshot)

    def update(self, stage=None, done=None, op=None, pct=None):
        self._require_started("update()")
        self._require_not_terminal("update()")
        now = time.time()
        snap = self._snapshot
        assert snap is not None  # guaranteed by _require_started
        if stage is not None:
            snap["stage"] = stage
        if op is not None:
            snap["current_operation"] = op
        total = snap["meta"].get("total")
        if done is not None:
            samples = snap["meta"]["samples"]
            samples.append([round(now, 2), float(done)])
            del samples[:-MAX_SPEED_SAMPLES]
            speed = self._compute_speed(samples)
            snap["speed"] = speed
            if total:
                snap["progress_pct"] = round(min(100.0, 100.0 * float(done) / total), 1)
                if speed and speed["value"] > 0:
                    remaining = max(0.0, total - float(done))
                    eta_s = int(remaining / speed["value"] * 60) if speed["unit"].endswith("/min") else None
                    conf = "high" if len(samples) >= 6 else ("medium" if len(samples) >= 3 else "low")
                    snap["eta"] = {"seconds": eta_s, "confidence": conf}
        if pct is not None:
            snap["progress_pct"] = round(float(pct), 1)
        # recovering from WARNING on a fresh heartbeat
        if snap["status"] == "WARNING":
            snap["status"] = "RUNNING"
        snap["last_heartbeat"] = _iso(now)
        self._write_snapshot()
        self._emit("progress.updated")
        return dict(snap)

    def heartbeat(self, op=None):
        """Liveness-only update (no progress movement)."""
        return self.update(op=op)

    def warning(self, code, detail=""):
        self._require_started("warning()")
        self._require_not_terminal("warning()")
        snap = self._snapshot
        assert snap is not None  # guaranteed by _require_started
        snap["warnings"].append({"at": _iso(), "code": code, "detail": detail})
        snap["status"] = "WARNING"
        snap["last_heartbeat"] = _iso()
        self._write_snapshot()
        self._emit("progress.warning", {"code": code, "detail": detail})
        return dict(snap)

    def complete(self, status="COMPLETED", op="done"):
        if status not in ("COMPLETED", "FAILED"):
            raise ValueError("complete() status must be COMPLETED or FAILED")
        self._require_started("complete()")
        self._require_not_terminal("complete()")
        snap = self._snapshot
        assert snap is not None  # guaranteed by _require_started
        snap["status"] = status
        snap["current_operation"] = op
        if status == "COMPLETED" and snap["meta"].get("total"):
            snap["progress_pct"] = 100.0
        snap["eta"] = {"seconds": 0, "confidence": "high"} if status == "COMPLETED" else snap["eta"]
        snap["last_heartbeat"] = _iso()
        started = _parse_iso(snap["started_at"])
        snap["meta"]["duration_s"] = int(time.time() - started)
        self._write_snapshot()
        self._emit("progress.completed", {"final_status": status})
        return dict(snap)

    def block(self, reason):
        self._require_started("block()")
        self._require_not_terminal("block()")
        snap = self._snapshot
        assert snap is not None  # guaranteed by _require_started
        snap["status"] = "BLOCKED"
        snap["current_operation"] = f"BLOCKED: {reason}"
        snap["last_heartbeat"] = _iso()
        self._write_snapshot()
        self._emit("progress.blocked", {"reason": reason})
        return dict(snap)

    # ── internals ───────────────────────────────────────
    @staticmethod
    def _compute_speed(samples):
        if len(samples) < 2:
            return None
        (t0, v0), (t1, v1) = samples[0], samples[-1]
        dt = t1 - t0
        if dt <= 0:
            return None
        per_min = (v1 - v0) / dt * 60.0
        return {"value": round(per_min, 2), "unit": "units/min",
                "window_s": int(dt)}

    def _write_snapshot(self):
        os.makedirs(self.store_dir, exist_ok=True)
        path = os.path.join(self.store_dir, f"{self.execution_id}.json")
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(self._snapshot, f, ensure_ascii=False, indent=1)
        os.replace(tmp, path)

    def _emit(self, event_type, extra=None):
        assert event_type in EVENT_TYPES
        snap = self._snapshot
        assert snap is not None
        event = {
            "event_type": event_type,
            "execution_id": self.execution_id,
            "skill_id": self.skill_id,
            "namespace": self.namespace,
            "task_kind": self.task_kind,
            "phase": snap["phase"],
            "stage": snap["stage"],
            "status": snap["status"],
            "progress_pct": snap["progress_pct"],
            "current_operation": snap["current_operation"],
            "speed": snap["speed"],
            "eta": snap["eta"],
            "last_heartbeat": snap["last_heartbeat"],
            "timestamp": _iso(),
            "body_truncated": True,
        }
        if extra:
            event.update(extra)
        _append_event(event, self.events_dir)


# ── cross-process helpers (CLI / watch scripts) ─────────
def resume(execution_id, store_dir=None, events_dir=None):
    """Reconstruct a tracker from its snapshot (for cross-process emitters).

    The snapshot IS the state: lifecycle position, samples window and
    heartbeat config all travel with it.
    """
    store = store_dir or PROGRESS_DIR
    path = os.path.join(store, f"{execution_id}.json")
    if not os.path.exists(path):
        raise ProgressLifecycleError(f"no snapshot for execution_id={execution_id} — call start() first")
    with open(path) as f:
        snap = json.load(f)
    t = ProgressTracker(
        execution_id=snap["execution_id"], task_kind=snap["task_kind"],
        phase=snap["phase"], skill_id=snap.get("skill_id", ""),
        namespace=snap.get("namespace", ""),
        heartbeat_interval_s=snap.get("heartbeat_interval_s", DEFAULT_HEARTBEAT_INTERVAL_S),
        store_dir=store, events_dir=events_dir or EVENTS_DIR)
    t._snapshot = snap
    return t


def load_snapshot(execution_id, store_dir=None):
    path = os.path.join(store_dir or PROGRESS_DIR, f"{execution_id}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def list_snapshots(store_dir=None, active_only=False):
    store = store_dir or PROGRESS_DIR
    if not os.path.isdir(store):
        return []
    out = []
    for fname in sorted(os.listdir(store)):
        if not fname.endswith(".json"):
            continue
        try:
            with open(os.path.join(store, fname)) as f:
                snap = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        if active_only and snap.get("status") in TERMINAL_STATUSES:
            continue
        out.append(snap)
    return out
