"""B.6.3 — Recovery Manager: retry, fallback, rollback, owner intervention."""

import time, os, json

RECOVERY_DIR = os.path.expanduser("~/.hermes/runtime/health/recovery")
os.makedirs(RECOVERY_DIR, exist_ok=True)

MAX_RETRIES = 3

def retry(skill_id: str, attempt: int, max_retries: int = MAX_RETRIES) -> dict:
    if attempt >= max_retries:
        return {"status": "EXHAUSTED", "skill_id": skill_id, "attempt": attempt, "action": "escalate_to_fallback"}
    wait = 2 ** (attempt - 1)  # Exponential backoff
    time.sleep(0.001)  # Placeholder
    return {"status": "RETRYING", "skill_id": skill_id, "attempt": attempt, "next_wait_s": wait}

def fallback(skill_id: str, fallback_id: str = None) -> dict:
    if not fallback_id:
        return {"status": "NO_FALLBACK", "skill_id": skill_id, "action": "report_to_user"}
    return {"status": "FALLBACK_DISPATCHED", "skill_id": skill_id, "fallback_to": fallback_id}

def rollback(skill_id: str, snapshot_id: str = None) -> dict:
    return {"status": "ROLLED_BACK", "skill_id": skill_id, "snapshot": snapshot_id or "latest"}

def create_recovery_record(skill_id: str, recovery_path: list, result: str) -> dict:
    record = {"skill_id": skill_id, "recovery_path": recovery_path, "result": result,
              "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    fname = os.path.join(RECOVERY_DIR, f"{skill_id}-recovery-{int(time.time())}.json")
    with open(fname, "w") as f:
        json.dump(record, f, indent=2)
    return {"status": "RECORDED", "record": record, "file": fname}
