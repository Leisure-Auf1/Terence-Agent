"""B.6.3 — Degradation Manager: auto-actions on health state transitions."""

import time

def handle_warning(skill_id: str, reason: str = "") -> dict:
    return {"skill_id": skill_id, "state": "WARNING", "actions": ["monitoring_increased", "warning_event_emitted"],
            "reason": reason, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

def handle_degraded(skill_id: str, reason: str = "") -> dict:
    return {"skill_id": skill_id, "state": "DEGRADED", 
            "actions": ["priority_lowered", "telemetry_frequency_increased", "maintenance_proposal_created"],
            "reason": reason, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

def handle_failed(skill_id: str, reason: str = "") -> dict:
    return {"skill_id": skill_id, "state": "FAILED",
            "actions": ["execution_blocked", "recovery_record_created"],
            "reason": reason, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

PROHIBITED = [
    "delete_skill", "modify_skill_file", "rename_skill", "change_registry", "auto_deprecate"
]

def assert_no_destructive_action(actions: list) -> bool:
    return not any(a in PROHIBITED for a in actions)
