"""B.6.4 — Approval Manager: human gate enforcement for governance proposals."""

import time, os, json

APPROVAL_DIR = os.path.expanduser("~/.hermes/runtime/governance/approvals")
os.makedirs(APPROVAL_DIR, exist_ok=True)

VALID_TRANSITIONS = {
    "pending": ["approved", "rejected"],
    "approved": ["executable"],
    "rejected": ["closed"],
    "executable": [],
    "closed": [],
}

AUTO_ALLOWED = ["create_proposal", "assign_priority", "collect_evidence", "notify_owner"]
AUTO_FORBIDDEN = ["delete_skill", "modify_registry", "rename_skill", 
                   "change_namespace", "merge_automatically", "archive_automatically"]

def submit_for_approval(proposal: dict) -> dict:
    """Submit proposal to approval queue."""
    fname = os.path.join(APPROVAL_DIR, f"{proposal['proposal_id']}.json")
    proposal["submitted_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(fname, "w") as f:
        json.dump(proposal, f, indent=2)
    return {"status": "pending_approval", "proposal_id": proposal["proposal_id"]}

def approve(proposal_id: str, approver: str = "governance") -> dict:
    fname = os.path.join(APPROVAL_DIR, f"{proposal_id}.json")
    if not os.path.exists(fname): return {"error": "Proposal not found"}
    with open(fname) as f: prop = json.load(f)
    prop["status"] = "approved"
    prop["approved_by"] = approver
    prop["approved_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(fname, "w") as f: json.dump(prop, f, indent=2)
    return {"status": "approved", "proposal": prop}

def reject(proposal_id: str, reason: str = "", rejecter: str = "governance") -> dict:
    fname = os.path.join(APPROVAL_DIR, f"{proposal_id}.json")
    if not os.path.exists(fname): return {"error": "Proposal not found"}
    with open(fname) as f: prop = json.load(f)
    prop["status"] = "rejected"
    prop["rejected_by"] = rejecter
    prop["rejection_reason"] = reason
    prop["rejected_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(fname, "w") as f: json.dump(prop, f, indent=2)
    return {"status": "rejected", "proposal": prop}

def is_auto_allowed(action: str) -> bool:
    return action in AUTO_ALLOWED

def is_auto_forbidden(action: str) -> bool:
    return action in AUTO_FORBIDDEN
