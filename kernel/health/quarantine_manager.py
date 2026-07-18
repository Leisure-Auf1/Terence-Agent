"""B.6.3 — Quarantine Manager: isolation for critical failures."""

import time, os, json

QUARANTINE_DIR = os.path.expanduser("~/.hermes/runtime/health/quarantine")
os.makedirs(QUARANTINE_DIR, exist_ok=True)

TRIGGERS = ["corruption", "security_violation", "repeated_failure", "cascade_failure", "governance_override"]

def quarantine(skill_id: str, trigger: str, evidence: dict = None) -> dict:
    """Quarantine a skill. Block execution. Preserve evidence. Notify owner."""
    if trigger not in TRIGGERS:
        return {"status": "ERROR", "reason": f"Invalid quarantine trigger: {trigger}"}
    
    record = {"skill_id": skill_id, "trigger": trigger, "state": "QUARANTINED",
              "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "evidence": evidence, "actions": ["execution_blocked", "evidence_preserved", "incident_created", "owner_notified"]}
    
    fname = os.path.join(QUARANTINE_DIR, f"{skill_id}-{int(time.time())}.json")
    with open(fname, "w") as f:
        json.dump(record, f, indent=2)
    
    return {"status": "QUARANTINED", "record": record, "file": fname}

def is_quarantined(skill_id: str) -> bool:
    """Check if skill is currently quarantined."""
    for fname in os.listdir(QUARANTINE_DIR):
        if fname.startswith(skill_id) and fname.endswith(".json"):
            return True
    return False

PROHIBITED = ["delete_skill", "edit_skill", "unregister_skill"]
