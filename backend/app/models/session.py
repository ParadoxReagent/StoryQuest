"""
Pydantic models for session management.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SessionInfo(BaseModel):
    """Information about a story session."""
    id: UUID
    player_name: str
    age_range: str
    theme: str
    created_at: datetime
    last_activity: datetime
    turns: int
    is_active: bool


class StoryTurn(BaseModel):
    """Represents a single turn in the story."""
    id: UUID
    session_id: UUID
    turn_number: int
    scene_text: str
    player_choice: Optional[str] = None
    custom_input: Optional[str] = None
    story_summary: str
    created_at: datetime
