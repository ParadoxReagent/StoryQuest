"""
Rate Limiter for API endpoints.
Phase 6: Enhanced Safety - Prevents abuse and ensures fair usage
"""

import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

from fastapi import Request, HTTPException, status


class RateLimitExceeded(HTTPException):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, retry_after: int):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Please try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)}
        )


class RateLimiter:
    """
    Token bucket rate limiter for API endpoints.
    Phase 6: Prevents abuse and ensures fair usage.
    """

    def __init__(self):
        """Initialize rate limiter with tracking dictionaries."""
        # Session-based limits: {session_id: {endpoint: [(timestamp, count), ...]}}
        self.session_requests: Dict[str, Dict[str, list]] = defaultdict(lambda: defaultdict(list))

        # IP-based limits: {ip: {endpoint: [(timestamp, count), ...]}}
        self.ip_requests: Dict[str, Dict[str, list]] = defaultdict(lambda: defaultdict(list))

        # Custom input tracking: {session_id: [timestamps]}
        self.custom_input_requests: Dict[str, list] = defaultdict(list)

        # Rate limit rules
        self.limits = {
            # Session limits (per session_id)
            "session_turns_per_hour": {
                "max_requests": 20,
                "window_seconds": 3600  # 1 hour
            },
            "session_turns_per_day": {
                "max_requests": 100,
                "window_seconds": 86400  # 24 hours
            },

            # Custom input limits (stricter to prevent abuse)
            "custom_input_per_10min": {
                "max_requests": 5,
                "window_seconds": 600  # 10 minutes
            },

            # IP limits (prevent same IP from creating too many sessions)
            "ip_per_hour": {
                "max_requests": 50,
                "window_seconds": 3600  # 1 hour
            },
            "ip_per_day": {
                "max_requests": 200,
                "window_seconds": 86400  # 24 hours
            },

            # Start story limits (prevent session spam)
            "start_per_ip_per_hour": {
                "max_requests": 10,
                "window_seconds": 3600  # 1 hour
            },
        }

    def _cleanup_old_entries(
        self,
        entries: list,
        window_seconds: int
    ) -> list:
        """
        Remove entries older than the window.

        Args:
            entries: List of (timestamp, count) tuples
            window_seconds: Window size in seconds

        Returns:
            Cleaned list
        """
        now = time.time()
        cutoff = now - window_seconds
        return [(ts, count) for ts, count in entries if ts > cutoff]

    def check_session_rate_limit(
        self,
        session_id: str,
        endpoint: str = "continue"
    ) -> Tuple[bool, Optional[int]]:
        """
        Check if session has exceeded rate limit.

        Args:
            session_id: Session UUID
            endpoint: Endpoint name

        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        now = time.time()

        # Check hourly limit
        hourly_limit = self.limits["session_turns_per_hour"]
        entries = self.session_requests[session_id][endpoint]
        entries = self._cleanup_old_entries(entries, hourly_limit["window_seconds"])

        if len(entries) >= hourly_limit["max_requests"]:
            oldest_timestamp = min(ts for ts, _ in entries)
            retry_after = int(oldest_timestamp + hourly_limit["window_seconds"] - now)
            return False, retry_after

        # Check daily limit
        daily_limit = self.limits["session_turns_per_day"]
        daily_entries = self._cleanup_old_entries(entries, daily_limit["window_seconds"])

        if len(daily_entries) >= daily_limit["max_requests"]:
            oldest_timestamp = min(ts for ts, _ in daily_entries)
            retry_after = int(oldest_timestamp + daily_limit["window_seconds"] - now)
            return False, retry_after

        # Add new entry
        entries.append((now, 1))
        self.session_requests[session_id][endpoint] = entries

        return True, None

    def check_custom_input_rate_limit(
        self,
        session_id: str
    ) -> Tuple[bool, Optional[int]]:
        """
        Check rate limit for custom input (stricter).

        Args:
            session_id: Session UUID

        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        now = time.time()
        limit = self.limits["custom_input_per_10min"]

        # Get and clean entries
        entries = self.custom_input_requests[session_id]
        entries = [ts for ts in entries if ts > now - limit["window_seconds"]]

        if len(entries) >= limit["max_requests"]:
            oldest_timestamp = min(entries)
            retry_after = int(oldest_timestamp + limit["window_seconds"] - now)
            return False, retry_after

        # Add new entry
        entries.append(now)
        self.custom_input_requests[session_id] = entries

        return True, None

    def check_ip_rate_limit(
        self,
        ip_address: str,
        endpoint: str = "general"
    ) -> Tuple[bool, Optional[int]]:
        """
        Check if IP has exceeded rate limit.

        Args:
            ip_address: Client IP address
            endpoint: Endpoint name

        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        now = time.time()

        # Check hourly limit
        hourly_limit = self.limits["ip_per_hour"]
        entries = self.ip_requests[ip_address][endpoint]
        entries = self._cleanup_old_entries(entries, hourly_limit["window_seconds"])

        if len(entries) >= hourly_limit["max_requests"]:
            oldest_timestamp = min(ts for ts, _ in entries)
            retry_after = int(oldest_timestamp + hourly_limit["window_seconds"] - now)
            return False, retry_after

        # Check daily limit
        daily_limit = self.limits["ip_per_day"]
        daily_entries = self._cleanup_old_entries(entries, daily_limit["window_seconds"])

        if len(daily_entries) >= daily_limit["max_requests"]:
            oldest_timestamp = min(ts for ts, _ in daily_entries)
            retry_after = int(oldest_timestamp + daily_limit["window_seconds"] - now)
            return False, retry_after

        # Add new entry
        entries.append((now, 1))
        self.ip_requests[ip_address][endpoint] = entries

        return True, None

    def check_start_story_rate_limit(
        self,
        ip_address: str
    ) -> Tuple[bool, Optional[int]]:
        """
        Check rate limit for starting new stories (prevent session spam).

        Args:
            ip_address: Client IP address

        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        now = time.time()
        limit = self.limits["start_per_ip_per_hour"]

        entries = self.ip_requests[ip_address]["start_story"]
        entries = self._cleanup_old_entries(entries, limit["window_seconds"])

        if len(entries) >= limit["max_requests"]:
            oldest_timestamp = min(ts for ts, _ in entries)
            retry_after = int(oldest_timestamp + limit["window_seconds"] - now)
            return False, retry_after

        # Add new entry
        entries.append((now, 1))
        self.ip_requests[ip_address]["start_story"] = entries

        return True, None

    def get_client_ip(self, request: Request) -> str:
        """
        Extract client IP from request.

        Args:
            request: FastAPI request object

        Returns:
            Client IP address
        """
        # Check for forwarded IP (behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct client
        return request.client.host if request.client else "unknown"

    def get_stats(self) -> Dict:
        """
        Get rate limiter statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "active_sessions": len(self.session_requests),
            "active_ips": len(self.ip_requests),
            "custom_input_tracked": len(self.custom_input_requests),
            "limits": self.limits
        }


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """
    Get the global rate limiter instance.

    Returns:
        RateLimiter instance
    """
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def reset_rate_limiter():
    """Reset the rate limiter (useful for testing)."""
    global _rate_limiter
    _rate_limiter = RateLimiter()
