"""
Cache Service for Legal Dashboard
================================

Provides Redis-based caching for OCR results, search queries, and other frequently accessed data.
"""

import os
import json
import logging
import hashlib
from typing import Optional, Any, Dict, List
from datetime import datetime, timedelta
import redis
from functools import wraps

logger = logging.getLogger(__name__)


class CacheService:
    """Redis-based caching service for performance optimization"""

    def __init__(self):
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
        self.redis_db = int(os.getenv("REDIS_DB", "0"))
        self.redis_password = os.getenv("REDIS_PASSWORD")

        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                password=self.redis_password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("✅ Redis cache service initialized successfully")
        except Exception as e:
            logger.warning(
                f"⚠️ Redis connection failed: {e}. Using in-memory fallback.")
            self.redis_client = None
            self._fallback_cache = {}

    def _get_cache_key(self, prefix: str, identifier: str) -> str:
        """Generate a cache key"""
        return f"legal_dashboard:{prefix}:{identifier}"

    def _hash_content(self, content: str) -> str:
        """Generate hash for content-based caching"""
        return hashlib.md5(content.encode()).hexdigest()

    def set(self, key: str, value: Any, expire_seconds: int = 3600) -> bool:
        """Set a cache value"""
        try:
            if self.redis_client:
                serialized_value = json.dumps(value, default=str)
                return self.redis_client.setex(key, expire_seconds, serialized_value)
            else:
                # Fallback to in-memory cache
                self._fallback_cache[key] = {
                    'value': value,
                    'expires_at': datetime.utcnow() + timedelta(seconds=expire_seconds)
                }
                return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """Get a cache value"""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                return json.loads(value) if value else None
            else:
                # Fallback to in-memory cache
                cache_entry = self._fallback_cache.get(key)
                if cache_entry and datetime.utcnow() < cache_entry['expires_at']:
                    return cache_entry['value']
                elif cache_entry:
                    # Remove expired entry
                    del self._fallback_cache[key]
                return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete a cache value"""
        try:
            if self.redis_client:
                return bool(self.redis_client.delete(key))
            else:
                self._fallback_cache.pop(key, None)
                return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if a key exists"""
        try:
            if self.redis_client:
                return bool(self.redis_client.exists(key))
            else:
                cache_entry = self._fallback_cache.get(key)
                return cache_entry is not None and datetime.utcnow() < cache_entry['expires_at']
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False

    def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for a key"""
        try:
            if self.redis_client:
                return bool(self.redis_client.expire(key, seconds))
            else:
                cache_entry = self._fallback_cache.get(key)
                if cache_entry:
                    cache_entry['expires_at'] = datetime.utcnow() + \
                        timedelta(seconds=seconds)
                return True
        except Exception as e:
            logger.error(f"Cache expire error: {e}")
            return False

    # OCR-specific caching methods
    def cache_ocr_result(self, file_hash: str, ocr_result: Dict[str, Any], expire_seconds: int = 86400) -> bool:
        """Cache OCR result for a file"""
        key = self._get_cache_key("ocr_result", file_hash)
        return self.set(key, ocr_result, expire_seconds)

    def get_cached_ocr_result(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached OCR result for a file"""
        key = self._get_cache_key("ocr_result", file_hash)
        return self.get(key)

    def cache_search_result(self, query_hash: str, search_result: List[Dict[str, Any]], expire_seconds: int = 1800) -> bool:
        """Cache search result for a query"""
        key = self._get_cache_key("search_result", query_hash)
        return self.set(key, search_result, expire_seconds)

    def get_cached_search_result(self, query_hash: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached search result for a query"""
        key = self._get_cache_key("search_result", query_hash)
        return self.get(key)

    # Analytics caching
    def cache_analytics(self, analytics_type: str, data: Dict[str, Any], expire_seconds: int = 3600) -> bool:
        """Cache analytics data"""
        key = self._get_cache_key("analytics", analytics_type)
        return self.set(key, data, expire_seconds)

    def get_cached_analytics(self, analytics_type: str) -> Optional[Dict[str, Any]]:
        """Get cached analytics data"""
        key = self._get_cache_key("analytics", analytics_type)
        return self.get(key)

    # User session caching
    def cache_user_session(self, user_id: int, session_data: Dict[str, Any], expire_seconds: int = 1800) -> bool:
        """Cache user session data"""
        key = self._get_cache_key("user_session", str(user_id))
        return self.set(key, session_data, expire_seconds)

    def get_user_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get cached user session data"""
        key = self._get_cache_key("user_session", str(user_id))
        return self.get(key)

    # Cache statistics
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            if self.redis_client:
                info = self.redis_client.info()
                return {
                    'connected_clients': info.get('connected_clients', 0),
                    'used_memory_human': info.get('used_memory_human', '0B'),
                    'total_commands_processed': info.get('total_commands_processed', 0),
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0),
                    'hit_rate': info.get('keyspace_hits', 0) / max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0), 1) * 100
                }
            else:
                return {
                    'connected_clients': 0,
                    'used_memory_human': '0B',
                    'total_commands_processed': 0,
                    'keyspace_hits': 0,
                    'keyspace_misses': 0,
                    'hit_rate': 0,
                    'fallback_mode': True,
                    'fallback_entries': len(self._fallback_cache)
                }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {}

    # Cache cleanup
    def cleanup_expired(self) -> int:
        """Clean up expired cache entries (for fallback mode)"""
        if not self.redis_client:
            expired_keys = []
            for key, entry in self._fallback_cache.items():
                if datetime.utcnow() >= entry['expires_at']:
                    expired_keys.append(key)

            for key in expired_keys:
                del self._fallback_cache[key]

            return len(expired_keys)
        return 0


# Global cache instance
cache_service = CacheService()

# Decorator for caching function results


def cache_result(prefix: str, expire_seconds: int = 3600, key_func=None):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Use function name and arguments as key
                key_parts = [func.__name__] + [str(arg) for arg in args] + [
                    f"{k}={v}" for k, v in sorted(kwargs.items())]
                cache_key = hashlib.md5(
                    ":".join(key_parts).encode()).hexdigest()

            full_key = cache_service._get_cache_key(prefix, cache_key)

            # Try to get from cache
            cached_result = cache_service.get(full_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache_service.set(full_key, result, expire_seconds)
            logger.debug(f"Cache miss for {func.__name__}, cached result")

            return result
        return wrapper
    return decorator
