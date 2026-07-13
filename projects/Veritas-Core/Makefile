.PHONY: test run clean

# Run all tests
test:
	PYTHONPATH=src:$$PYTHONPATH python -m pytest tests/ -v

# Run demo pipeline
run:
	PYTHONPATH=src:$$PYTHONPATH python -c "\
from agents.base import AgentContext; \
from agents.profile_agent import ProfileAgent; \
from agents.planner_agent import PlannerAgent; \
from memory.manager import MemoryManager; \
from providers.mock import MockLLMProvider; \
ctx = AgentContext(session_id='demo', student_id='demo-001', llm_provider=MockLLMProvider(), memory_manager=MemoryManager()); \
print('Veritas-Core runtime ready.')"

# Clean temporary files
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache
