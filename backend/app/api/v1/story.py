"""
Story API endpoints.
Phase 6: Enhanced with rate limiting and safety features
"""

import json
import logging
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.config import get_config
from app.db.database import get_db_session
from app.db.models import Session as SessionModel
from app.models.story import (
    ContinueStoryRequest,
    StartStoryRequest,
    StoryResponse,
)
from app.services.llm_factory import create_llm_provider
from app.services.prompts import StoryPrompts
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
            choice_text=request.choice_text,
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


@router.post("/start/stream")
async def start_story_stream(
    http_request: Request,
    request: StartStoryRequest,
    db: Session = Depends(get_db_session)
):
    """
    Start a new story session with streaming response.

    Returns Server-Sent Events (SSE) with:
    - Stream of text chunks as they're generated
    - Final event with choices and metadata
    """
    config = get_config()

    # Rate limiting check (if enabled)
    if config.safety.enable_rate_limiting:
        rate_limiter = get_rate_limiter()
        client_ip = rate_limiter.get_client_ip(http_request)

        is_allowed, retry_after = rate_limiter.check_start_story_rate_limit(client_ip)
        if not is_allowed:
            logger.warning(f"Rate limit exceeded for IP {client_ip} on start_story_stream")
            raise RateLimitExceeded(retry_after)

        is_allowed, retry_after = rate_limiter.check_ip_rate_limit(client_ip, "start_story")
        if not is_allowed:
            logger.warning(f"IP rate limit exceeded for {client_ip}")
            raise RateLimitExceeded(retry_after)

    async def generate_stream():
        """Generate SSE stream for story start."""
        try:
            # Create LLM provider and prompts
            llm_provider = create_llm_provider(config)
            prompts = StoryPrompts()

            # Create session in database
            session_id = uuid4()
            db_session_model = SessionModel(
                id=session_id,
                player_name=request.player_name,
                age_range=request.age_range,
                theme=request.theme,
                turns=0,
                is_active=True
            )
            db.add(db_session_model)
            db.flush()

            # Generate prompts
            prompt = prompts.get_story_start_prompt(
                request.player_name,
                request.age_range,
                request.theme
            )
            system_message = prompts.get_system_message(request.age_range)

            # Send initial event with session info
            yield f"data: {json.dumps({'type': 'session_start', 'session_id': str(session_id)})}\n\n"

            # Accumulate full response for parsing
            full_response = ""

            # Stream LLM response
            async for chunk in llm_provider.generate_story_continuation_stream(
                prompt=prompt,
                system_message=system_message,
                max_tokens=500,
                temperature=0.8
            ):
                full_response += chunk
                # Send text chunk
                yield f"data: {json.dumps({'type': 'text_chunk', 'content': chunk})}\n\n"

            # Parse complete response to extract scene_text and choices
            try:
                # Parse using the provider's method
                from app.services.llm_provider import LLMProvider
                llm_base = LLMProvider()
                llm_response = llm_base._parse_llm_response(full_response)

                # Create choices
                choices = [
                    {
                        "choice_id": choice.choice_id,
                        "text": choice.text
                    }
                    for choice in llm_response.choices
                ]

                # Save to database
                from app.db.models import StoryTurn
                turn = StoryTurn(
                    id=uuid4(),
                    session_id=session_id,
                    turn_number=1,
                    scene_text=llm_response.scene_text,
                    choices_json=json.dumps(choices),
                    story_summary=llm_response.story_summary_update or ""
                )
                db.add(turn)
                db_session_model.turns = 1
                db_session_model.updated_at = turn.created_at
                db.commit()

                # Send final event with metadata
                yield f"data: {json.dumps({'type': 'complete', 'choices': choices, 'metadata': {'theme': request.theme, 'turns': 0, 'session_id': str(session_id)}})}\n\n"

            except Exception as e:
                logger.error(f"Failed to parse streamed response: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': 'Failed to parse story response'})}\n\n"

        except Exception as e:
            logger.error(f"Error in streaming story start: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.post("/continue/stream")
async def continue_story_stream(
    http_request: Request,
    request: ContinueStoryRequest,
    db: Session = Depends(get_db_session)
):
    """
    Continue an existing story with streaming response.

    Returns Server-Sent Events (SSE) with:
    - Stream of text chunks as they're generated
    - Final event with choices and metadata
    """
    config = get_config()

    # Rate limiting check (if enabled)
    if config.safety.enable_rate_limiting:
        rate_limiter = get_rate_limiter()
        client_ip = rate_limiter.get_client_ip(http_request)
        session_id_str = str(request.session_id)

        is_allowed, retry_after = rate_limiter.check_session_rate_limit(session_id_str, "continue")
        if not is_allowed:
            logger.warning(f"Session rate limit exceeded for session {session_id_str}")
            raise RateLimitExceeded(retry_after)

        if request.custom_input:
            is_allowed, retry_after = rate_limiter.check_custom_input_rate_limit(session_id_str)
            if not is_allowed:
                logger.warning(f"Custom input rate limit exceeded for session {session_id_str}")
                raise RateLimitExceeded(retry_after)

        is_allowed, retry_after = rate_limiter.check_ip_rate_limit(client_ip, "continue")
        if not is_allowed:
            logger.warning(f"IP rate limit exceeded for {client_ip}")
            raise RateLimitExceeded(retry_after)

    async def generate_stream():
        """Generate SSE stream for story continuation."""
        try:
            # Create LLM provider and prompts
            llm_provider = create_llm_provider(config)
            prompts = StoryPrompts()

            # Load session from database
            from sqlalchemy import select
            stmt = select(SessionModel).where(SessionModel.id == request.session_id)
            result = db.execute(stmt)
            db_session_model = result.scalar_one_or_none()

            if not db_session_model:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Session not found'})}\n\n"
                return

            if not db_session_model.is_active:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Session is no longer active'})}\n\n"
                return

            # Get choice text
            choice_text = request.choice_text if request.choice_text else request.custom_input

            # Generate continuation prompt
            prompt = prompts.get_story_continuation_prompt(
                player_name=db_session_model.player_name,
                age_range=db_session_model.age_range,
                theme=db_session_model.theme,
                story_summary=request.story_summary or "",
                player_choice=choice_text or ""
            )
            system_message = prompts.get_system_message(db_session_model.age_range)

            # Accumulate full response for parsing
            full_response = ""

            # Stream LLM response
            async for chunk in llm_provider.generate_story_continuation_stream(
                prompt=prompt,
                system_message=system_message,
                max_tokens=500,
                temperature=0.8
            ):
                full_response += chunk
                # Send text chunk
                yield f"data: {json.dumps({'type': 'text_chunk', 'content': chunk})}\n\n"

            # Parse complete response
            try:
                from app.services.llm_provider import LLMProvider
                llm_base = LLMProvider()
                llm_response = llm_base._parse_llm_response(full_response)

                # Create choices
                choices = [
                    {
                        "choice_id": choice.choice_id,
                        "text": choice.text
                    }
                    for choice in llm_response.choices
                ]

                # Save to database
                from app.db.models import StoryTurn
                new_turn_number = db_session_model.turns + 1
                turn = StoryTurn(
                    id=uuid4(),
                    session_id=request.session_id,
                    turn_number=new_turn_number,
                    scene_text=llm_response.scene_text,
                    player_choice=choice_text,
                    choices_json=json.dumps(choices),
                    story_summary=llm_response.story_summary_update or request.story_summary or ""
                )
                db.add(turn)
                db_session_model.turns = new_turn_number
                db_session_model.updated_at = turn.created_at
                db.commit()

                # Send final event
                yield f"data: {json.dumps({'type': 'complete', 'choices': choices, 'metadata': {'theme': db_session_model.theme, 'turns': new_turn_number, 'session_id': str(request.session_id)}})}\n\n"

            except Exception as e:
                logger.error(f"Failed to parse streamed response: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': 'Failed to parse story response'})}\n\n"

        except Exception as e:
            logger.error(f"Error in streaming story continuation: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
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
