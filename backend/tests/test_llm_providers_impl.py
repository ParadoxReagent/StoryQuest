"""Unit tests for individual LLM providers."""

from __future__ import annotations

import json as json_module
from typing import Any, Dict, Optional

import httpx
import pytest

from app.models.story import LLMStoryResponse
from app.services.llm_provider import LLMProvider, OllamaProvider


class DummyProvider(LLMProvider):
    """Minimal LLM provider implementation for exercising base helpers."""

    async def generate_story_continuation(  # pragma: no cover - not used in tests
        self,
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.8,
    ) -> LLMStoryResponse:
        raise NotImplementedError

    async def is_healthy(self) -> bool:  # pragma: no cover - not used in tests
        return True


def test_parse_llm_response_from_plain_json():
    """The base helper should parse a straightforward JSON payload."""

    provider = DummyProvider()
    payload = {
        "scene_text": "A calm meadow",
        "choices": ["Walk", "Listen", "Rest"],
        "story_summary_update": "The hero enjoys the meadow.",
    }

    response = provider._parse_llm_response(json_module.dumps(payload))

    assert response.scene_text == "A calm meadow"
    assert response.choices == ["Walk", "Listen", "Rest"]
    assert response.story_summary_update.endswith("meadow.")


def test_parse_llm_response_from_code_block():
    """JSON wrapped in markdown code fences should still be parsed."""

    provider = DummyProvider()
    payload = {
        "scene_text": "Inside a friendly castle",
        "choices": ["Wave", "Explore", "Sing"],
        "story_summary_update": "The player enters a castle.",
    }
    wrapped = "```json\n" + json_module.dumps(payload) + "\n```"

    response = provider._parse_llm_response(wrapped)

    assert response.scene_text.startswith("Inside")
    assert response.choices[0] == "Wave"


def test_parse_llm_response_invalid_json():
    """Invalid JSON should raise a descriptive ValueError."""

    provider = DummyProvider()

    with pytest.raises(ValueError, match="Invalid JSON response"):
        provider._parse_llm_response("not-json")


@pytest.mark.asyncio
async def test_ollama_provider_generates_and_parses(monkeypatch):
    """Ensure the Ollama provider sends the correct payload and parses output."""

    sent_requests: list[Dict[str, Any]] = []
    story_payload = {
        "scene_text": "A starship hums softly.",
        "choices": ["Check the map", "Talk to the robot", "Look outside"],
        "story_summary_update": "The journey begins in space.",
    }

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def post(
            self,
            url: str,
            json: Optional[Dict[str, Any]] = None,
            params=None,
        ):
            sent_requests.append({"url": url, "json": json})
            request = httpx.Request("POST", url)
            return httpx.Response(
                200,
                request=request,
                json={"response": json_module.dumps(story_payload)},
            )

        async def get(self, url: str, params=None):  # pragma: no cover - not used here
            request = httpx.Request("GET", url)
            return httpx.Response(200, request=request, json={"tags": []})

        async def aclose(self):  # pragma: no cover - no-op in tests
            return None

    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)

    provider = OllamaProvider(model="llama3.2:3b", base_url="http://localhost:11434")
    response = await provider.generate_story_continuation(
        prompt="Tell a story",
        system_message="You are a calm narrator",
        max_tokens=200,
        temperature=0.5,
    )

    assert response == LLMStoryResponse(**story_payload)
    assert sent_requests  # ensure a request was made
    request = sent_requests[0]
    assert request["url"].endswith("/api/generate")
    assert request["json"]["model"] == "llama3.2:3b"
    assert request["json"]["stream"] is False
    assert request["json"]["options"]["num_predict"] == 200
    assert request["json"]["system"] == "You are a calm narrator"
