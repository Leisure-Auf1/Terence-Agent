"""B.6.3 — Health Engine: score calculation and state classification."""

import sys, os
sys.path.insert(0, os.path.expanduser("~/.hermes/kernel"))
from telemetry.metrics_aggregator import aggregate_skill

HEALTH_STATES = {range(90, 101): "HEALTHY", range(75, 90): "WARNING",
                 range(50, 75): "DEGRADED", range(25, 50): "FAILED",
                 range(0, 25): "QUARANTINED"}

def calculate_score(metrics: dict) -> dict:
    """Compute 0-100 health score from metrics."""
    sr = metrics.get("success_rate", 100.0)
    fc = metrics.get("failure_count", 0)
    lat = metrics.get("p95_latency_ms", 0)
    
    # Success rate (0-35)
    sr_score = 35 if sr >= 98 else (30 if sr >= 95 else (22 if sr >= 90 else (14 if sr >= 80 else (7 if sr >= 70 else 0))))
    
    # Failure frequency (0-25)
    ff_score = 25 if fc == 0 else (20 if fc <= 2 else (13 if fc <= 5 else (6 if fc <= 10 else 0)))
    
    # Latency (0-15)
    lat_score = 15 if lat < 5000 else (12 if lat < 15000 else (8 if lat < 30000 else (4 if lat < 60000 else 0)))
    
    # Dependency (0-15): assume healthy if no events
    dep_score = 15
    
    # Trend (0-10): assume stable
    trend_score = 6
    
    total = sr_score + ff_score + lat_score + dep_score + trend_score
    return {"score": min(total, 100), "factors": {"success_rate": sr_score, "failure_frequency": ff_score,
            "latency": lat_score, "dependency": dep_score, "trend": trend_score}}

def evaluate(skill_id: str) -> dict:
    """Evaluate health for a skill. Returns {score, state, factors}."""
    metrics = aggregate_skill(skill_id)
    result = calculate_score(metrics)
    state = "HEALTHY"
    for rng, st in HEALTH_STATES.items():
        if result["score"] in rng:
            state = st
            break
    return {"skill_id": skill_id, "score": result["score"], "state": state,
            "factors": result["factors"], "metrics": metrics}

def get_state(skill_id: str) -> str:
    return evaluate(skill_id)["state"]

def is_deterministic(skill_id: str) -> bool:
    """Verify same input produces same score."""
    e1 = evaluate(skill_id)
    e2 = evaluate(skill_id)
    return e1["score"] == e2["score"]
