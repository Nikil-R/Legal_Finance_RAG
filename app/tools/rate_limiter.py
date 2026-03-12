"""
Rate Limiting and Quota Management System

Prevents tool abuse and ensures fair resource allocation.
Supports per-user quotas, time-based windows, and tool-specific limits.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from collections import defaultdict
import threading
from enum import Enum

class QuotaWindow(Enum):
    """Time window for rate limiting"""
    PER_MINUTE = "per_minute"
    PER_HOUR = "per_hour"
    PER_DAY = "per_day"

class RateLimitConfig:
    """Configuration for rate limiting"""
    
    # Default quotas per time window
    DEFAULT_QUOTAS = {
        QuotaWindow.PER_MINUTE: 10,
        QuotaWindow.PER_HOUR: 100,
        QuotaWindow.PER_DAY: 500
    }
    
    # Tool-specific limits (more restrictive for expensive tools)
    TOOL_SPECIFIC_LIMITS = {
        "calculate_financial_ratios": {
            QuotaWindow.PER_MINUTE: 5,
            QuotaWindow.PER_HOUR: 50,
            QuotaWindow.PER_DAY: 300
        },
        "document_comparison": {
            QuotaWindow.PER_MINUTE: 3,
            QuotaWindow.PER_HOUR: 30,
            QuotaWindow.PER_DAY: 200
        },
        "search_court_cases": {
            QuotaWindow.PER_MINUTE: 10,
            QuotaWindow.PER_HOUR: 100,
            QuotaWindow.PER_DAY: 500
        }
    }
    
    # Special VIP quotas (for staff/internal use)
    VIP_QUOTAS = {
        QuotaWindow.PER_MINUTE: 100,
        QuotaWindow.PER_HOUR: 1000,
        QuotaWindow.PER_DAY: 10000
    }


class RateLimiter:
    """
    Rate limiter with configurable quotas and time windows
    
    Thread-safe implementation for production environments.
    """
    
    def __init__(self):
        self.lock = threading.RLock()
        self.usage: Dict[str, Dict[str, list]] = defaultdict(
            lambda: defaultdict(list)
        )  # user_id -> window -> timestamps
    
    def is_allowed(
        self,
        user_id: str,
        tool_name: str = None,
        is_vip: bool = False
    ) -> Tuple[bool, Dict[str, any]]:
        """
        Check if user is allowed to invoke tool
        
        Args:
            user_id: Unique user identifier
            tool_name: Name of tool being invoked
            is_vip: Whether user has VIP status
        
        Returns:
            Tuple of (allowed: bool, info: Dict with quota details)
        """
        
        with self.lock:
            now = datetime.now()
            
            # Get quota limits for this tool
            if is_vip:
                limits = RateLimitConfig.VIP_QUOTAS
            else:
                limits = RateLimitConfig.TOOL_SPECIFIC_LIMITS.get(
                    tool_name,
                    RateLimitConfig.DEFAULT_QUOTAS
                )
            
            # Check each time window
            for window, limit in limits.items():
                window_key = f"{window.value}"
                
                # Remove old entries outside this window
                cutoff_time = self._get_window_start(now, window)
                current_usage = self._get_usage_in_window(
                    user_id, window_key, cutoff_time
                )
                
                # Check if limit exceeded
                if current_usage >= limit:
                    return False, {
                        "blocked_by": window.value,
                        "current_usage": current_usage,
                        "limit": limit,
                        "resets_at": self._get_window_reset_time(now, window).isoformat(),
                        "requests_remaining": 0
                    }
            
            # Record this usage
            self.usage[user_id]["all_calls"].append(now)
            if tool_name:
                self.usage[user_id][f"tool:{tool_name}"].append(now)
            
            # Return success with quota info
            return True, {
                "status": "allowed",
                "next_check": (now + timedelta(seconds=1)).isoformat()
            }
    
    def get_usage_summary(self, user_id: str, tool_name: Optional[str] = None) -> Dict[str, any]:
        """Get current usage summary for user/tool combination"""
        
        with self.lock:
            now = datetime.now()
            limits = RateLimitConfig.DEFAULT_QUOTAS
            
            summary = {
                "user_id": user_id,
                "tool": tool_name or "all_tools",
                "usage_by_window": {},
                "quotas": {}
            }
            
            for window, limit in limits.items():
                window_key = f"{window.value}"
                cutoff_time = self._get_window_start(now, window)
                
                current_usage = self._get_usage_in_window(
                    user_id, window_key, cutoff_time
                )
                
                summary["usage_by_window"][window.value] = {
                    "current": current_usage,
                    "limit": limit,
                    "remaining": max(0, limit - current_usage),
                    "percentage_used": round((current_usage / limit) * 100, 1),
                    "resets_at": self._get_window_reset_time(now, window).isoformat()
                }
                
                summary["quotas"][window.value] = limit
            
            return summary
    
    def reset_user_quota(self, user_id: str):
        """Reset quota for a user (admin action)"""
        with self.lock:
            if user_id in self.usage:
                self.usage[user_id].clear()
    
    def set_custom_limit(
        self,
        user_id: str,
        tool_name: str,
        window: QuotaWindow,
        limit: int
    ):
        """Set custom limit for user/tool combination (admin action)"""
        # Implementation would store custom limits separately
        # For now, this is a placeholder for future enhancement
        pass
    
    def cleanup_old_entries(self, older_than_hours: int = 24):
        """Cleanup old usage entries to prevent memory bloat"""
        
        with self.lock:
            cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
            
            for user_id in list(self.usage.keys()):
                for key in list(self.usage[user_id].keys()):
                    # Keep only recent entries
                    self.usage[user_id][key] = [
                        ts for ts in self.usage[user_id][key]
                        if ts > cutoff_time
                    ]
                
                # Remove user if no usage left
                if not any(self.usage[user_id].values()):
                    del self.usage[user_id]
    
    @staticmethod
    def _get_window_start(now: datetime, window: QuotaWindow) -> datetime:
        """Get start time of current window"""
        if window == QuotaWindow.PER_MINUTE:
            return now - timedelta(minutes=1)
        elif window == QuotaWindow.PER_HOUR:
            return now - timedelta(hours=1)
        elif window == QuotaWindow.PER_DAY:
            return now - timedelta(days=1)
    
    @staticmethod
    def _get_window_reset_time(now: datetime, window: QuotaWindow) -> datetime:
        """Get time when current window resets"""
        if window == QuotaWindow.PER_MINUTE:
            return now + timedelta(minutes=1)
        elif window == QuotaWindow.PER_HOUR:
            return now + timedelta(hours=1)
        elif window == QuotaWindow.PER_DAY:
            return now + timedelta(days=1)
    
    def _get_usage_in_window(
        self,
        user_id: str,
        window_key: str,
        cutoff_time: datetime
    ) -> int:
        """Count usage entries in time window"""
        
        if user_id not in self.usage:
            return 0
        
        return len([
            ts for ts in self.usage[user_id][window_key]
            if ts >= cutoff_time
        ])


class TokenBucket:
    """
    Token bucket rate limiter implementation
    
    Allows bursty traffic while maintaining average rate limit.
    More sophisticated than simple counter.
    """
    
    def __init__(self, capacity: int, refill_rate_per_second: float):
        """
        Initialize token bucket
        
        Args:
            capacity: Maximum tokens in bucket
            refill_rate_per_second: Tokens added per second
        """
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate_per_second
        self.last_refill = datetime.now()
        self.lock = threading.Lock()
    
    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens
        
        Args:
            tokens: Number of tokens to consume
        
        Returns:
            True if tokens available, False otherwise
        """
        
        with self.lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    def get_available_tokens(self) -> float:
        """Get current number of available tokens"""
        with self.lock:
            self._refill()
            return self.tokens
    
    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = datetime.now()
        elapsed_seconds = (now - self.last_refill).total_seconds()
        
        new_tokens = elapsed_seconds * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def rate_limit_check(user_id: str, tool_name: str, is_vip: bool = False) -> Tuple[bool, Dict]:
    """Convenience function for rate limit checking"""
    limiter = get_rate_limiter()
    return limiter.is_allowed(user_id, tool_name, is_vip)


# Example usage of TokenBucket for specific high-cost operations
# Create per-user buckets for expensive tools
_token_buckets: Dict[str, TokenBucket] = {}
_bucket_lock = threading.Lock()


def get_token_bucket(user_id: str, capacity: int = 10, refill_rate: float = 1.0) -> TokenBucket:
    """Get token bucket for user"""
    
    with _bucket_lock:
        if user_id not in _token_buckets:
            _token_buckets[user_id] = TokenBucket(capacity, refill_rate)
        
        return _token_buckets[user_id]
