"""
Redis caching layer for improved performance.

Caches expensive operations like scraping and complex queries.
"""
from __future__ import annotations

import json
import os
from typing import Optional, Any
from functools import wraps

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
CACHE_TTL = int(os.getenv("CACHE_TTL", 3600))  # 1 hour default

# Initialize Redis client if available
if REDIS_AVAILABLE:
    try:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=2
        )
        redis_client.ping()
        print("[Cache] Redis connected successfully")
    except (redis.ConnectionError, redis.TimeoutError):
        redis_client = None
        print("[Cache] Redis not available, using in-memory fallback")
else:
    redis_client = None
    print("[Cache] Redis module not installed, caching disabled")

# Fallback in-memory cache
_memory_cache: dict[str, tuple[Any, float]] = {}


def get_cache(key: str) -> Optional[Any]:
    """Get value from cache."""
    if redis_client:
        try:
            value = redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            print(f"[Cache] Redis get error: {e}")
            return None
    else:
        # Use in-memory fallback
        import time
        if key in _memory_cache:
            value, expires_at = _memory_cache[key]
            if time.time() < expires_at:
                return value
            else:
                del _memory_cache[key]
        return None


def set_cache(key: str, value: Any, ttl: int = CACHE_TTL) -> bool:
    """Set value in cache with TTL."""
    if redis_client:
        try:
            redis_client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            print(f"[Cache] Redis set error: {e}")
            return False
    else:
        # Use in-memory fallback
        import time
        _memory_cache[key] = (value, time.time() + ttl)
        return True


def delete_cache(key: str) -> bool:
    """Delete value from cache."""
    if redis_client:
        try:
            redis_client.delete(key)
            return True
        except Exception as e:
            print(f"[Cache] Redis delete error: {e}")
            return False
    else:
        if key in _memory_cache:
            del _memory_cache[key]
        return True


def clear_cache() -> bool:
    """Clear all cache."""
    if redis_client:
        try:
            redis_client.flushdb()
            return True
        except Exception as e:
            print(f"[Cache] Redis flush error: {e}")
            return False
    else:
        _memory_cache.clear()
        return True


def cache_result(ttl: int = CACHE_TTL, key_prefix: str = ""):
    """
    Decorator to cache function results.

    Usage:
        @cache_result(ttl=3600, key_prefix="plans")
        def get_plans(...):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [key_prefix or func.__name__]
            if args:
                key_parts.extend(str(arg) for arg in args)
            if kwargs:
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)

            # Try to get from cache
            cached = get_cache(cache_key)
            if cached is not None:
                print(f"[Cache] HIT: {cache_key}")
                return cached

            # Execute function and cache result
            print(f"[Cache] MISS: {cache_key}")
            result = func(*args, **kwargs)
            set_cache(cache_key, result, ttl)
            return result

        return wrapper
    return decorator
