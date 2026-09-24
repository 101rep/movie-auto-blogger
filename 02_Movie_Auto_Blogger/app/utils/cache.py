"""Lightweight in-memory TTL (Time-To-Live) cache for high-speed dashboard and service queries."""
import time
from typing import Any, Callable, Dict, Optional, Tuple


class TTLCache:
    """Thread-safe and simple in-memory key-value cache with TTL expiration."""

    def __init__(self, default_ttl: float = 300.0):
        self.default_ttl = default_ttl
        self._store: Dict[str, Tuple[Any, float]] = {}

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value if exists and not expired, otherwise None."""
        if key not in self._store:
            return None
        val, expiry = self._store[key]
        if time.time() > expiry:
            del self._store[key]
            return None
        return val

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Store value with custom or default TTL in seconds."""
        expiry = time.time() + (ttl if ttl is not None else self.default_ttl)
        self._store[key] = (value, expiry)

    def delete(self, key: str) -> None:
        """Delete specific key from cache."""
        self._store.pop(key, None)

    def clear(self) -> None:
        """Clear all entries."""
        self._store.clear()


# Global cache instance
global_cache = TTLCache(default_ttl=300.0)  # 5 minutes default
