"""B.6.3 — Health Runtime."""
from .health_engine import calculate_score, evaluate, get_state, is_deterministic
from .degradation_manager import handle_warning, handle_degraded, handle_failed, assert_no_destructive_action
from .quarantine_manager import quarantine, is_quarantined
from .recovery_manager import retry, fallback, rollback, create_recovery_record
__version__ = "0.1.0"
__phase__ = "B.6.3"
