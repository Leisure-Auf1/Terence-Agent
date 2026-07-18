"""B.6.1 — Namespace Resolver: enforce C.3 namespace boundary rules."""

from typing import Dict

# Allowed dependency directions per C.3 model
ALLOWED_DIRECTIONS = {
    ("core", "core"): True,
    ("core", "adapter"): False,     # Core must not depend on adapter
    ("core", "project"): False,     # Core must not depend on project
    ("adapter", "core"): True,      # Adapter may use core
    ("adapter", "adapter"): True,
    ("adapter", "project"): False,  # Adapter must not depend on project
    ("project", "core"): True,      # Project may use core
    ("project", "adapter"): True,   # Project may use adapter
    ("project", "project"): True,   # Same-project allowed; cross-project checked elsewhere
}

def check_namespace(caller_scope: str, skill_scope: str, skill_namespace: str = "") -> Dict:
    """Validate namespace direction. Returns {allowed, reason, violated_rule}."""
    
    # Normalize scopes
    def normalize(scope: str) -> str:
        if scope.startswith("hermes.core"):
            return "core"
        if scope.startswith("adapter"):
            return "adapter"
        if scope.startswith("project."):
            return "project"
        return scope
    
    caller = normalize(caller_scope)
    skill = normalize(skill_scope)
    
    allowed = ALLOWED_DIRECTIONS.get((caller, skill), False)
    
    if allowed:
        return {"allowed": True, "reason": f"{caller}→{skill} is allowed", "violated_rule": None}
    elif (caller, skill) == ("core", "adapter"):
        return {"allowed": False, "reason": "Core must not depend on adapter", "violated_rule": "R1: Core→Adapter forbidden"}
    elif (caller, skill) == ("core", "project"):
        return {"allowed": False, "reason": "Core must not depend on any project", "violated_rule": "R1: Core→Project forbidden"}
    elif (caller, skill) == ("adapter", "project"):
        return {"allowed": False, "reason": "Adapter must be project-neutral", "violated_rule": "R2: Adapter→Project forbidden"}
    else:
        return {"allowed": False, "reason": f"Unknown direction: {caller}→{skill}", "violated_rule": "UNKNOWN"}
