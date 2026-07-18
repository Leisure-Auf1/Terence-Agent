"""HPP W1 unit tests — ProgressTracker lifecycle, snapshot, events."""

import json
import os
import sys
import time

import pytest

KERNEL = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.abspath(KERNEL))

from telemetry.progress_tracker import (  # noqa: E402
    ProgressTracker, ProgressLifecycleError, resume, load_snapshot,
    list_snapshots, get_observability, DEFAULT_OBSERVABILITY,
)


@pytest.fixture
def dirs(tmp_path):
    return str(tmp_path / "progress"), str(tmp_path / "progress-events")


def make(dirs, eid="exec-t1"):
    store, events = dirs
    return ProgressTracker(eid, "docker_build", "Phase 4", skill_id="adapter.test",
                           namespace="adapter", heartbeat_interval_s=60,
                           store_dir=store, events_dir=events)


def read_events(dirs):
    _, events = dirs
    out = []
    if os.path.isdir(events):
        for f in sorted(os.listdir(events)):
            with open(os.path.join(events, f)) as fh:
                out += [json.loads(l) for l in fh if l.strip()]
    return out


# ── lifecycle validation: started -> updated* -> terminal ──

def test_update_before_start_raises(dirs):
    t = make(dirs)
    with pytest.raises(ProgressLifecycleError):
        t.update(done=1)


def test_warning_before_start_raises(dirs):
    t = make(dirs)
    with pytest.raises(ProgressLifecycleError):
        t.warning("X")


def test_complete_before_start_raises(dirs):
    t = make(dirs)
    with pytest.raises(ProgressLifecycleError):
        t.complete()


def test_double_start_raises(dirs):
    t = make(dirs)
    t.start(total=100, unit="MB")
    with pytest.raises(ProgressLifecycleError):
        t.start()


def test_update_after_terminal_raises(dirs):
    t = make(dirs)
    t.start(total=100, unit="MB")
    t.complete()
    with pytest.raises(ProgressLifecycleError):
        t.update(done=50)


def test_block_after_complete_raises(dirs):
    t = make(dirs)
    t.start()
    t.complete()
    with pytest.raises(ProgressLifecycleError):
        t.block("late")


def test_happy_path_lifecycle(dirs):
    t = make(dirs)
    t.start(total=200, unit="MB", stages=["apt", "pip"])
    t.update(stage="pip", done=50, op="downloading")
    t.update(done=100)
    snap = t.complete()
    assert snap["status"] == "COMPLETED"
    assert snap["progress_pct"] == 100.0
    types = [e["event_type"] for e in read_events(dirs)]
    assert types == ["progress.started", "progress.updated",
                     "progress.updated", "progress.completed"]


# ── snapshot content: 8 required fields ──

def test_snapshot_required_fields(dirs):
    t = make(dirs)
    t.start(total=100, unit="MB")
    t.update(done=42, op="downloading X")
    snap = load_snapshot("exec-t1", dirs[0])
    for field in ("phase", "stage", "status", "progress_pct",
                  "current_operation", "speed", "eta", "last_heartbeat"):
        assert field in snap, f"missing required field: {field}"
    assert snap["progress_pct"] == 42.0
    assert snap["status"] == "RUNNING"


def test_speed_and_eta_computed(dirs):
    t = make(dirs)
    t.start(total=100, unit="MB")
    t._snapshot["meta"]["samples"][0][0] -= 60  # backdate start sample 1 min
    t.update(done=20)
    snap = load_snapshot("exec-t1", dirs[0])
    assert snap["speed"] is not None and snap["speed"]["value"] > 0
    assert snap["eta"] is not None and snap["eta"]["seconds"] > 0


def test_block_records_reason(dirs):
    t = make(dirs)
    t.start()
    snap = t.block("dependency unreachable")
    assert snap["status"] == "BLOCKED"
    assert "dependency unreachable" in snap["current_operation"]
    assert read_events(dirs)[-1]["event_type"] == "progress.blocked"


def test_warning_then_update_recovers(dirs):
    t = make(dirs)
    t.start(total=10, unit="files")
    t.warning("SPEED_DROP", "rate -90%")
    assert load_snapshot("exec-t1", dirs[0])["status"] == "WARNING"
    t.update(done=5)
    assert load_snapshot("exec-t1", dirs[0])["status"] == "RUNNING"


# ── cross-process resume ──

def test_resume_preserves_lifecycle(dirs):
    t = make(dirs)
    t.start(total=100, unit="MB")
    t.update(done=30)
    t2 = resume("exec-t1", store_dir=dirs[0], events_dir=dirs[1])
    snap = t2.update(done=60)
    assert snap["progress_pct"] == 60.0
    t2.complete()
    t3 = resume("exec-t1", store_dir=dirs[0], events_dir=dirs[1])
    with pytest.raises(ProgressLifecycleError):
        t3.update(done=70)


def test_resume_unknown_id_raises(dirs):
    with pytest.raises(ProgressLifecycleError):
        resume("exec-nope", store_dir=dirs[0])


# ── listing ──

def test_list_active_filters_terminal(dirs):
    a = make(dirs, "exec-a"); a.start()
    b = make(dirs, "exec-b"); b.start(); b.complete()
    active = list_snapshots(dirs[0], active_only=True)
    assert [s["execution_id"] for s in active] == ["exec-a"]
    assert len(list_snapshots(dirs[0])) == 2


# ── W3 read-side observability defaults ──

def test_observability_defaults():
    assert get_observability({}) == DEFAULT_OBSERVABILITY
    assert get_observability({"observability": {"progress": True}})["progress"] is True
    assert get_observability({"observability": {"progress": True}})["heartbeat"] == "auto"
    assert get_observability({"observability": "garbage"}) == DEFAULT_OBSERVABILITY
