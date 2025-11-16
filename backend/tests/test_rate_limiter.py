"""
Tests for the rate limiter functionality.
Phase 6: Enhanced Safety - Testing rate limiting and abuse prevention
"""

import time
from unittest.mock import Mock

import pytest

from app.services.rate_limiter import RateLimiter, RateLimitExceeded, reset_rate_limiter


@pytest.fixture
def rate_limiter():
    """Create a fresh rate limiter for each test."""
    reset_rate_limiter()
    return RateLimiter()


def test_session_rate_limit_allows_within_limit(rate_limiter):
    """Test that requests within rate limit are allowed."""
    session_id = "test-session-123"

    # Should allow first 20 requests within an hour
    for i in range(20):
        is_allowed, retry_after = rate_limiter.check_session_rate_limit(session_id)
        assert is_allowed is True
        assert retry_after is None


def test_session_rate_limit_blocks_exceeding_hourly_limit(rate_limiter):
    """Test that exceeding hourly limit blocks requests."""
    session_id = "test-session-456"

    # Consume the hourly limit (20 requests)
    for i in range(20):
        is_allowed, retry_after = rate_limiter.check_session_rate_limit(session_id)
        assert is_allowed is True

    # 21st request should be blocked
    is_allowed, retry_after = rate_limiter.check_session_rate_limit(session_id)
    assert is_allowed is False
    assert retry_after is not None
    assert retry_after > 0


def test_session_rate_limit_cleanup_old_entries(rate_limiter):
    """Test that old entries are cleaned up and limit resets."""
    session_id = "test-session-789"

    # Manually add old entries (older than 1 hour)
    old_time = time.time() - 3700  # 1 hour and 100 seconds ago
    rate_limiter.session_requests[session_id]["continue"] = [(old_time, 1) for _ in range(20)]

    # New request should be allowed since old entries should be cleaned up
    is_allowed, retry_after = rate_limiter.check_session_rate_limit(session_id)
    assert is_allowed is True
    assert retry_after is None


def test_custom_input_rate_limit_allows_within_limit(rate_limiter):
    """Test that custom inputs within limit are allowed."""
    session_id = "test-session-custom-1"

    # Should allow first 5 custom inputs within 10 minutes
    for i in range(5):
        is_allowed, retry_after = rate_limiter.check_custom_input_rate_limit(session_id)
        assert is_allowed is True
        assert retry_after is None


def test_custom_input_rate_limit_blocks_exceeding_limit(rate_limiter):
    """Test that exceeding custom input limit blocks requests."""
    session_id = "test-session-custom-2"

    # Consume the limit (5 requests)
    for i in range(5):
        is_allowed, retry_after = rate_limiter.check_custom_input_rate_limit(session_id)
        assert is_allowed is True

    # 6th request should be blocked
    is_allowed, retry_after = rate_limiter.check_custom_input_rate_limit(session_id)
    assert is_allowed is False
    assert retry_after is not None
    assert retry_after > 0


def test_ip_rate_limit_allows_within_limit(rate_limiter):
    """Test that IP requests within limit are allowed."""
    ip_address = "192.168.1.1"

    # Should allow first 50 requests within an hour
    for i in range(50):
        is_allowed, retry_after = rate_limiter.check_ip_rate_limit(ip_address)
        assert is_allowed is True
        assert retry_after is None


def test_ip_rate_limit_blocks_exceeding_hourly_limit(rate_limiter):
    """Test that exceeding IP hourly limit blocks requests."""
    ip_address = "192.168.1.2"

    # Consume the hourly limit (50 requests)
    for i in range(50):
        is_allowed, retry_after = rate_limiter.check_ip_rate_limit(ip_address)
        assert is_allowed is True

    # 51st request should be blocked
    is_allowed, retry_after = rate_limiter.check_ip_rate_limit(ip_address)
    assert is_allowed is False
    assert retry_after is not None


def test_start_story_rate_limit_allows_within_limit(rate_limiter):
    """Test that story starts within limit are allowed."""
    ip_address = "192.168.1.3"

    # Should allow first 10 story starts within an hour
    for i in range(10):
        is_allowed, retry_after = rate_limiter.check_start_story_rate_limit(ip_address)
        assert is_allowed is True
        assert retry_after is None


def test_start_story_rate_limit_blocks_exceeding_limit(rate_limiter):
    """Test that exceeding story start limit blocks requests."""
    ip_address = "192.168.1.4"

    # Consume the limit (10 requests)
    for i in range(10):
        is_allowed, retry_after = rate_limiter.check_start_story_rate_limit(ip_address)
        assert is_allowed is True

    # 11th request should be blocked
    is_allowed, retry_after = rate_limiter.check_start_story_rate_limit(ip_address)
    assert is_allowed is False
    assert retry_after is not None


