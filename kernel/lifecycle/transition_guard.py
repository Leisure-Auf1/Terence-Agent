"""B.6.2 — Transition Guard: namespace, permission, lifecycle rule enforcement."""

from .state_machine import is_transition_allowed

def guard_transition(skill_id: str, from_state: str, to_state: str, 
                     caller_tier: int = 1, reason: str = "") -> dict:
    """Full guard: check transition validity + permission + lifecycle rules."""
    
    # 1. Check valid transition
    result = is_transition_allowed(from_state, to_state)
    if not result["allowed"]:
        return {"allowed": False, "error": "INVALID_TRANSITION", "detail": result["reason"]}
    
    # 2. Permission check based on target state
    restricted_states = ["EXECUTING", "DEPRECATED", "ARCHIVED"]
    if to_state in restricted_states and caller_tier > 1:
        return {"allowed": False, "error": "PERMISSION_DENIED",
                "detail": f"Tier {caller_tier} cannot transition to {to_state} (requires tier 0-1)"}
    
    # 3. Lifecycle rules
    if to_state == "ARCHIVED" and from_state != "DEPRECATED":
        return {"allowed": False, "error": "LIFECYCLE_VIOLATION",
                "detail": "Can only archive from DEPRECATED state"}
    
    return {"allowed": True, "from_state": from_state, "to_state": to_state, 
            "skill_id": skill_id, "reason": reason, "caller_tier": caller_tier}
