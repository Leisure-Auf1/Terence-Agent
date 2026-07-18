"""B.6.3 — Event Store: append-only JSONL event storage."""

import json, os, hashlib, time

STORE_DIR = os.path.expanduser("~/.hermes/runtime/telemetry/events")
os.makedirs(STORE_DIR, exist_ok=True)

def _today_file() -> str:
    return os.path.join(STORE_DIR, f"{time.strftime('%Y-%m-%d')}.jsonl")

def append_event(event: dict) -> dict:
    """Append event to today's JSONL file. Immutable once written."""
    fname = _today_file()
    event["_written_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    line = json.dumps(event, ensure_ascii=False)
    with open(fname, "a") as f:
        f.write(line + "\n")
    return {"stored": True, "file": fname, "event": event}

def query_events(skill_id: str = None, limit: int = 100) -> list:
    """Query events, optionally filtered by skill_id."""
    results = []
    for fname in sorted(os.listdir(STORE_DIR)):
        if not fname.endswith(".jsonl"): continue
        with open(os.path.join(STORE_DIR, fname)) as f:
            for line in f:
                if not line.strip(): continue
                try:
                    ev = json.loads(line)
                    if skill_id is None or ev.get("skill_id") == skill_id:
                        results.append(ev)
                except: pass
    return results[-limit:]

def count_events(skill_id: str = None) -> int:
    return len(query_events(skill_id, limit=10000))

def validate_integrity() -> dict:
    """Check event store integrity."""
    total, corrupt = 0, 0
    for fname in sorted(os.listdir(STORE_DIR)):
        if not fname.endswith(".jsonl"): continue
        with open(os.path.join(STORE_DIR, fname)) as f:
            for line in f:
                if not line.strip(): continue
                total += 1
                try: json.loads(line)
                except: corrupt += 1
    return {"total_events": total, "corrupt": corrupt, "healthy": corrupt == 0}
