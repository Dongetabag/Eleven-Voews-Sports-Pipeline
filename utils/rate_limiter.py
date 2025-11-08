#!/usr/bin/env python3
"""
Rate limiting utilities for API calls
Prevents hitting API rate limits and ensures fair usage
"""

import time
from collections import defaultdict
from typing import Dict, Optional
from threading import Lock
from utils.logger import get_logger

logger = get_logger('rate_limiter')

class RateLimiter:
    """Thread-safe rate limiter"""
    
    def __init__(self, max_calls: int, period: float):
        """
        Initialize rate limiter
        
        Args:
            max_calls: Maximum number of calls allowed
            period: Time period in seconds
        """
        self.max_calls = max_calls
        self.period = period
        self.calls = defaultdict(list)
        self.lock = Lock()
    
    def wait_if_needed(self, key: str = 'default'):
        """
        Wait if rate limit would be exceeded
        
        Args:
            key: Rate limit key (for different limits per service)
        """
        with self.lock:
            now = time.time()
            # Remove old calls outside the period
            self.calls[key] = [
                call_time for call_time in self.calls[key]
                if now - call_time < self.period
            ]
            
            # If at limit, wait
            if len(self.calls[key]) >= self.max_calls:
                sleep_time = self.period - (now - self.calls[key][0])
                if sleep_time > 0:
                    logger.debug(f"Rate limit reached for {key}, waiting {sleep_time:.2f}s")
                    time.sleep(sleep_time)
                    # Clean up again after sleep
                    now = time.time()
                    self.calls[key] = [
                        call_time for call_time in self.calls[key]
                        if now - call_time < self.period
                    ]
            
            # Record this call
            self.calls[key].append(time.time())
    
    def can_proceed(self, key: str = 'default') -> bool:
        """
        Check if call can proceed without waiting
        
        Args:
            key: Rate limit key
        
        Returns:
            True if can proceed, False if would exceed limit
        """
        with self.lock:
            now = time.time()
            self.calls[key] = [
                call_time for call_time in self.calls[key]
                if now - call_time < self.period
            ]
            return len(self.calls[key]) < self.max_calls

# Global rate limiters for different services
_rate_limiters: Dict[str, RateLimiter] = {}

def get_rate_limiter(service: str, max_calls: int = 60, period: float = 60.0) -> RateLimiter:
    """
    Get or create rate limiter for a service
    
    Args:
        service: Service name
        max_calls: Max calls per period
        period: Period in seconds
    
    Returns:
        RateLimiter instance
    """
    if service not in _rate_limiters:
        _rate_limiters[service] = RateLimiter(max_calls, period)
    return _rate_limiters[service]






