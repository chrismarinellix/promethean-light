"""Simple in-memory cache for API responses with LRU eviction"""

import time
from typing import Optional, Any, Dict, OrderedDict
from functools import wraps
from collections import OrderedDict


class SimpleCache:
    """TTL-based cache with LRU eviction and max size"""

    def __init__(self, ttl_seconds: int = 300, max_size: int = 1000):
        self.cache: OrderedDict[str, Dict] = OrderedDict()
        self.ttl = ttl_seconds
        self.max_size = max_size

    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired (LRU: move to end)"""
        if key in self.cache:
            entry = self.cache[key]
            # Use per-item TTL if set, otherwise default TTL
            item_ttl = entry.get('ttl', self.ttl)
            if time.time() - entry['timestamp'] < item_ttl:
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                return entry['value']
            else:
                # Expired, remove it
                del self.cache[key]
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set cache value with LRU eviction and optional per-item TTL"""
        # Remove if exists (to update position)
        if key in self.cache:
            del self.cache[key]

        # Add new entry
        self.cache[key] = {
            'value': value,
            'timestamp': time.time(),
            'ttl': ttl if ttl is not None else self.ttl
        }

        # Evict oldest if over max size (FIFO/LRU)
        while len(self.cache) > self.max_size:
            self.cache.popitem(last=False)  # Remove oldest (first item)

    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()

    def invalidate(self, key: str) -> None:
        """Invalidate specific key"""
        if key in self.cache:
            del self.cache[key]

    def size(self) -> int:
        """Get current cache size"""
        return len(self.cache)


# Global cache instance
_cache = SimpleCache(ttl_seconds=300)  # 5 minute TTL


def cached(key_prefix: str = ""):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key
            cache_key = f"{key_prefix}:{str(args)}:{str(kwargs)}"

            # Check cache
            cached_value = _cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Call function
            result = await func(*args, **kwargs)

            # Cache result
            _cache.set(cache_key, result)

            return result
        return wrapper
    return decorator


def get_cache() -> SimpleCache:
    """Get global cache instance"""
    return _cache
