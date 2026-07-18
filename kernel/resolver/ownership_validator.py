"""B.6.1 — Ownership Validator: verify skill ownership matches namespace model."""

from typing import Dict

# Valid ownership assignments per C.3 model
VALID_OWNERS = {
    # Core tier 0: hermes-governance
    "hermes.core.governance": "hermes-governance",
    "hermes.core.constraints": "hermes-governance", 
    "hermes.core.errors": "hermes-governance",
    "hermes.core.tracker": "hermes-governance",
    "hermes.core.auditor": "hermes-governance",
    # Core tier 1: hermes-platform
    "hermes.core.guidance": "hermes-platform",
    "hermes.core.registry": "hermes-platform",
    "hermes.core.preflight": "hermes-platform",
    "hermes.core.logger": "hermes-platform",
    "hermes.core.debugger": "hermes-platform",
    "hermes.core.developer": "hermes-platform",
    "hermes.core.executor": "hermes-platform",
    "hermes.core.coding": "hermes-platform",
    "hermes.core.webhooks": "hermes-platform",
}

def validate_ownership(skill_namespace: str, skill_owner: str, skill_scope: str) -> Dict:
    """
    Validate that the skill's owner matches the namespace model.
    Returns {valid, reason, error_code}.
    """
    
    # Core skills: must match known owner
    if skill_scope == "core":
        expected = VALID_OWNERS.get(skill_namespace)
        if expected and skill_owner != expected:
            return {
                "valid": False,
                "reason": f"Core skill '{skill_namespace}' owner '{skill_owner}' does not match expected '{expected}'",
                "error_code": "OWNER_MISMATCH"
            }
        return {"valid": True, "reason": "Core owner verified", "error_code": None}
    
    # Adapter skills: must be hermes-platform
    if skill_scope == "adapter":
        if skill_owner != "hermes-platform":
            return {
                "valid": False,
                "reason": f"Adapter skill owner '{skill_owner}' must be 'hermes-platform'",
                "error_code": "OWNER_MISMATCH"
            }
        return {"valid": True, "reason": "Adapter owner verified", "error_code": None}
    
    # Project skills: any project team owner is valid
    if skill_scope == "project":
        if not skill_owner:
            return {
                "valid": False,
                "reason": "Project skill must have an owner",
                "error_code": "OWNER_MISSING"
            }
        return {"valid": True, "reason": f"Project owner '{skill_owner}' accepted", "error_code": None}
    
    return {"valid": False, "reason": f"Unknown scope: {skill_scope}", "error_code": "UNKNOWN_SCOPE"}
