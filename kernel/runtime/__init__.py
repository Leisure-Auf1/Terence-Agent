"""B.6.2 — Runtime: context manager, permission gate, executor, rollback."""
from .context_manager import load_context, release_context, use_context, get_active_contexts
from .permission_gate import check_permission, REQUIREMENTS
from .executor import execute_skill
from .rollback_manager import rollback_context, rollback_state, save_rollback_snapshot

__version__ = "0.1.0"
__phase__ = "B.6.2"
