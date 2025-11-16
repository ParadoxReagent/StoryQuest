"""Tests covering API request/response validation models."""

import pytest
from pydantic import ValidationError

from app.models.story import (
    Choice,
    ContinueStoryRequest,
    Scene,
    StartStoryRequest,
    StoryMetadata,
    StoryResponse,
)


def test_start_story_request_requires_player_name():
    with pytest.raises(ValidationError):
        StartStoryRequest(player_name="", age_range="6-8", theme="space_adventure")


def test_continue_story_request_enforces_custom_input_length():
    with pytest.raises(ValidationError):
        ContinueStoryRequest(
            session_id="550e8400-e29b-41d4-a716-446655440000",
            story_summary="Summary",
            custom_input="a" * 500,
        )


def test_story_response_schema_round_trip():
    scene = Scene(scene_id="scene_1", text="A sunny day")
    metadata = StoryMetadata(turns=0, theme="space_adventure", age_range="6-8")
    response = StoryResponse(
        session_id="550e8400-e29b-41d4-a716-446655440000",
        story_summary="The hero wakes up",
        current_scene=scene,
        choices=[
            Choice(choice_id="c1", text="Look around"),
            Choice(choice_id="c2", text="Call a friend"),
        ],
        metadata=metadata,
    )

    serialized = response.model_dump()
    assert serialized["current_scene"]["text"] == "A sunny day"
    assert serialized["choices"][0]["choice_id"] == "c1"
