"""B.6.2 — Executor: execute_skill() with timeout, retry, fallback."""

import time

from .context_manager import load_context, use_context, release_context
from .permission_gate import check_permission, REQUIREMENTS
from .rollback_manager import rollback_context

def execute_skill(skill_id: str, caller_tier: int = 1, 
                  mount: str = "routed", timeout_ms: int = 300000,
                  max_retries: int = 3, skill_registry_path: str = None) -> dict:
    """
    Full execution pipeline: resolve → gate → load → execute → release.
    """
    execution_id = f"exec-{int(time.time())}"
    log = {"execution_id": execution_id, "skill_id": skill_id, "stages": []}
    
    # Stage 1: Permission check
    perm = check_permission(caller_tier, REQUIREMENTS.get("execute_skill", 2), "execute_skill")
    log["stages"].append({"stage": "permission", "result": perm})
    if not perm["allowed"]:
        return {"status": "PERMISSION_DENIED", "execution_id": execution_id, 
                "reason": perm["reason"], "log": log}
    
    # Stage 2: Load context
    ctx_result = load_context(skill_id, mount, skill_registry_path)
    log["stages"].append({"stage": "context_load", "result": ctx_result["status"]})
    if ctx_result["status"] != "CONTEXT_READY":
        return {"status": "CONTEXT_LOAD_FAILED", "execution_id": execution_id,
                "error": ctx_result.get("error"), "log": log}
    
    context = ctx_result["context"]
    context_id = context["context_id"]
    use_context(context_id)
    
    # Stage 3: Execute with retry
    for attempt in range(max_retries):
        try:
            # Simulate skill execution (in real implementation: dispatch to skill handler)
            start = time.time()
            # --- Skill execution would happen here ---
            time.sleep(0.001)  # Placeholder for actual execution
            elapsed_ms = int((time.time() - start) * 1000)
            
            if elapsed_ms > timeout_ms:
                log["stages"].append({"stage": "execution", "attempt": attempt+1, "result": "TIMEOUT"})
                if attempt < max_retries - 1:
                    continue
                release_context(context_id)
                return {"status": "FAILED", "execution_id": execution_id, 
                        "error": "TIMEOUT", "error_class": "F5", "log": log}
            
            # Success
            release_context(context_id)
            log["stages"].append({"stage": "execution", "attempt": attempt+1, "result": "SUCCESS"})
            return {"status": "SUCCESS", "execution_id": execution_id, 
                    "skill_id": skill_id, "duration_ms": elapsed_ms, "log": log}
        
        except Exception as e:
            log["stages"].append({"stage": "execution", "attempt": attempt+1, "result": "ERROR", "error": str(e)})
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            release_context(context_id)
            return {"status": "FAILED", "execution_id": execution_id, 
                    "error": str(e), "error_class": "F6", "log": log}
    
    release_context(context_id)
    return {"status": "FAILED", "execution_id": execution_id, 
            "error": "Max retries exhausted", "log": log}
