"""Integration tests for FastAPI endpoints."""

from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.config import AppConfig, DatabaseConfig, SafetyConfig, get_config, set_config
from app.models.story import Choice, Scene, StoryMetadata, StoryResponse
from app.api.v1 import story as story_router
from app.db import database as database_module
from app.main import app


class StubStoryEngine:
    def __init__(self):
        self.session_id = uuid4()
        self.start_calls = []
        self.continue_calls = []

    async def start_story(self, player_name: str, age_range: str, theme: str, db_session):
        self.start_calls.append({
            "player_name": player_name,
            "age_range": age_range,
            "theme": theme,
        })
        scene = Scene(scene_id="scene-1", text="Stub start scene")
        metadata = StoryMetadata(turns=0, theme=theme, age_range=age_range)
        return StoryResponse(
            session_id=self.session_id,
            story_summary="Stub summary",
            current_scene=scene,
            choices=[Choice(choice_id="c1", text="Go left")],
            metadata=metadata,
        )

    async def continue_story(
        self,
        session_id,
        choice_id,
        custom_input,
        story_summary,
        db_session,
    ):
        self.continue_calls.append({
            "session_id": session_id,
            "choice_id": choice_id,
            "custom_input": custom_input,
            "story_summary": story_summary,
        })
        scene = Scene(scene_id="scene-2", text="Stub continue scene")
        metadata = StoryMetadata(turns=1, theme="space_adventure", age_range="6-8")
        return StoryResponse(
            session_id=session_id,
            story_summary=story_summary + " -> next",
            current_scene=scene,
            choices=[Choice(choice_id="c1", text="Keep going")],
            metadata=metadata,
        )


@pytest.fixture
def api_client():
    prev_config = get_config()
    test_config = AppConfig(
        database=DatabaseConfig(url="sqlite:///:memory:"),
        safety=SafetyConfig(
            use_enhanced_filter=False,
            use_moderation_api=False,
            log_violations=False,
            enable_rate_limiting=False,
            max_turns_per_session=10,
            max_custom_inputs_per_10min=5,
        ),
    )
    set_config(test_config)

    stub_engine = StubStoryEngine()

    def override_engine():
        return stub_engine

    def override_db_session():
        class DummySession:
            def commit(self):  # pragma: no cover - no-op
                pass

            def rollback(self):  # pragma: no cover - no-op
                pass

        yield DummySession()

    app.dependency_overrides[story_router.get_story_engine] = override_engine
    app.dependency_overrides[database_module.get_db_session] = override_db_session

    with TestClient(app) as client:
        yield client, stub_engine

    app.dependency_overrides.clear()
    set_config(prev_config)


def test_start_story_endpoint(api_client):
    client, stub_engine = api_client

    response = client.post(
        "/api/v1/story/start",
        json={"player_name": "Luna", "age_range": "6-8", "theme": "space_adventure"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["current_scene"]["text"] == "Stub start scene"
    assert stub_engine.start_calls[0]["player_name"] == "Luna"


def test_start_story_validation_error(api_client):
    client, _ = api_client

    response = client.post(
        "/api/v1/story/start",
        json={"player_name": "", "age_range": "6-8", "theme": "space_adventure"},
    )

    assert response.status_code == 422


def test_continue_story_endpoint(api_client):
    client, stub_engine = api_client

    response = client.post(
        "/api/v1/story/continue",
        json={
            "session_id": str(stub_engine.session_id),
            "choice_id": "c1",
            "custom_input": None,
            "story_summary": "Stub summary",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["current_scene"]["text"] == "Stub continue scene"
    assert stub_engine.continue_calls[0]["choice_id"] == "c1"


def test_continue_story_validation_error(api_client):
    client, stub_engine = api_client

    response = client.post(
        "/api/v1/story/continue",
        json={"session_id": str(stub_engine.session_id)},
    )

    assert response.status_code == 422
