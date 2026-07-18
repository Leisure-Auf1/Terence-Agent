"""B.6.3 — Metrics Aggregator: compute rolling metrics from event store."""

from .event_store import query_events

def aggregate_skill(skill_id: str, window_hours: int = 24) -> dict:
    """Compute metrics for a single skill over time window."""
    events = query_events(skill_id, limit=1000)
    if not events:
        return _empty_metrics(skill_id)
    
    total = len(events)
    successes = sum(1 for e in events if e.get("result") == "SUCCESS")
    failures = sum(1 for e in events if e.get("result") in ("FAILED", "CONTEXT_LOAD_FAILED"))
    durations = [e.get("duration_ms", 0) for e in events if e.get("duration_ms")]
    retries = sum(1 for e in events if e.get("retry_count", 0) > 0)
    
    durations.sort()
    p95_idx = int(len(durations) * 0.95) if durations else 0
    
    return {
        "skill_id": skill_id,
        "window_hours": window_hours,
        "execution_count": total,
        "success_count": successes,
        "failure_count": failures,
        "success_rate": round(successes / total * 100, 1) if total else 100.0,
        "failure_rate": round(failures / total * 100, 1) if total else 0.0,
        "avg_latency_ms": round(sum(durations) / len(durations), 1) if durations else 0,
        "p95_latency_ms": durations[p95_idx] if durations and p95_idx < len(durations) else 0,
        "retry_rate": round(retries / total * 100, 1) if total else 0.0,
        "dependency_failure_rate": 0.0,
        "total_events_analyzed": total
    }

def aggregate_namespace(ns_prefix: str = "") -> dict:
    """Aggregate metrics across namespace."""
    all_events = query_events(limit=5000)
    ns_events = [e for e in all_events if e.get("namespace", "").startswith(ns_prefix)] if ns_prefix else all_events
    
    total = len(ns_events)
    successes = sum(1 for e in ns_events if e.get("result") == "SUCCESS")
    
    return {
        "namespace": ns_prefix or "all",
        "total_executions": total,
        "success_rate": round(successes / total * 100, 1) if total else 100.0,
        "skills_tracked": len(set(e.get("skill_id") for e in ns_events))
    }

def generate_snapshot() -> dict:
    return {
        "system": aggregate_namespace(""),
        "core": aggregate_namespace("hermes.core"),
        "adapter": aggregate_namespace("adapter"),
        "project": aggregate_namespace("project"),
        "timestamp": __import__('time').strftime("%Y-%m-%dT%H:%M:%SZ", __import__('time').gmtime())
    }

def _empty_metrics(skill_id: str) -> dict:
    return {"skill_id": skill_id, "execution_count": 0, "success_rate": 100.0,
            "failure_rate": 0.0, "avg_latency_ms": 0, "p95_latency_ms": 0}