def test_get_client_ip_from_forwarded_header(rate_limiter):
    """Test extracting IP from X-Forwarded-For header."""
    request = Mock()
    request.headers = {"X-Forwarded-For": "203.0.113.1, 198.51.100.1"}
    request.client = Mock(host="10.0.0.1")

    ip = rate_limiter.get_client_ip(request)
    assert ip == "203.0.113.1"


def test_get_client_ip_from_real_ip_header(rate_limiter):
    """Test extracting IP from X-Real-IP header."""
    request = Mock()
    request.headers = {"X-Real-IP": "203.0.113.2"}
    request.client = Mock(host="10.0.0.1")

    ip = rate_limiter.get_client_ip(request)
    assert ip == "203.0.113.2"


def test_get_client_ip_fallback_to_client(rate_limiter):
    """Test falling back to request.client.host."""
    request = Mock()
    request.headers = {}
    request.client = Mock(host="203.0.113.3")

    ip = rate_limiter.get_client_ip(request)
    assert ip == "203.0.113.3"


def test_get_client_ip_unknown_fallback(rate_limiter):
    """Test fallback when no client information is available."""
    request = Mock()
    request.headers = {}
    request.client = None

    ip = rate_limiter.get_client_ip(request)
    assert ip == "unknown"


def test_get_stats(rate_limiter):
    """Test getting rate limiter statistics."""
    # Add some activity
    rate_limiter.check_session_rate_limit("session-1")
    rate_limiter.check_session_rate_limit("session-2")
    rate_limiter.check_ip_rate_limit("192.168.1.1")
    rate_limiter.check_custom_input_rate_limit("session-1")

    stats = rate_limiter.get_stats()

    assert stats["active_sessions"] >= 2
    assert stats["active_ips"] >= 1
    assert stats["custom_input_tracked"] >= 1
    assert "limits" in stats
    assert "session_turns_per_hour" in stats["limits"]


def test_rate_limit_exception_has_retry_after():
    """Test that RateLimitExceeded exception includes retry_after."""
    with pytest.raises(RateLimitExceeded) as exc_info:
        raise RateLimitExceeded(retry_after=60)

    assert exc_info.value.status_code == 429
    assert "60 seconds" in exc_info.value.detail
    assert exc_info.value.headers["Retry-After"] == "60"


def test_different_sessions_have_independent_limits(rate_limiter):
    """Test that different sessions have independent rate limits."""
    session_1 = "session-a"
    session_2 = "session-b"

    # Consume limit for session 1
    for i in range(20):
        is_allowed, _ = rate_limiter.check_session_rate_limit(session_1)
        assert is_allowed is True

    # Session 1 should be blocked
    is_allowed, _ = rate_limiter.check_session_rate_limit(session_1)
    assert is_allowed is False

    # Session 2 should still be allowed
    is_allowed, _ = rate_limiter.check_session_rate_limit(session_2)
    assert is_allowed is True


def test_different_ips_have_independent_limits(rate_limiter):
    """Test that different IPs have independent rate limits."""
    ip_1 = "192.168.1.10"
    ip_2 = "192.168.1.20"

    # Consume limit for IP 1
    for i in range(50):
        is_allowed, _ = rate_limiter.check_ip_rate_limit(ip_1)
        assert is_allowed is True

    # IP 1 should be blocked
    is_allowed, _ = rate_limiter.check_ip_rate_limit(ip_1)
    assert is_allowed is False

    # IP 2 should still be allowed
    is_allowed, _ = rate_limiter.check_ip_rate_limit(ip_2)
    assert is_allowed is True


def test_multiple_sessions_tracked_independently(rate_limiter):
    """Test that multiple sessions are tracked independently in stats."""
    rate_limiter.check_session_rate_limit("session-alpha")
    rate_limiter.check_session_rate_limit("session-beta")
    rate_limiter.check_session_rate_limit("session-gamma")

    stats = rate_limiter.get_stats()
    assert stats["active_sessions"] == 3


def test_custom_input_limit_is_per_session(rate_limiter):
    """Test that custom input limits are tracked per session."""
    session_1 = "custom-session-1"
    session_2 = "custom-session-2"

    # Use up custom input limit for session 1
    for i in range(5):
        is_allowed, _ = rate_limiter.check_custom_input_rate_limit(session_1)
        assert is_allowed is True

    # Session 1 should be blocked
    is_allowed, _ = rate_limiter.check_custom_input_rate_limit(session_1)
    assert is_allowed is False

    # Session 2 should still work
    is_allowed, _ = rate_limiter.check_custom_input_rate_limit(session_2)
    assert is_allowed is True
