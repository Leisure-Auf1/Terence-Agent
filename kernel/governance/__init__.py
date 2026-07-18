"""B.6.4 — Governance Loop Runtime."""
from .proposal_engine import generate, generate_from_health, generate_from_trigger, PROPOSAL_TYPES
from .proposal_store import create as store_create, get, list_all, update_status, validate_integrity
from .approval_manager import submit_for_approval, approve, reject, is_auto_allowed, is_auto_forbidden
from .action_tracker import create_action, update_result, get_history
from .governance_rules import RULES, is_destructive, requires_approval, validate_action, assert_no_bypass
__version__ = "0.1.0"
__phase__ = "B.6.4"
