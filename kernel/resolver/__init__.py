"""B.6.1 — Skill Resolver Runtime: resolve_skill() pipeline."""

import json, os, time
from typing import Dict, List, Optional

from .capability_resolver import resolve_capabilities
from .namespace_resolver import check_namespace
from .ownership_validator import validate_ownership
from .dependency_validator import validate_dependencies

RUNTIME = os.path.expanduser("~/.hermes/runtime/resolver")

def _log_resolution(entry: dict):
    """Append resolution record to history."""
    os.makedirs(f"{RUNTIME}/resolution-history", exist_ok=True)
    ts = time.strftime("%Y-%m-%dT%H:%M:%S")
    fname = f"{RUNTIME}/resolution-history/{ts}-{entry.get('execution_id','unknown')}.json"
    with open(fname, "w") as f:
        json.dump(entry, f, indent=2)

def resolve_skill(intent: str, caller_scope: str = "adapter", 
                  caller_tier: int = 1, max_candidates: int = 10) -> Dict:
    """
    Full 4-stage resolution pipeline.
    
    Returns:
      {status, skill_id, namespace, scope, owner, candidates, pipeline_log}
    
    Status values:
      SUCCESS, NO_MATCH, NAMESPACE_BLOCKED, OWNERSHIP_FAILED, DEPENDENCY_FAILED
    """
    execution_id = f"res-{int(time.time())}"
    log = {"execution_id": execution_id, "intent": intent, "caller_scope": caller_scope, "stages": []}
    
    # Stage 1: Capability matching
    candidates = resolve_capabilities(intent, caller_scope)
    log["stages"].append({"stage": "capability", "candidates_found": len(candidates)})
    
    if not candidates:
        result = {"status": "NO_MATCH", "skill_id": None, "reason": "No capability match found", "candidates": []}
        log["result"] = result
        _log_resolution(log)
        return result
    
    # Stage 2-4: Validate each candidate through pipeline
    for candidate in candidates[:max_candidates]:
        skill_id = candidate["skill_id"]
        skill_scope = candidate["scope"]
        skill_namespace = candidate["namespace"]
        skill_owner = candidate["owner"]
        
        # Stage 2: Namespace check
        ns_result = check_namespace(caller_scope, skill_scope, skill_namespace)
        log["stages"].append({"stage": "namespace", "skill": skill_id, "result": ns_result})
        if not ns_result["allowed"]:
            continue
        
        # Stage 3: Ownership validation
        own_result = validate_ownership(skill_namespace, skill_owner, skill_scope)
        log["stages"].append({"stage": "ownership", "skill": skill_id, "result": own_result})
        if not own_result["valid"]:
            continue
        
        # Stage 4: Dependency validation
        dep_result = validate_dependencies(skill_id, caller_scope)
        log["stages"].append({"stage": "dependency", "skill": skill_id, "result": dep_result})
        if not dep_result["valid"]:
            continue
        
        # All gates passed
        result = {
            "status": "SUCCESS",
            "skill_id": skill_id,
            "namespace": skill_namespace,
            "scope": skill_scope,
            "owner": skill_owner,
            "lifecycle": candidate["lifecycle"],
            "score": candidate["capability_score"],
            "candidates": candidates[:5],
            "pipeline_log": log["stages"]
        }
        log["result"] = result
        _log_resolution(log)
        return result
    
    # All candidates failed some gate
    result = {"status": "NAMESPACE_BLOCKED", "skill_id": None, 
              "reason": "All candidates failed namespace/ownership/dependency validation",
              "candidates": candidates[:5]}
    log["result"] = result
    _log_resolution(log)
    return result

# Module metadata
__version__ = "0.1.0"
__phase__ = "B.6.1"
