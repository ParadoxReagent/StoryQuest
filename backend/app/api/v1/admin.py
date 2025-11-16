"""
Admin API endpoints for safety monitoring and system management.
Phase 6: Safety monitoring and content review
"""

import logging
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import get_config
from app.services.rate_limiter import get_rate_limiter
from app.services.story_engine import StoryEngine
from app.api.v1.story import get_story_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/safety/violations")
async def get_safety_violations(
    engine: StoryEngine = Depends(get_story_engine)
) -> Dict:
    """
    Get summary of logged safety violations.

    Returns:
        Dictionary with violation statistics
    """
    # Check if using enhanced safety filter
    safety_filter = engine.safety

    if hasattr(safety_filter, 'get_violation_summary'):
        # Enhanced safety filter with violation logging
        return safety_filter.get_violation_summary()
    else:
        # Basic safety filter
        return {
            "message": "Enhanced safety filter not enabled. Enable use_enhanced_filter in config to track violations."
        }


@router.get("/rate-limiter/stats")
async def get_rate_limiter_stats() -> Dict:
    """
    Get rate limiter statistics.

    Returns:
        Dictionary with rate limiter statistics
    """
    config = get_config()

    if not config.safety.enable_rate_limiting:
        return {
            "message": "Rate limiting is not enabled. Enable it in config to track statistics."
        }

    rate_limiter = get_rate_limiter()
    return rate_limiter.get_stats()


@router.post("/rate-limiter/reset")
async def reset_rate_limiter() -> Dict:
    """
    Reset the rate limiter (clear all tracking).
    Use with caution - this clears all rate limit tracking.

    Returns:
        Success message
    """
    from app.services.rate_limiter import reset_rate_limiter

    reset_rate_limiter()
    logger.info("Rate limiter has been reset by admin")

    return {
        "message": "Rate limiter has been reset successfully",
        "warning": "All rate limit tracking has been cleared"
    }


@router.get("/config/safety")
async def get_safety_config() -> Dict:
    """
    Get current safety configuration.

    Returns:
        Safety configuration settings
    """
    config = get_config()

    return {
        "use_enhanced_filter": config.safety.use_enhanced_filter,
        "use_moderation_api": config.safety.use_moderation_api,
        "log_violations": config.safety.log_violations,
        "enable_rate_limiting": config.safety.enable_rate_limiting,
        "max_turns_per_session": config.safety.max_turns_per_session,
        "max_custom_inputs_per_10min": config.safety.max_custom_inputs_per_10min,
    }


@router.get("/health/detailed")
async def detailed_health_check() -> Dict:
    """
    Detailed health check with safety status.

    Returns:
        Detailed health information
    """
    config = get_config()

    return {
        "status": "healthy",
        "version": "0.6.0",  # Phase 6
        "llm_provider": config.llm.provider,
        "safety": {
            "enhanced_filter_enabled": config.safety.use_enhanced_filter,
            "moderation_api_enabled": config.safety.use_moderation_api,
            "rate_limiting_enabled": config.safety.enable_rate_limiting,
            "violation_logging_enabled": config.safety.log_violations,
        },
        "database": {
            "type": "sqlite" if "sqlite" in config.database.url else "postgresql",
            "url": config.database.url.split("@")[-1] if "@" in config.database.url else config.database.url,
        },
        "story": {
            "available_themes": config.story.themes,
            "max_turns": config.safety.max_turns_per_session,
        }
    }
