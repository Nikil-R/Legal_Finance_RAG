"""
Caching Layer for Tool Results

Improves performance by caching expensive tool results while maintaining
data freshness and compliance requirements.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, TypeVar, cast
import json
import hashlib
import threading
from pathlib import Path

T = TypeVar('T')

class CacheEntry:
    """Single cache entry with metadata"""
    
    def __init__(self, data: Any, ttl_seconds: Optional[int] = None):
        """
        Initialize cache entry
        
        Args:
            data: Data to cache
            ttl_seconds: Time-to-live in seconds, None for never expire
        """
        self.data = data
        self.created_at = datetime.now()
        self.ttl_seconds = ttl_seconds
        self.access_count = 0
        self.last_accessed = datetime.now()
    
    def is_expired(self) -> bool:
        """Check if entry has expired"""
        if self.ttl_seconds is None:
            return False
        
        age_seconds = (datetime.now() - self.created_at).total_seconds()
        return age_seconds > self.ttl_seconds
    
    def access(self) -> Any:
        """Record access and return data"""
        self.last_accessed = datetime.now()
        self.access_count += 1
        return self.data
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get cache entry metadata"""
        return {
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
            "ttl_seconds": self.ttl_seconds,
            "expired": self.is_expired(),
            "age_seconds": (datetime.now() - self.created_at).total_seconds()
        }


class CachePolicy:
    """Cache policy configuration"""
    
    # Default TTLs for different data types
    IMMUTABLE_DATA_TTL = None  # Court cases don't change (until court overrules)
    REGULATORY_DATA_TTL = 86400 * 30  # 30 days for regulatory data
    CALCULATION_RESULT_TTL = 3600 * 24  # 24 hours for calculations
    SEARCH_RESULT_TTL = 3600  # 1 hour for search results
    
    # Cache sizes (max entries before eviction)
    MAX_CACHE_SIZE = 1000
    EVICTION_STRATEGY = "lru"  # least-recently-used


