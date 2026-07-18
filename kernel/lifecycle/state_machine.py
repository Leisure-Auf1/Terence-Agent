"""B.6.2 — 13-State Lifecycle Machine."""

VALID_TRANSITIONS = {
    "PROPOSED":      ["REGISTERED"],
    "REGISTERED":    ["AVAILABLE"],
    "AVAILABLE":     ["RESOLVED", "DEPRECATED"],
    "RESOLVED":      ["LOADING", "AVAILABLE"],
    "LOADING":       ["CONTEXT_READY", "FAILED", "DEGRADED"],
    "CONTEXT_READY": ["EXECUTING", "AVAILABLE"],
    "EXECUTING":     ["SUCCESS", "FAILED", "DEGRADED"],
    "SUCCESS":       ["AVAILABLE"],
    "FAILED":        ["RECOVERY", "DEGRADED"],
    "DEGRADED":      ["RECOVERY", "AVAILABLE", "FAILED"],
    "RECOVERY":      ["AVAILABLE", "FAILED", "DEGRADED"],
    "DEPRECATED":    ["ARCHIVED"],
    "ARCHIVED":      [],
}

FORBIDDEN_TRANSITIONS = {
    ("FAILED", "EXECUTING"): "Must go through RECOVERY or AVAILABLE",
    ("ARCHIVED", "AVAILABLE"): "Terminal state — re-register as PROPOSED",
    ("ARCHIVED", "any"): "Terminal — no exits from ARCHIVED",
    ("DEGRADED", "SUCCESS"): "Degraded cannot retroactively succeed",
    ("PROPOSED", "EXECUTING"): "Bypasses registration and activation",
}

def get_allowed_transitions(state: str) -> list:
    return VALID_TRANSITIONS.get(state, [])

def is_transition_allowed(from_state: str, to_state: str) -> dict:
    if to_state not in VALID_TRANSITIONS.get(from_state, []):
        reason = FORBIDDEN_TRANSITIONS.get((from_state, to_state),
                 FORBIDDEN_TRANSITIONS.get((from_state, "any"),
                 f"Transition {from_state}→{to_state} is not defined"))
        return {"allowed": False, "from_state": from_state, "to_state": to_state, "reason": reason}
    return {"allowed": True, "from_state": from_state, "to_state": to_state, "reason": "Valid transition"}

def get_state_graph() -> dict:
    return {"states": list(VALID_TRANSITIONS.keys()), "transitions": {k: v for k, v in VALID_TRANSITIONS.items()}}
