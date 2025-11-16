"""Unit tests for the safety filter rules."""

import pytest

from app.services.safety_filter import SafetyFilter


@pytest.mark.asyncio
async def test_filter_user_input_blocks_banned_words():
    safety = SafetyFilter()

    is_safe, reason = await safety.filter_user_input("I want to fight the dragon")

    assert is_safe is False
    assert "inappropriate" in reason


@pytest.mark.asyncio
async def test_filter_user_input_rejects_urls():
    safety = SafetyFilter()

    is_safe, reason = await safety.filter_user_input("Check out https://example.com")

    assert is_safe is False
    assert "URLs" in reason


@pytest.mark.asyncio
async def test_filter_user_input_length_limit():
    safety = SafetyFilter()
    long_text = "a" * (safety.max_input_length + 1)

    is_safe, reason = await safety.filter_user_input(long_text)

    assert is_safe is False
    assert "Input too long" in reason


@pytest.mark.asyncio
async def test_validate_llm_output_blocks_banned_words():
    safety = SafetyFilter()

    is_valid = await safety.validate_llm_output(
        scene_text="The hero plans a fight",
        choices=["Fight", "Hide", "Talk"],
    )

    assert is_valid is False


def test_get_fallback_response_is_theme_specific():
    safety = SafetyFilter()

    scene, choices = safety.get_fallback_response("magical_forest")

    assert "butterflies" in scene
    assert len(choices) == 3