class ToolResultCache:
    """
    Thread-safe cache for tool results
    
    Features:
    - Per-tool caching with configurable TTLs
    - LRU eviction when cache fills
    - Cache statistics and monitoring
    - Compliance-aware caching (skips sensitive results)
    - Export/import for backup
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize cache
        
        Args:
            cache_dir: Directory for persistent cache storage
        """
        self.cache: Dict[str, CacheEntry] = {}
        self.lock = threading.RLock()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }
        
        self.cache_dir = Path(cache_dir or "app/cache") if cache_dir else None
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found/expired
        """
        
        with self.lock:
            if key not in self.cache:
                self.stats["misses"] += 1
                return None
            
            entry = self.cache[key]
            
            if entry.is_expired():
                del self.cache[key]
                self.stats["misses"] += 1
                return None
            
            self.stats["hits"] += 1
            return entry.access()
    
    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        tool_name: Optional[str] = None
    ):
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time-to-live (uses tool defaults if None)
            tool_name: Tool name (for policy application)
        """
        
        # Don't cache sensitive result types
        if self._should_skip_cache(value):
            return
        
        # Use tool-specific TTL if not provided
        if ttl_seconds is None:
            ttl_seconds = self._get_default_ttl(tool_name)
        
        with self.lock:
            # Check if cache is full
            if len(self.cache) >= CachePolicy.MAX_CACHE_SIZE:
                self._evict_entry()
            
            self.cache[key] = CacheEntry(value, ttl_seconds)
    
    def delete(self, key: str):
        """Remove entry from cache"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
    
    def clear(self):
        """Clear entire cache"""
        with self.lock:
            self.cache.clear()
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries. Returns count of entries removed"""
        
        with self.lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self.cache[key]
            
            return len(expired_keys)
    
    def get_cache_key(
        self,
        tool_name: str,
        **parameters
    ) -> str:
        """
        Generate cache key from tool name and parameters
        
        Args:
            tool_name: Name of tool
            **parameters: Tool parameters
        
        Returns:
            Cache key
        """
        
        # Create deterministic key from tool name and params
        param_str = json.dumps(parameters, sort_keys=True, default=str)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
        
        return f"{tool_name}:{param_hash}"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        
        with self.lock:
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = (
                self.stats["hits"] / total_requests * 100
                if total_requests > 0 else 0
            )
            
            return {
                "size": len(self.cache),
                "max_size": CachePolicy.MAX_CACHE_SIZE,
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "evictions": self.stats["evictions"],
                "hit_rate": round(hit_rate, 2),
                "total_requests": total_requests
            }
    
    def get_entries_info(self, limit: int = 10) -> Dict[str, Any]:
        """Get info about cached entries"""
        
        with self.lock:
            # Sort by last accessed (most recent first)
            sorted_entries = sorted(
                self.cache.items(),
                key=lambda x: x[1].last_accessed,
                reverse=True
            )
            
            entries_info = []
            for key, entry in sorted_entries[:limit]:
                entries_info.append({
                    "key": key,
                    "metadata": entry.get_metadata()
                })
            
            return {
                "total_entries": len(self.cache),
                "recent_entries": entries_info
            }
    
    def invalidate_by_tool(self, tool_name: str):
        """Invalidate all cache entries for a specific tool"""
        
        with self.lock:
            keys_to_delete = [
                key for key in self.cache.keys()
                if key.startswith(tool_name + ":")
            ]
            
            for key in keys_to_delete:
                del self.cache[key]
            
            return len(keys_to_delete)
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern"""
        
        with self.lock:
            keys_to_delete = [
                key for key in self.cache.keys()
                if pattern in key
            ]
            
            for key in keys_to_delete:
                del self.cache[key]
            
            return len(keys_to_delete)
    
    def warmup_cache(self, preload_data: Dict[str, Any]):
        """Warm up cache with pre-computed data"""
        
        with self.lock:
            for key, value in preload_data.items():
                self.set(key, value)
    
    def export_cache(self, output_file: str) -> str:
        """Export cache to JSON file for backup"""
        
        with self.lock:
            export_data = {}
            
            for key, entry in self.cache.items():
                if not entry.is_expired():
                    export_data[key] = {
                        "data": entry.data,
                        "metadata": entry.get_metadata()
                    }
            
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            return str(output_path)
    
    def import_cache(self, input_file: str):
        """Import cache from JSON file"""
        
        input_path = Path(input_file)
        if not input_path.exists():
            return
        
        with open(input_path, 'r') as f:
            import_data = json.load(f)
        
        with self.lock:
            for key, value in import_data.items():
                self.cache[key] = CacheEntry(value["data"])
    
    @staticmethod
    def _should_skip_cache(value: Any) -> bool:
        """Check if value should not be cached (e.g., errors, empty results)"""
        
        if value is None:
            return True
        
        if isinstance(value, dict):
            # Don't cache error responses
            if "error" in value or "exception" in value:
                return True
            
            # Don't cache empty results
            if not value:
                return True
        
        return False
    
    @staticmethod
    def _get_default_ttl(tool_name: Optional[str]) -> Optional[int]:
        """Get default TTL for tool"""
        
        if not tool_name:
            return CachePolicy.CALCULATION_RESULT_TTL
        
        if tool_name == "search_court_cases":
            return CachePolicy.IMMUTABLE_DATA_TTL
        elif tool_name == "check_compliance":
            return CachePolicy.REGULATORY_DATA_TTL
        elif tool_name == "calculate_financial_ratios":
            return CachePolicy.CALCULATION_RESULT_TTL
        else:
            return CachePolicy.CALCULATION_RESULT_TTL
    
    def _evict_entry(self):
        """Evict least-recently-used entry"""
        
        if not self.cache:
            return
        
        # Find LRU entry
        lru_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k].last_accessed
        )
        
        del self.cache[lru_key]
        self.stats["evictions"] += 1


class CachedToolDecorator:
    """Decorator to add caching to tool functions"""
    
    def __init__(self, cache: ToolResultCache, ttl_seconds: Optional[int] = None):
        """
        Initialize decorator
        
        Args:
            cache: Cache instance to use
            ttl_seconds: Cache TTL
        """
        self.cache = cache
        self.ttl_seconds = ttl_seconds
    
    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """Wrap function with caching"""
        
        def wrapper(*args, **kwargs) -> T:
            # Generate cache key
            cache_key = self.cache.get_cache_key(func.__name__, **kwargs)
            
            # Try to get from cache
            cached_value = self.cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            self.cache.set(cache_key, result, self.ttl_seconds, func.__name__)
            
            return result
        
        return wrapper


# Global cache instance
_tool_cache: Optional[ToolResultCache] = None


def get_tool_cache() -> ToolResultCache:
    """Get global tool result cache"""
    global _tool_cache
    if _tool_cache is None:
        _tool_cache = ToolResultCache()
    return _tool_cache


def cached_tool_result(ttl_seconds: Optional[int] = None):
    """Decorator for caching tool results"""
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        cache = get_tool_cache()
        return CachedToolDecorator(cache, ttl_seconds)(func)
    
    return decorator
