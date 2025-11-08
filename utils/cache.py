#!/usr/bin/env python3
"""
Caching system for API responses and AI results
Reduces API costs and improves performance
"""

import json
import hashlib
import time
from typing import Optional, Any, Dict
from pathlib import Path
from functools import wraps
from utils.logger import get_logger

logger = get_logger('cache')

class Cache:
    """Simple file-based cache with TTL"""
    
    def __init__(self, cache_dir: str = "cache", default_ttl: int = 3600):
        """
        Initialize cache
        
        Args:
            cache_dir: Directory for cache files
            default_ttl: Default time-to-live in seconds (1 hour)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.default_ttl = default_ttl
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0
        }
    
    def _get_key_path(self, key: str) -> Path:
        """Get file path for cache key"""
        # Hash key to avoid filesystem issues
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"
    
    def get(self, key: str, ttl: Optional[int] = None) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            ttl: Override default TTL
        
        Returns:
            Cached value or None if not found/expired
        """
        ttl = ttl or self.default_ttl
        cache_file = self._get_key_path(key)
        
        if not cache_file.exists():
            self._stats['misses'] += 1
            return None
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            # Check expiration
            if time.time() - data['timestamp'] > ttl:
                cache_file.unlink()  # Delete expired cache
                self._stats['misses'] += 1
                return None
            
            self._stats['hits'] += 1
            return data['value']
        except Exception as e:
            logger.warning(f"Cache read error for {key}: {e}")
            self._stats['misses'] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Override default TTL
        """
        try:
            cache_file = self._get_key_path(key)
            data = {
                'timestamp': time.time(),
                'value': value
            }
            
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            
            self._stats['sets'] += 1
        except Exception as e:
            logger.warning(f"Cache write error for {key}: {e}")
    
    def delete(self, key: str):
        """Delete cache entry"""
        cache_file = self._get_key_path(key)
        if cache_file.exists():
            cache_file.unlink()
    
    def clear(self):
        """Clear all cache entries"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total = self._stats['hits'] + self._stats['misses']
        hit_rate = (self._stats['hits'] / total * 100) if total > 0 else 0
        
        return {
            **self._stats,
            'hit_rate': round(hit_rate, 2),
            'total_requests': total
        }

# Global cache instance
_cache = None

def get_cache() -> Cache:
    """Get cache instance"""
    global _cache
    if _cache is None:
        _cache = Cache()
    return _cache

def cached(key_prefix: str, ttl: int = 3600):
    """
    Decorator to cache function results
    
    Args:
        key_prefix: Prefix for cache key
        ttl: Time-to-live in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)
            
            cache = get_cache()
            cached_value = cache.get(cache_key, ttl=ttl)
            
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)
            logger.debug(f"Cache miss: {cache_key}")
            
            return result
        return wrapper
    return decorator






