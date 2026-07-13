"""
Veritas_Core — StorageBackend: Memory Persistence Abstraction.

Abstract interface for memory storage backends:
  - MemoryStorage: In-memory dicts (MVP)
  - Future: RedisStorage, PostgreSQLStorage

Allows swapping storage backend without changing MemoryManager logic.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class StorageBackend(ABC):
    """Abstract storage backend interface.

    Implementations:
        MemoryStorage  — In-memory dicts (MVP, zero dependencies)
        RedisStorage   — Redis for conversation + session (future)
        PostgreSQLStorage — PostgreSQL for profile + history (future)
    """

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value by key."""
        ...

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Store a value by key."""
        ...

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a key. Returns True if key existed."""
        ...

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if a key exists."""
        ...

    @abstractmethod
    def keys(self, pattern: str = "*") -> List[str]:
        """List keys matching a pattern."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Remove all data."""
        ...


class MemoryStorage(StorageBackend):
    """In-memory dict-based storage — suitable for MVP and testing.

    No external dependencies. All data is lost on process exit.
    """

    def __init__(self):
        self._store: Dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        return self._store.get(key)

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value

    def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            return True
        return False

    def exists(self, key: str) -> bool:
        return key in self._store

    def keys(self, pattern: str = "*") -> List[str]:
        # Simple prefix matching (no glob support in MVP)
        if pattern == "*":
            return list(self._store.keys())
        prefix = pattern.rstrip("*")
        return [k for k in self._store if k.startswith(prefix)]

    def clear(self) -> None:
        self._store.clear()

    def __len__(self) -> int:
        return len(self._store)


# ── Future backends (placeholder interfaces) ──


class RedisStorage(StorageBackend):
    """Redis-based storage for conversation + session context.

    Planned for Phase 5: FastAPI + Deployment.
    Features: TTL support, pub/sub, clustering.
    """

    def __init__(self, url: str = "redis://localhost:6379"):
        self._url = url

    def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError("RedisStorage — planned for Phase 5")

    def set(self, key: str, value: Any) -> None:
        raise NotImplementedError("RedisStorage — planned for Phase 5")

    def delete(self, key: str) -> bool:
        raise NotImplementedError("RedisStorage — planned for Phase 5")

    def exists(self, key: str) -> bool:
        raise NotImplementedError("RedisStorage — planned for Phase 5")

    def keys(self, pattern: str = "*") -> List[str]:
        raise NotImplementedError("RedisStorage — planned for Phase 5")

    def clear(self) -> None:
        raise NotImplementedError("RedisStorage — planned for Phase 5")


class PostgreSQLStorage(StorageBackend):
    """PostgreSQL-based storage for profile + history memory.

    Planned for Phase 5: FastAPI + Deployment.
    Features: ACID transactions, pgvector extension, JSONB columns.
    """

    def __init__(self, dsn: str = "postgresql://localhost:5432/veritas"):
        self._dsn = dsn

    def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError("PostgreSQLStorage — planned for Phase 5")

    def set(self, key: str, value: Any) -> None:
        raise NotImplementedError("PostgreSQLStorage — planned for Phase 5")

    def delete(self, key: str) -> bool:
        raise NotImplementedError("PostgreSQLStorage — planned for Phase 5")

    def exists(self, key: str) -> bool:
        raise NotImplementedError("PostgreSQLStorage — planned for Phase 5")

    def keys(self, pattern: str = "*") -> List[str]:
        raise NotImplementedError("PostgreSQLStorage — planned for Phase 5")

    def clear(self) -> None:
        raise NotImplementedError("PostgreSQLStorage — planned for Phase 5")
