"""B.6.2 — Lifecycle Runtime: 13-state machine with transition guard and audit log."""
from .state_machine import is_transition_allowed, get_allowed_transitions, get_state_graph
from .transition_guard import guard_transition
from .state_logger import log_transition, get_transition_history

__version__ = "0.1.0"
__phase__ = "B.6.2"
