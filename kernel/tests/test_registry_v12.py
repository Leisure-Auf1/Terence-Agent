"""HPP W3 tests — Registry schema v1.2 compatibility (149 skills, zero migration)."""

import json
import os
import sys

KERNEL = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.abspath(KERNEL))

from telemetry.progress_tracker import get_observability, DEFAULT_OBSERVABILITY  # noqa: E402

REPO_REG = os.path.expanduser("~/Terence-Agent/skill-manager/skill-registry.json")
DEPLOYED_REG = os.path.expanduser(
    "~/.hermes/skills/devops/skill-manager/references/skill-registry.json")


def _load(path):
    with open(path) as f:
        return json.load(f)


def test_registry_v12_loads_149():
    for path in (REPO_REG, DEPLOYED_REG):
        r = _load(path)
        assert r["version"] == "1.2.0"
        assert r["schema_version"] == "1.2"
        assert len(r["skills"]) == 149


def test_observability_field_documented():
    r = _load(DEPLOYED_REG)
    assert "observability" in r["fields"]


def test_governance_structures_intact():
    r = _load(DEPLOYED_REG)
    assert len(r["forbidden_pairs"]) == 5
    assert len(r["mount_strategies"]) == 3
    scopes = {}
    for s in r["skills"]:
        scopes[s.get("scope", "?")] = scopes.get(s.get("scope", "?"), 0) + 1
    assert scopes == {"core": 14, "adapter": 123, "project": 12}


def test_all_149_entries_get_observability_defaults():
    """No entry declares observability yet — every consumer must receive defaults."""
    r = _load(DEPLOYED_REG)
    for s in r["skills"]:
        obs = get_observability(s)
        assert set(obs) == {"heartbeat", "progress", "eta"}
        if "observability" not in s:
            assert obs == DEFAULT_OBSERVABILITY


def test_repo_deployed_byte_sync():
    with open(REPO_REG, "rb") as a, open(DEPLOYED_REG, "rb") as b:
        assert a.read() == b.read()
