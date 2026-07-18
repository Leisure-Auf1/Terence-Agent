"""B.6.4 — Proposal Store: append-only JSONL storage for governance proposals."""

import json, os, time

STORE_DIR = os.path.expanduser("~/.hermes/runtime/governance/proposals")
os.makedirs(STORE_DIR, exist_ok=True)

def _file(): return os.path.join(STORE_DIR, "proposals.jsonl")

def create(proposal: dict) -> dict:
    proposal["_stored_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(_file(), "a") as f:
        f.write(json.dumps(proposal, ensure_ascii=False) + "\n")
    return {"stored": True, "proposal_id": proposal.get("proposal_id")}

def get(proposal_id: str) -> dict:
    if not os.path.exists(_file()): return None
    with open(_file()) as f:
        for line in f:
            if not line.strip(): continue
            p = json.loads(line)
            if p.get("proposal_id") == proposal_id:
                return p
    return None

def list_all(status: str = None) -> list:
    if not os.path.exists(_file()): return []
    results = []
    with open(_file()) as f:
        for line in f:
            if not line.strip(): continue
            p = json.loads(line)
            if status is None or p.get("status") == status:
                results.append(p)
    return results

def update_status(proposal_id: str, new_status: str) -> dict:
    if not os.path.exists(_file()): return {"error": "No proposals exist"}
    all_proposals = []
    found = None
    with open(_file()) as f:
        for line in f:
            if not line.strip(): continue
            p = json.loads(line)
            if p.get("proposal_id") == proposal_id:
                p["status"] = new_status
                p["_updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                found = p
            all_proposals.append(p)
    if found:
        with open(_file(), "w") as f:
            for p in all_proposals:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")
        return {"updated": True, "proposal": found}
    return {"error": "Proposal not found"}

def validate_integrity() -> dict:
    if not os.path.exists(_file()): return {"total": 0, "corrupt": 0, "healthy": True}
    total, corrupt = 0, 0
    with open(_file()) as f:
        for line in f:
            if not line.strip(): continue
            total += 1
            try: 
                p = json.loads(line)
                if not p.get("proposal_id"): corrupt += 1
            except: corrupt += 1
    return {"total_proposals": total, "corrupt": corrupt, "healthy": corrupt == 0}
