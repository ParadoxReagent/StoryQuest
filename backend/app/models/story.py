"""
Pydantic models for story data structures.
Phase 1: Story format & API contract
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class Choice(BaseModel):
    """Represents a single choice option for the player."""
    choice_id: str = Field(..., description="Unique identifier for this choice")
    text: str = Field(..., description="The text displayed to the player")


class Scene(BaseModel):
    """Represents a single scene in the story."""
    scene_id: str = Field(..., description="Unique identifier for this scene")
    text: str = Field(..., description="The narrative text for this scene")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When this scene was created")


class StoryMetadata(BaseModel):
    """Metadata about the story session."""
    turns: int = Field(default=0, description="Number of turns taken in this story")
    theme: str = Field(..., description="The theme of the story (e.g., 'magical_forest', 'space_adventure')")
    age_range: str = Field(..., description="Target age range (e.g., '6-8', '9-12')")
    max_turns: int = Field(default=15, description="Maximum number of turns for this story")
    is_finished: bool = Field(default=False, description="Whether the story has reached its ending")


class StoryState(BaseModel):
    """Complete state of a story session."""
    session_id: UUID = Field(default_factory=uuid4, description="Unique session identifier")
    story_summary: str = Field(..., description="Compact summary of the story so far (for LLM context)")
    current_scene: Scene = Field(..., description="The current scene")
    choices: List[Choice] = Field(..., description="Available choices for the player")
    metadata: StoryMetadata = Field(..., description="Story metadata")


class StartStoryRequest(BaseModel):
    """Request to start a new story."""
    player_name: str = Field(..., min_length=1, max_length=100, description="The player's name")
    age_range: str = Field(..., description="Target age range (e.g., '6-8', '9-12')")
    theme: str = Field(..., description="Story theme (e.g., 'space_adventure', 'magical_forest')")


class ContinueStoryRequest(BaseModel):
    """Request to continue an existing story."""
    session_id: UUID = Field(..., description="The session ID to continue")
    choice_id: Optional[str] = Field(None, description="ID of the selected choice (if using suggested choice)")
    choice_text: Optional[str] = Field(None, description="Text of the selected choice (if using suggested choice)")
    custom_input: Optional[str] = Field(None, max_length=200, description="Custom player input (if not using suggested choice)")
    story_summary: str = Field(..., description="Current story summary (sent by client for stateless backend)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "choice_id": "c1",
                "custom_input": None,
                "story_summary": "Alex is exploring a magical forest and has met a friendly fox."
            }
        }
    )


class StoryResponse(BaseModel):
    """Response containing story state."""
    session_id: UUID
    story_summary: str
    current_scene: Scene
    choices: List[Choice]
    metadata: Optional[StoryMetadata] = None


class LLMStoryResponse(BaseModel):
    """The expected response format from the LLM."""
    scene_text: str = Field(..., description="The narrative text for the next scene")
    choices: Optional[List[str]] = Field(default=None, description="List of 3 choice options (optional for final turn)")
    story_summary_update: str = Field(..., description="Updated story summary")
