"""HPP W2 — Progress CLI: shell-facing entry for the progress capability.

Usage (from any cwd):
  python ~/.hermes/kernel/telemetry/progress_cli.py start --id EID --kind docker_build \
      --phase "Phase 4" [--total 380 --unit MB --stages apt,pip --interval 60]
  python .../progress_cli.py update --id EID [--done 61] [--stage pip] [--op "..."] [--pct 42]
  python .../progress_cli.py heartbeat --id EID [--op "..."]
  python .../progress_cli.py warning --id EID --code SPEED_DROP [--detail "..."]
  python .../progress_cli.py complete --id EID [--failed]
  python .../progress_cli.py block --id EID --reason "..."
  python .../progress_cli.py snapshot --id EID
  python .../progress_cli.py list [--active]
  python .../progress_cli.py watchdog
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telemetry.progress_tracker import (  # noqa: E402
    ProgressTracker, ProgressLifecycleError, resume, load_snapshot, list_snapshots,
)
from telemetry import progress_watchdog  # noqa: E402


def main(argv=None):
    p = argparse.ArgumentParser(prog="progress")
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp):
        sp.add_argument("--id", required=True, dest="eid")

    sp = sub.add_parser("start")
    common(sp)
    sp.add_argument("--kind", required=True)
    sp.add_argument("--phase", required=True)
    sp.add_argument("--skill", default="")
    sp.add_argument("--namespace", default="")
    sp.add_argument("--total", type=float)
    sp.add_argument("--unit", default="")
    sp.add_argument("--stages", default="")
    sp.add_argument("--interval", type=int, default=60)
    sp.add_argument("--op", default="registered")

    sp = sub.add_parser("update")
    common(sp)
    sp.add_argument("--done", type=float)
    sp.add_argument("--stage")
    sp.add_argument("--op")
    sp.add_argument("--pct", type=float)

    sp = sub.add_parser("heartbeat")
    common(sp)
    sp.add_argument("--op")

    sp = sub.add_parser("warning")
    common(sp)
    sp.add_argument("--code", required=True)
    sp.add_argument("--detail", default="")

    sp = sub.add_parser("complete")
    common(sp)
    sp.add_argument("--failed", action="store_true")

    sp = sub.add_parser("block")
    common(sp)
    sp.add_argument("--reason", required=True)

    sp = sub.add_parser("snapshot")
    common(sp)

    sp = sub.add_parser("list")
    sp.add_argument("--active", action="store_true")

    sub.add_parser("watchdog")

    a = p.parse_args(argv)
    try:
        if a.cmd == "start":
            t = ProgressTracker(a.eid, a.kind, a.phase, skill_id=a.skill,
                                namespace=a.namespace, heartbeat_interval_s=a.interval)
            stages = [s for s in a.stages.split(",") if s] or None
            out = t.start(total=a.total, unit=a.unit, stages=stages, op=a.op)
        elif a.cmd == "update":
            out = resume(a.eid).update(stage=a.stage, done=a.done, op=a.op, pct=a.pct)
        elif a.cmd == "heartbeat":
            out = resume(a.eid).heartbeat(op=a.op)
        elif a.cmd == "warning":
            out = resume(a.eid).warning(a.code, a.detail)
        elif a.cmd == "complete":
            out = resume(a.eid).complete(status="FAILED" if a.failed else "COMPLETED")
        elif a.cmd == "block":
            out = resume(a.eid).block(a.reason)
        elif a.cmd == "snapshot":
            out = load_snapshot(a.eid) or {"error": f"no snapshot for {a.eid}"}
        elif a.cmd == "list":
            out = list_snapshots(active_only=a.active)
        elif a.cmd == "watchdog":
            out = progress_watchdog.scan()
        else:  # pragma: no cover
            out = {"error": "unknown command"}
    except ProgressLifecycleError as e:
        print(json.dumps({"error": "lifecycle", "detail": str(e)}), file=sys.stderr)
        return 2
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
