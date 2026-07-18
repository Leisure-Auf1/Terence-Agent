"""B.6.2 — Permission Gate: tier-based access control (G1-G6)."""

VALID_TIERS = {0: "governance", 1: "platform", 2: "project", 3: "maintainer"}

def check_permission(caller_tier: int, required_tier: int, action: str = "execute") -> dict:
    """
    Higher tier (lower number) can call lower tier (higher number).
    Tier 0 can do anything. Tier 3 is most restricted.
    """
    if caller_tier < 0 or caller_tier > 3:
        return {"allowed": False, "reason": f"Invalid caller tier: {caller_tier}", 
                "required_tier": required_tier, "error_code": "INVALID_TIER"}
    
    if caller_tier <= required_tier:
        return {"allowed": True, 
                "reason": f"Tier {VALID_TIERS[caller_tier]} ({caller_tier}) ≥ required tier {required_tier} for {action}",
                "required_tier": required_tier}
    
    return {"allowed": False, 
            "reason": f"Tier {VALID_TIERS[caller_tier]} ({caller_tier}) cannot perform {action} (requires tier {required_tier})",
            "required_tier": required_tier, "error_code": "PERMISSION_DENIED"}

# Pre-defined permission requirements
REQUIREMENTS = {
    "execute_skill": 2,       # Tier 2+ (project owner) can execute
    "load_core_skill": 1,     # Tier 1+ (platform) can load core
    "load_project_skill": 2,  # Tier 2+ (project owner) can load project
    "modify_metadata": 1,     # Tier 1+ can modify metadata
    "governance_action": 0,   # Tier 0 only for governance
    "read_registry": 3,       # Tier 3+ (anyone) can read
}
