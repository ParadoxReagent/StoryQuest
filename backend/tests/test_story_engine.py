"""Tests for the StoryEngine orchestration logic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import pytest

from app.db import models as db_models
from app.models.story import LLMStoryResponse, StoryResponse
from app.services.llm_provider import LLMProvider
from app.services.story_engine import StoryEngine


@dataclass
class FakeSafetyFilter:
    """Lightweight safety filter stub."""

    valid_output: bool = True
    fallback_scene: str = "Safe fallback scene"
    fallback_choices: List[str] = None

    def __post_init__(self):
        if self.fallback_choices is None:
            self.fallback_choices = ["Explore", "Wait", "Sing"]
        self.filtered_inputs: List[str] = []

    async def filter_user_input(self, text: str):
        self.filtered_inputs.append(text)
        return True, text.strip()

    async def validate_llm_output(self, scene_text: str, choices: List[str]) -> bool:
        return self.valid_output

    def get_fallback_response(self, theme: str):
        return self.fallback_scene, self.fallback_choices


class FakeLLMProvider(LLMProvider):
    """LLM provider that replays a queue of canned responses."""

    def __init__(self, responses: List[LLMStoryResponse]):
        self.responses = responses
        self.calls: List[dict] = []

    async def generate_story_continuation(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.8,
    ) -> LLMStoryResponse:
        self.calls.append({
            "prompt": prompt,
            "system_message": system_message,
            "max_tokens": max_tokens,
            "temperature": temperature,
        })
        return self.responses.pop(0)

    async def is_healthy(self) -> bool:  # pragma: no cover - not used
        return True


def _make_llm_response(text: str) -> LLMStoryResponse:
    return LLMStoryResponse(
        scene_text=text,
        choices=["Choice A", "Choice B", "Choice C"],
        story_summary_update=f"Summary of {text}",
    )


@pytest.mark.asyncio
async def test_start_story_persists_initial_turn(db_session):
    llm = FakeLLMProvider([_make_llm_response("Scene 1")])
    safety = FakeSafetyFilter()
    engine = StoryEngine(llm_provider=llm, safety_filter=safety)

    response = await engine.start_story(
        player_name="Alex",
        age_range="6-8",
        theme="space_adventure",
        db_session=db_session,
    )

    assert isinstance(response, StoryResponse)
    assert response.current_scene.text == "Scene 1"
    assert len(response.choices) == 3

    stored_session = db_session.query(db_models.Session).one()
    assert stored_session.player_name == "Alex"
    turns = db_session.query(db_models.StoryTurn).all()
    assert len(turns) == 1
    assert turns[0].scene_text == "Scene 1"


@pytest.mark.asyncio
async def test_continue_story_updates_turns_and_summary(db_session):
    llm = FakeLLMProvider([
        _make_llm_response("Scene 1"),
        _make_llm_response("Scene 2"),
    ])
    safety = FakeSafetyFilter()
    engine = StoryEngine(llm_provider=llm, safety_filter=safety)

    start_response = await engine.start_story("Maya", "6-8", "space_adventure", db_session)
    continue_response = await engine.continue_story(
        session_id=start_response.session_id,
        choice_id=None,
        choice_text=None,
        custom_input="I open the door",
        story_summary=start_response.story_summary,
        db_session=db_session,
    )

    assert continue_response.metadata.turns == 1
    assert safety.filtered_inputs == ["I open the door"]
    assert db_session.query(db_models.StoryTurn).count() == 2


@pytest.mark.asyncio
async def test_engine_allows_llm_provider_switch(db_session):
    llm_start = FakeLLMProvider([_make_llm_response("Scene 1")])
    llm_continue = FakeLLMProvider([_make_llm_response("Scene 2")])
    safety = FakeSafetyFilter()
    engine = StoryEngine(llm_provider=llm_start, safety_filter=safety)

    start_response = await engine.start_story("Noa", "6-8", "space_adventure", db_session)

    # Switch providers mid-session to verify StoryEngine uses the new one
    engine.llm = llm_continue

    response = await engine.continue_story(
        session_id=start_response.session_id,
        choice_id="c1",
        choice_text="Go left",
        custom_input=None,
        story_summary=start_response.story_summary,
        db_session=db_session,
    )

    assert response.current_scene.text == "Scene 2"
    assert llm_continue.calls, "New provider should have been invoked"


@pytest.mark.asyncio
async def test_retry_logic_returns_fallback_when_validation_fails(db_session):
    llm = FakeLLMProvider([_make_llm_response("Unsafe scene")])
    safety = FakeSafetyFilter(valid_output=False, fallback_scene="Fallback scene")
    engine = StoryEngine(
        llm_provider=llm,
        safety_filter=safety,
        max_retries=1,
    )

    response = await engine.start_story("Kai", "6-8", "magical_forest", db_session)

    assert response.current_scene.text == "Fallback scene"
    assert response.choices[0].text == safety.fallback_choices[0]


@pytest.mark.asyncio
async def test_session_history_and_reset(db_session):
    llm = FakeLLMProvider([
        _make_llm_response("Scene 1"),
        _make_llm_response("Scene 2"),
    ])
    safety = FakeSafetyFilter()
    engine = StoryEngine(llm_provider=llm, safety_filter=safety)

    start_response = await engine.start_story("Tess", "6-8", "space_adventure", db_session)
    await engine.continue_story(
        session_id=start_response.session_id,
        choice_id="c1",
        choice_text="Go left",
        custom_input=None,
        story_summary=start_response.story_summary,
        db_session=db_session,
    )

    history = await engine.get_session_history(start_response.session_id, db_session)
    assert history["total_turns"] == 1
    assert len(history["turns"]) == 2

    await engine.reset_session(start_response.session_id, db_session)
    session_row = db_session.get(db_models.Session, start_response.session_id)
    assert session_row.is_active is False
