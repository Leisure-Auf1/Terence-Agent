"""B.6.2 — State Logger: append-only transition audit log."""

import json, os, time

LOG_DIR = os.path.expanduser("~/.hermes/runtime/state")

def log_transition(skill_id: str, from_state: str, to_state: str, 
                   actor: str = "kernel", reason: str = "") -> dict:
    """Append state transition to audit log."""
    os.makedirs(LOG_DIR, exist_ok=True)
    entry = {
        "skill_id": skill_id,
        "from_state": from_state,
        "to_state": to_state,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "actor": actor,
        "reason": reason
    }
    fname = os.path.join(LOG_DIR, "state-transitions.jsonl")
    with open(fname, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry

def get_transition_history(skill_id: str = None) -> list:
    """Read transition history. Filter by skill_id if provided."""
    fname = os.path.join(LOG_DIR, "state-transitions.jsonl")
    if not os.path.exists(fname):
        return []
    with open(fname) as f:
        entries = [json.loads(line) for line in f if line.strip()]
    if skill_id:
        entries = [e for e in entries if e["skill_id"] == skill_id]
    return entries
