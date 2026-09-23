import time
import threading
from typing import Any, Optional, Dict, Callable
from functools import wraps

class SimpleTTLCache:
    """Thread-safe in-memory cache with Time-To-Live (TTL) expiration."""
    def __init__(self, default_ttl: int = 300):
        self.default_ttl = default_ttl
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            item = self._store.get(key)
            if not item:
                return None
            if time.time() > item["expires_at"]:
                del self._store[key]
                return None
            return item["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        duration = ttl if ttl is not None else self.default_ttl
        with self._lock:
            self._store[key] = {
                "value": value,
                "expires_at": time.time() + duration
            }

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._store:
                del self._store[key]
                return True
            return False

    def clear_prefix(self, prefix: str) -> int:
        with self._lock:
            keys_to_del = [k for k in self._store if k.startswith(prefix)]
            for k in keys_to_del:
                del self._store[k]
            return len(keys_to_del)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

app_cache = SimpleTTLCache(default_ttl=300)
