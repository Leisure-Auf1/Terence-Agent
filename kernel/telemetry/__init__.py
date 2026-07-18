"""B.6.3 — Telemetry Runtime."""
from .collector import collect, validate_schema
from .event_store import append_event, query_events, count_events, validate_integrity
from .metrics_aggregator import aggregate_skill, aggregate_namespace, generate_snapshot
__version__ = "0.1.0"
__phase__ = "B.6.3"
