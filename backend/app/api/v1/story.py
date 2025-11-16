"""
Story API endpoints.
Phase 6: Enhanced with rate limiting and safety features
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import get_config
from app.db.database import get_db_session
from app.models.story import (
    ContinueStoryRequest,
    StartStoryRequest,
    StoryResponse,
)
from app.services.llm_factory import create_llm_provider
from app.services.safety_filter import SafetyFilter
from app.services.safety_filter_enhanced import EnhancedSafetyFilter
from app.services.story_engine import StoryEngine
from app.services.rate_limiter import get_rate_limiter, RateLimitExceeded

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/story", tags=["story"])


def get_story_engine() -> StoryEngine:
    """
    Dependency for getting StoryEngine instance.
    Phase 6: Uses enhanced safety filter based on configuration.

    Returns:
        StoryEngine instance
    """
    config = get_config()
    llm_provider = create_llm_provider(config)

    # Use enhanced safety filter if enabled in config
    if config.safety.use_enhanced_filter:
        # Get OpenAI API key from settings if moderation API is enabled
        openai_key = None
        if config.safety.use_moderation_api:
            try:
                from app.config import Settings
                settings = Settings()
                openai_key = settings.OPENAI_API_KEY
            except Exception as e:
                logger.warning(f"Could not load OpenAI API key for moderation: {e}")

        safety_filter = EnhancedSafetyFilter(
            use_moderation_api=config.safety.use_moderation_api,
            openai_api_key=openai_key,
            log_violations=config.safety.log_violations
        )
    else:
        # Use basic safety filter
        safety_filter = SafetyFilter()

    return StoryEngine(
        llm_provider=llm_provider,
        safety_filter=safety_filter,
        max_retries=3,
        max_turns=config.safety.max_turns_per_session
    )


@router.post("/start", response_model=StoryResponse, status_code=status.HTTP_201_CREATED)
async def start_story(
    http_request: Request,
    request: StartStoryRequest,
    engine: StoryEngine = Depends(get_story_engine),
    db: Session = Depends(get_db_session)
) -> StoryResponse:
    """
    Start a new story session.
    Phase 6: Includes rate limiting to prevent abuse.

    Args:
        http_request: HTTP request (for rate limiting)
        request: Story initialization parameters (player_name, age_range, theme)
        engine: Story engine instance (injected)
        db: Database session (injected)

    Returns:
        StoryResponse with initial scene and choices
    """
    config = get_config()

    # Rate limiting check (if enabled)
    if config.safety.enable_rate_limiting:
        rate_limiter = get_rate_limiter()
        client_ip = rate_limiter.get_client_ip(http_request)

        # Check start story rate limit
        is_allowed, retry_after = rate_limiter.check_start_story_rate_limit(client_ip)
        if not is_allowed:
            logger.warning(f"Rate limit exceeded for IP {client_ip} on start_story")
            raise RateLimitExceeded(retry_after)

        # Check general IP rate limit
        is_allowed, retry_after = rate_limiter.check_ip_rate_limit(client_ip, "start_story")
        if not is_allowed:
            logger.warning(f"IP rate limit exceeded for {client_ip}")
            raise RateLimitExceeded(retry_after)

    try:
        logger.info(f"Starting story for player: {request.player_name}, theme: {request.theme}")
        response = await engine.start_story(
            player_name=request.player_name,
            age_range=request.age_range,
            theme=request.theme,
            db_session=db
        )
        return response
    except ValueError as e:
        logger.error(f"Validation error starting story: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error starting story: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start story. Please try again."
        )


@router.post("/continue", response_model=StoryResponse)
async def continue_story(
    http_request: Request,
    request: ContinueStoryRequest,
    engine: StoryEngine = Depends(get_story_engine),
    db: Session = Depends(get_db_session)
) -> StoryResponse:
    """
    Continue an existing story with a player's choice.
    Phase 6: Includes rate limiting to prevent abuse.

    Args:
        http_request: HTTP request (for rate limiting)
        request: Session ID, choice, and current story state
        engine: Story engine instance (injected)
        db: Database session (injected)

    Returns:
        StoryResponse with next scene and new choices
    """
    config = get_config()

    # Rate limiting check (if enabled)
    if config.safety.enable_rate_limiting:
        rate_limiter = get_rate_limiter()
        client_ip = rate_limiter.get_client_ip(http_request)
        session_id_str = str(request.session_id)

        # Check session rate limit
        is_allowed, retry_after = rate_limiter.check_session_rate_limit(session_id_str, "continue")
        if not is_allowed:
            logger.warning(f"Session rate limit exceeded for session {session_id_str}")
            raise RateLimitExceeded(retry_after)

        # If custom input, check stricter rate limit
        if request.custom_input:
            is_allowed, retry_after = rate_limiter.check_custom_input_rate_limit(session_id_str)
            if not is_allowed:
                logger.warning(f"Custom input rate limit exceeded for session {session_id_str}")
                raise RateLimitExceeded(retry_after)

        # Check general IP rate limit
        is_allowed, retry_after = rate_limiter.check_ip_rate_limit(client_ip, "continue")
        if not is_allowed:
            logger.warning(f"IP rate limit exceeded for {client_ip}")
            raise RateLimitExceeded(retry_after)

    try:
        logger.info(f"Continuing story for session: {request.session_id}")
        response = await engine.continue_story(
            session_id=request.session_id,
            choice_id=request.choice_id,
            custom_input=request.custom_input,
            story_summary=request.story_summary,
            db_session=db
        )
        return response
    except ValueError as e:
        logger.error(f"Validation error continuing story: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error continuing story: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to continue story. Please try again."
        )


@router.get("/session/{session_id}", response_model=dict)
async def get_session(
    session_id: UUID,
    engine: StoryEngine = Depends(get_story_engine),
    db: Session = Depends(get_db_session)
) -> dict:
    """
    Retrieve full story history for a session.

    Args:
        session_id: The session UUID to retrieve
        engine: Story engine instance (injected)
        db: Database session (injected)

    Returns:
        Complete session history with all turns
    """
    try:
        logger.info(f"Retrieving session: {session_id}")
        history = await engine.get_session_history(
            session_id=session_id,
            db_session=db
        )
        return history
    except ValueError as e:
        logger.error(f"Session not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error retrieving session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session. Please try again."
        )


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
async def reset_session(
    session_id: UUID,
    engine: StoryEngine = Depends(get_story_engine),
    db: Session = Depends(get_db_session)
) -> None:
    """
    Reset/abandon a story session.

    Args:
        session_id: The session UUID to reset
        engine: Story engine instance (injected)
        db: Database session (injected)
    """
    try:
        logger.info(f"Resetting session: {session_id}")
        await engine.reset_session(
            session_id=session_id,
            db_session=db
        )
    except ValueError as e:
        logger.error(f"Session not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error resetting session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset session. Please try again."
        )
