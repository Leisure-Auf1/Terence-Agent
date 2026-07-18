"""HPP W1 unit tests — progress_watchdog stale-heartbeat escalation."""

import json
import os
import sys
import time

import pytest

KERNEL = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.abspath(KERNEL))

from telemetry.progress_tracker import ProgressTracker, load_snapshot  # noqa: E402
from telemetry import progress_watchdog as wd  # noqa: E402


@pytest.fixture
def dirs(tmp_path):
    return str(tmp_path / "progress"), str(tmp_path / "progress-events")


def start_task(dirs, eid, interval=60):
    store, events = dirs
    t = ProgressTracker(eid, "test_task", "PhaseX", heartbeat_interval_s=interval,
                        store_dir=store, events_dir=events)
    t.start(total=100, unit="MB")
    return t


def read_events(dirs):
    _, events = dirs
    out = []
    if os.path.isdir(events):
        for f in sorted(os.listdir(events)):
            with open(os.path.join(events, f)) as fh:
                out += [json.loads(l) for l in fh if l.strip()]
    return out


def test_fresh_heartbeat_is_healthy(dirs):
    start_task(dirs, "exec-fresh")
    s = wd.scan(store_dir=dirs[0], events_dir=dirs[1])
    assert s == {"checked": 1, "healthy": 1, "warned": [], "blocked": []}


def test_stale_2x_escalates_to_warning(dirs):
    start_task(dirs, "exec-stale", interval=60)
    s = wd.scan(store_dir=dirs[0], events_dir=dirs[1], now=time.time() + 150)
    assert s["warned"] == ["exec-stale"] and s["blocked"] == []
    snap = load_snapshot("exec-stale", dirs[0])
    assert snap["status"] == "WARNING"
    assert snap["warnings"][-1]["code"] == "STALE_HEARTBEAT"
    assert read_events(dirs)[-1]["event_type"] == "progress.warning"


def test_stale_5x_escalates_to_blocked(dirs):
    start_task(dirs, "exec-dead", interval=60)
    s = wd.scan(store_dir=dirs[0], events_dir=dirs[1], now=time.time() + 400)
    assert s["blocked"] == ["exec-dead"]
    snap = load_snapshot("exec-dead", dirs[0])
    assert snap["status"] == "BLOCKED"
    ev = read_events(dirs)[-1]
    assert ev["event_type"] == "progress.blocked"
    assert ev["reason"] == "HEARTBEAT_LOST"
    assert ev["emitted_by"] == "progress_watchdog"


def test_terminal_snapshots_ignored(dirs):
    t = start_task(dirs, "exec-done")
    t.complete()
    s = wd.scan(store_dir=dirs[0], events_dir=dirs[1], now=time.time() + 10_000)
    assert s["checked"] == 0 and s["blocked"] == []


def test_warning_not_duplicated(dirs):
    start_task(dirs, "exec-w", interval=60)
    late = time.time() + 150
    wd.scan(store_dir=dirs[0], events_dir=dirs[1], now=late)
    wd.scan(store_dir=dirs[0], events_dir=dirs[1], now=late + 1)
    warn_events = [e for e in read_events(dirs) if e["event_type"] == "progress.warning"]
    assert len(warn_events) == 1  # second scan must not re-emit
