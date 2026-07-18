"""B.6.1 — Dependency Validator: check skill dependencies and forbidden pairs."""

import json, os
from typing import Dict, List

REG_PATH = os.path.expanduser("~/.hermes/skills/devops/skill-manager/references/skill-registry.json")

def _load_registry() -> dict:
    with open(REG_PATH) as f:
        return json.load(f)

def validate_dependencies(skill_id: str, caller_scope: str) -> Dict:
    """
    Validate that the skill's dependencies are resolvable and not forbidden.
    Returns {valid, reason, details}.
    """
    reg = _load_registry()
    
    # Find the skill
    skill = next((s for s in reg["skills"] if s["name"] == skill_id), None)
    if not skill:
        return {"valid": False, "reason": f"Skill '{skill_id}' not found in registry", "details": None}
    
    deps = skill.get("dependencies", {}).get("skills", [])
    if not deps:
        return {"valid": True, "reason": "No dependencies declared", "details": {"deps": []}}
    
    # Check each dependency exists in registry
    all_skill_names = {s["name"] for s in reg["skills"]}
    unresolved = [d for d in deps if d not in all_skill_names]
    if unresolved:
        return {
            "valid": False,
            "reason": f"Unresolved dependencies: {unresolved}",
            "details": {"unresolved": unresolved}
        }
    
    # Check forbidden pairs
    forbidden_pairs = reg.get("forbidden_pairs", [])
    for fp in forbidden_pairs:
        forbidden_skills = set(fp.get("forbidden", []))
        # Check if this skill + any dependency forms a forbidden pair
        deps_set = set(deps)
        if skill["name"] in forbidden_skills:
            overlap = deps_set & forbidden_skills
            if overlap:
                return {
                    "valid": False,
                    "reason": f"Forbidden pair: {skill['name']} with {list(overlap)} (task: {fp.get('task')})",
                    "details": {"forbidden_pair": fp.get("task")}
                }
    
    # Check namespace direction for each dependency (core→project, adapter→project)
    skill_scope = skill.get("scope", "")
    for dep_name in deps:
        dep = next((s for s in reg["skills"] if s["name"] == dep_name), None)
        if dep:
            dep_scope = dep.get("scope", "")
            # Core→Project forbidden
            if skill_scope == "core" and dep_scope == "project":
                return {
                    "valid": False,
                    "reason": f"Core skill '{skill_id}' depends on project skill '{dep_name}' — forbidden",
                    "details": {"violation": "core→project"}
                }
            # Adapter→Project forbidden
            if skill_scope == "adapter" and dep_scope == "project":
                return {
                    "valid": False,
                    "reason": f"Adapter skill '{skill_id}' depends on project skill '{dep_name}' — forbidden",
                    "details": {"violation": "adapter→project"}
                }
    
    return {"valid": True, "reason": f"All {len(deps)} dependencies resolved", "details": {"deps": deps, "resolved": True}}
