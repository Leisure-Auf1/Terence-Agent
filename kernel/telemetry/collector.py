"""B.6.3 — Telemetry Collector: execution record from executor output."""

import time, json, os

def collect(exec_result: dict, skill_namespace: str = "", caller_scope: str = "") -> dict:
    """Build ExecutionRecord from executor output. Strips all PII/content."""
    record = {
        "execution_id": exec_result.get("execution_id", f"exec-{int(time.time())}"),
        "skill_id": exec_result.get("skill_id", "unknown"),
        "namespace": skill_namespace,
        "caller_scope": caller_scope,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "duration_ms": exec_result.get("duration_ms", 0),
        "result": exec_result.get("status", "UNKNOWN"),
        "error_type": exec_result.get("error_class"),
        "error_message": exec_result.get("error", "").split("\n")[0] if exec_result.get("error") else None,
        "retry_count": len([s for s in exec_result.get("log", {}).get("stages", []) if s.get("stage")=="execution"]) - 1,
        "dependency_status": {},
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "body_truncated": True
    }
    return record

def validate_schema(record: dict) -> bool:
    """Validate record has all required fields."""
    required = ["execution_id", "skill_id", "result", "timestamp"]
    return all(k in record and record[k] for k in required)

def collect_batch(exec_results: list) -> list:
    return [collect(r) for r in exec_results]
