"""B.6.4 — Governance Rules: immutable constraints for all governance actions."""

RULES = {
    "GOV-001": "Every destructive action requires human approval",
    "GOV-002": "Governance cannot bypass lifecycle state machine",
    "GOV-003": "Governance cannot modify SKILL.md body content",
    "GOV-004": "All governance actions require audit records",
    "GOV-005": "Cross-project changes require explicit governance review",
}

DESTRUCTIVE_ACTIONS = ["delete_skill", "modify_registry", "rename_skill", 
                        "change_namespace", "merge_automatically", "archive_automatically"]

def is_destructive(action: str) -> bool:
    return action in DESTRUCTIVE_ACTIONS

def requires_approval(action: str) -> bool:
    return is_destructive(action) or action in ["deprecate_skill", "change_owner", "change_scope"]

def validate_action(action: str, has_approval: bool = False) -> dict:
    if is_destructive(action) and not has_approval:
        return {"valid": False, "rule": "GOV-001", "reason": f"Destructive action '{action}' requires human approval"}
    return {"valid": True, "rule": None}

def assert_no_bypass(action: str, current_lifecycle: str) -> dict:
    """GOV-002: governance cannot bypass lifecycle."""
    if action == "archive_skill" and current_lifecycle != "deprecated":
        return {"valid": False, "rule": "GOV-002", "reason": f"Cannot archive from lifecycle '{current_lifecycle}'"}
    if action == "deprecate_skill" and current_lifecycle != "active":
        return {"valid": False, "rule": "GOV-002", "reason": f"Cannot deprecate from lifecycle '{current_lifecycle}'"}
    return {"valid": True, "rule": None}
