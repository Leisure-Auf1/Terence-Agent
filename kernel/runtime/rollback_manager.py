"""B.6.2 — Rollback Manager: context rollback, state rollback, runtime recovery."""

import os, json, time

ROLLBACK_DIR = os.path.expanduser("~/.hermes/runtime/rollback")
os.makedirs(ROLLBACK_DIR, exist_ok=True)

def save_rollback_snapshot(skill_id: str, state: str, context: dict = None) -> str:
    """Save snapshot before risky operation."""
    snap_id = f"snap-{skill_id}-{int(time.time())}"
    snap = {
        "snap_id": snap_id,
        "skill_id": skill_id,
        "state": state,
        "context": context,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    with open(os.path.join(ROLLBACK_DIR, f"{snap_id}.json"), "w") as f:
        json.dump(snap, f, indent=2)
    return snap_id

def rollback_context(context_id: str) -> dict:
    """Rollback a context — release and return to pre-load state."""
    from .context_manager import release_context, _contexts
    if context_id in _contexts:
        release_context(context_id)
    return {"status": "ROLLED_BACK", "context_id": context_id, "action": "context_released"}

def rollback_state(skill_id: str, target_state: str, reason: str = "") -> dict:
    """Rollback a skill to a specific state."""
    from lifecycle.state_logger import log_transition
    log_transition(skill_id, "ROLLBACK", target_state, "rollback_manager", reason)
    return {"status": "ROLLED_BACK", "skill_id": skill_id, "target_state": target_state, "reason": reason}

def is_rollback_needed(error_class: str) -> bool:
    """Determine if rollback is needed based on error class."""
    return error_class in ("F4",)  # Corruption always requires rollback

def restore_from_snapshot(snap_id: str) -> dict:
    """Restore skill state from a saved snapshot."""
    fpath = os.path.join(ROLLBACK_DIR, f"{snap_id}.json")
    if not os.path.exists(fpath):
        return {"status": "ERROR", "error": "SNAPSHOT_NOT_FOUND"}
    with open(fpath) as f:
        snap = json.load(f)
    return {"status": "RESTORED", "snapshot": snap}
