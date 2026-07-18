"""B.6.1 — Capability Resolver: match user intent to skill candidates."""

import json, os, re
from typing import List, Dict, Optional

REG_PATH = os.path.expanduser("~/.hermes/skills/devops/skill-manager/references/skill-registry.json")

def _load_registry() -> dict:
    with open(REG_PATH) as f:
        return json.load(f)

def resolve_capabilities(intent: str, caller_scope: str = "adapter") -> List[Dict]:
    """Match intent text against all registered skills. Returns ranked candidates."""
    reg = _load_registry()
    candidates = []
    intent_lower = intent.lower()
    
    for skill in reg["skills"]:
        name = skill["name"]
        desc = skill.get("description", "").lower()
        triggers = [t.lower() for t in skill.get("trigger", [])]
        tags = [t.lower() for t in skill.get("tags", [])]
        capability = skill.get("capability", "").lower()
        namespace = skill.get("namespace", "")
        scope = skill.get("scope", "")
        lifecycle = skill.get("lifecycle", "active")
        status = skill.get("status", "ok")
        
        # Skip archived skills
        if lifecycle == "archived":
            continue
        
        score = 0
        
        # Exact trigger match: +10
        for t in triggers:
            if t in intent_lower:
                score += 10
                break
        
        # Partial trigger match: +7
        if score == 0:
            for t in triggers:
                if any(word in intent_lower for word in t.split()):
                    score += 7
                    break
        
        # Domain match: +5
        if capability and capability in intent_lower:
            score += 5
        
        # Keyword match in description: +3
        keywords = re.findall(r'\b\w{4,}\b', intent_lower)
        for kw in keywords:
            if kw in desc:
                score += 3
                break
        
        # Tag match: +2
        for tag in tags:
            if tag in intent_lower:
                score += 2
                break
        
        # Namespace proximity bonus: +2 if same layer
        if caller_scope.startswith("project") and scope == "project":
            score += 2
        
        # Lifecycle penalty: deprecated = -5
        if lifecycle == "deprecated":
            score -= 5
        
        # Status penalty: non-ok = -3
        if status not in ("ok", "grace_period"):
            score -= 3
        
        candidates.append({
            "skill_id": name,
            "capability_score": score,
            "namespace": namespace,
            "scope": scope,
            "owner": skill.get("owner", ""),
            "lifecycle": lifecycle,
            "status": status,
            "triggers": triggers,
            "mount": skill.get("mount", "routed")
        })
    
    # Sort by score descending
    candidates.sort(key=lambda c: c["capability_score"], reverse=True)
    return [c for c in candidates if c["capability_score"] > 0]
