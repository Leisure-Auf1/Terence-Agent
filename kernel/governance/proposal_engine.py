"""B.6.4 — Proposal Engine: generate governance proposals from health/telemetry data."""

import time, uuid, json

PROPOSAL_TYPES = {
    "P1": {"name": "MAINTENANCE_REQUIRED", "trigger": "DEGRADED", "priority": "P2"},
    "P2": {"name": "HEALTH_REVIEW", "trigger": "FAILED", "priority": "P1"},
    "P3": {"name": "ARCHIVE_CANDIDATE", "trigger": "INACTIVE", "priority": "P3"},
    "P4": {"name": "MERGE_REVIEW", "trigger": "DUPLICATE", "priority": "P3"},
    "P5": {"name": "DEPENDENCY_AUDIT", "trigger": "DEP_FAILURE", "priority": "P2"},
    "P6": {"name": "OWNERSHIP_REVIEW", "trigger": "OWNER_MISMATCH", "priority": "P2"},
    "P7": {"name": "NAMESPACE_REVIEW", "trigger": "NS_VIOLATION", "priority": "P1"},
    "P8": {"name": "CROSS_PROJECT_REVIEW", "trigger": "CROSS_ANOMALY", "priority": "P2"},
}

def generate(skill_id: str, proposal_type: str, namespace: str = "", 
             evidence: dict = None, reason: str = "") -> dict:
    """Generate a governance proposal."""
    if proposal_type not in PROPOSAL_TYPES:
        return {"status": "ERROR", "reason": f"Unknown proposal type: {proposal_type}"}
    
    pt = PROPOSAL_TYPES[proposal_type]
    return {
        "proposal_id": f"prop-{uuid.uuid4().hex[:12]}",
        "skill_id": skill_id,
        "namespace": namespace,
        "type": proposal_type,
        "type_name": pt["name"],
        "priority": pt["priority"],
        "reason": reason or f"Auto-generated: {pt['trigger']} condition detected",
        "evidence": evidence or {},
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "pending",
        "auto_generated": True,
        "requires_approval": True
    }

def generate_from_health(skill_id: str, health_state: str, namespace: str = "", metrics: dict = None) -> list:
    """Generate proposals based on health state."""
    proposals = []
    if health_state == "DEGRADED":
        proposals.append(generate(skill_id, "P1", namespace, metrics, f"Health state: {health_state}"))
    elif health_state == "FAILED":
        proposals.append(generate(skill_id, "P2", namespace, metrics, f"Health state: {health_state}"))
    elif health_state == "QUARANTINED":
        proposals.append(generate(skill_id, "P2", namespace, metrics, "QUARANTINED — immediate review required"))
    return proposals

def generate_from_trigger(skill_id: str, trigger: str, namespace: str = "", evidence: dict = None) -> dict:
    """Generate proposal from a specific trigger condition."""
    type_map = {"corruption": "P2", "security_violation": "P2", "repeated_failure": "P1",
                "cascade_failure": "P5", "governance_override": "P7",
                "owner_mismatch": "P6", "namespace_violation": "P7", "cross_anomaly": "P8"}
    ptype = type_map.get(trigger, "P1")
    return generate(skill_id, ptype, namespace, evidence, f"Trigger: {trigger}")
