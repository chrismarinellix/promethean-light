"""Simple in-memory cache for API responses"""

import time
from typing import Optional, Any, Dict
from functools import wraps


class SimpleCache:
    """Simple TTL-based cache"""

    def __init__(self, ttl_seconds: int = 300):
        self.cache: Dict[str, Dict] = {}
        self.ttl = ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired"""
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl:
                return entry['value']
            else:
                # Expired, remove it
                del self.cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """Set cache value"""
        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }

    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()

    def invalidate(self, key: str) -> None:
        """Invalidate specific key"""
        if key in self.cache:
            del self.cache[key]


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
