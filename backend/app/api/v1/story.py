"""
Story API endpoints.
Phase 1: API contract implementation
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.models.story import (
    ContinueStoryRequest,
    StartStoryRequest,
    StoryResponse,
)

router = APIRouter(prefix="/api/v1/story", tags=["story"])


@router.post("/start", response_model=StoryResponse, status_code=status.HTTP_201_CREATED)
async def start_story(request: StartStoryRequest) -> StoryResponse:
    """
    Start a new story session.

    Args:
        request: Story initialization parameters (player_name, age_range, theme)

    Returns:
        StoryResponse with initial scene and choices
    """
    # TODO: Implement story engine integration
    # This is a stub for Phase 1
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Story engine not yet implemented. This will be completed in Phase 3."
    )


@router.post("/continue", response_model=StoryResponse)
async def continue_story(request: ContinueStoryRequest) -> StoryResponse:
    """
    Continue an existing story with a player's choice.

    Args:
        request: Session ID, choice, and current story state

    Returns:
        StoryResponse with next scene and new choices
    """
    # TODO: Implement story engine integration
    # This is a stub for Phase 1
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Story engine not yet implemented. This will be completed in Phase 3."
    )


@router.get("/session/{session_id}", response_model=dict)
async def get_session(session_id: UUID) -> dict:
    """
    Retrieve full story history for a session.

    Args:
        session_id: The session UUID to retrieve

    Returns:
        Complete session history with all turns
    """
    # TODO: Implement database integration
    # This is a stub for Phase 1
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Session retrieval not yet implemented. This will be completed in Phase 3."
    )


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
async def reset_session(session_id: UUID) -> None:
    """
    Reset/abandon a story session.

    Args:
        session_id: The session UUID to reset
    """
    # TODO: Implement database integration
    # This is a stub for Phase 1
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Session reset not yet implemented. This will be completed in Phase 3."
    )
