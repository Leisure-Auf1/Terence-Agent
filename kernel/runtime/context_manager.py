"""B.6.2 — Context Manager: skill context lifecycle (UNLOADED→LOADING→READY→IN_USE→RELEASED)."""

import hashlib, os, json, time

CONTEXT_STATES = ["UNLOADED", "LOADING", "READY", "IN_USE", "RELEASED"]
CONTEXT_DIR = os.path.expanduser("~/.hermes/runtime/contexts")
SKILLS = os.path.expanduser("~/.hermes/skills")

_contexts = {}  # In-memory context registry

def load_context(skill_id: str, mount: str = "routed", skill_registry_path: str = None) -> dict:
    """Load skill content into context. Returns SkillRuntimeContext."""
    os.makedirs(CONTEXT_DIR, exist_ok=True)
    context_id = f"ctx-{int(time.time())}"
    
    # Locate SKILL.md via registry or direct path
    if skill_registry_path:
        skill_path = os.path.join(SKILLS, skill_registry_path, "SKILL.md")
    else:
        # Search skills directory
        skill_path = None
        for root, dirs, files in os.walk(SKILLS):
            if os.path.basename(root) == skill_id and "SKILL.md" in files:
                skill_path = os.path.join(root, "SKILL.md")
                break
        if not skill_path:
            return {"status": "CONTEXT_LOAD_FAILED", "error": "FILE_NOT_FOUND", "skill_id": skill_id}
    
    if not os.path.exists(skill_path):
        return {"status": "CONTEXT_LOAD_FAILED", "error": "FILE_NOT_FOUND", "skill_id": skill_id}
    
    # Read and verify
    with open(skill_path, "rb") as f:
        content = f.read()
    sha = hashlib.sha256(content).hexdigest()
    size = len(content)
    
    ctx = {
        "context_id": context_id,
        "skill_id": skill_id,
        "mount": mount,
        "state": "READY",
        "content_sha256": sha,
        "content_size": size,
        "loaded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "execution_id": None
    }
    _contexts[context_id] = ctx
    
    # Persist to disk
    with open(os.path.join(CONTEXT_DIR, f"{context_id}.json"), "w") as f:
        json.dump(ctx, f, indent=2)
    
    return {"status": "CONTEXT_READY", "context": ctx, "skill_id": skill_id}

def use_context(context_id: str) -> dict:
    """Mark context as IN_USE."""
    if context_id not in _contexts:
        return {"status": "ERROR", "error": "CONTEXT_NOT_FOUND"}
    _contexts[context_id]["state"] = "IN_USE"
    return {"status": "IN_USE", "context": _contexts[context_id]}

def release_context(context_id: str) -> dict:
    """Release context and free memory."""
    if context_id in _contexts:
        ctx = _contexts.pop(context_id)
        ctx["state"] = "RELEASED"
        ctx["released_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        # Update persisted record
        fpath = os.path.join(CONTEXT_DIR, f"{context_id}.json")
        if os.path.exists(fpath):
            with open(fpath, "w") as f:
                json.dump(ctx, f, indent=2)
        return {"status": "RELEASED", "context": ctx}
    return {"status": "ERROR", "error": "CONTEXT_NOT_FOUND"}

def get_active_contexts() -> list:
    return list(_contexts.values())

def is_mount_supported(mount: str) -> bool:
    return mount in ("routed", "auto", "manual")
