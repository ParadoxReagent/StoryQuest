"""
Tests for the enhanced safety filter.
Phase 6: Enhanced Safety, Guardrails & Kid-Friendly Constraints
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from app.services.safety_filter_enhanced import (
    EnhancedSafetyFilter,
    SafetyViolation,
    ViolationType,
)


@pytest.fixture
def safety_filter():
    """Create an enhanced safety filter instance."""
    return EnhancedSafetyFilter(use_moderation_api=False, log_violations=False)


@pytest.mark.asyncio
async def test_filter_user_input_allows_safe_input(safety_filter):
    """Test that safe user input is allowed."""
    is_safe, sanitized, violation = await safety_filter.filter_user_input(
        "I want to explore the garden", age_range="6-8"
    )

    assert is_safe is True
    assert sanitized == "I want to explore the garden"
    assert violation is None


@pytest.mark.asyncio
async def test_filter_user_input_blocks_banned_words(safety_filter):
    """Test that banned words are blocked."""
    is_safe, reason, violation = await safety_filter.filter_user_input(
        "I want to fight the dragon", age_range="6-8"
    )

    assert is_safe is False
    assert "kinder words" in reason
    assert violation is not None
    assert violation.violation_type == ViolationType.BANNED_WORD


@pytest.mark.asyncio
async def test_filter_user_input_blocks_urls(safety_filter):
    """Test that URLs are blocked."""
    is_safe, reason, violation = await safety_filter.filter_user_input(
        "Check out https://example.com for more"
    )

    assert is_safe is False
    assert "personal information" in reason
    assert violation is not None
    assert violation.violation_type == ViolationType.INAPPROPRIATE_PATTERN


@pytest.mark.asyncio
async def test_filter_user_input_blocks_email_addresses(safety_filter):
    """Test that email addresses are blocked."""
    is_safe, reason, violation = await safety_filter.filter_user_input(
        "Contact me at user@example.com"
    )

    assert is_safe is False
    assert "personal information" in reason
    assert violation.violation_type == ViolationType.INAPPROPRIATE_PATTERN


@pytest.mark.asyncio
async def test_filter_user_input_blocks_phone_numbers(safety_filter):
    """Test that phone numbers are blocked."""
    is_safe, reason, violation = await safety_filter.filter_user_input(
        "Call me at 555-123-4567"
    )

    assert is_safe is False
    assert violation.violation_type == ViolationType.INAPPROPRIATE_PATTERN


@pytest.mark.asyncio
async def test_filter_user_input_enforces_length_limit(safety_filter):
    """Test that overly long input is rejected."""
    long_text = "a" * 201

    is_safe, reason, violation = await safety_filter.filter_user_input(long_text)

    assert is_safe is False
    assert "too long" in reason
    assert violation.violation_type == ViolationType.INAPPROPRIATE_PATTERN


@pytest.mark.asyncio
async def test_filter_user_input_blocks_empty_input(safety_filter):
    """Test that empty input is rejected."""
    is_safe, reason, violation = await safety_filter.filter_user_input("")

    assert is_safe is False
    assert "cannot be empty" in reason


@pytest.mark.asyncio
async def test_filter_user_input_blocks_age_inappropriate_words_6_8(safety_filter):
    """Test that complex words are blocked for age 6-8."""
    is_safe, reason, violation = await safety_filter.filter_user_input(
        "there was a betrayal", age_range="6-8"
    )

    assert is_safe is False
    assert "simpler" in reason
    assert violation.violation_type == ViolationType.AGE_INAPPROPRIATE


@pytest.mark.asyncio
async def test_filter_user_input_allows_age_appropriate_for_9_12(safety_filter):
    """Test that words blocked for 6-8 might be OK for 9-12."""
    # "complex" is in the 6-8 banned list but not 9-12
    is_safe, sanitized, violation = await safety_filter.filter_user_input(
        "This puzzle is complex", age_range="9-12"
    )

    assert is_safe is True


@pytest.mark.asyncio
async def test_validate_llm_output_allows_safe_content(safety_filter):
    """Test that safe LLM output is allowed."""
    is_valid, violation = await safety_filter.validate_llm_output(
        scene_text="You find yourself in a beautiful magical forest with friendly animals dancing around.",
        choices=["Talk to the rabbit", "Pick some flowers", "Follow the butterflies"],
        age_range="6-8"
    )

    assert is_valid is True
    assert violation is None


@pytest.mark.asyncio
async def test_validate_llm_output_blocks_banned_words_in_scene(safety_filter):
    """Test that banned words in scene text are blocked."""
    is_valid, violation = await safety_filter.validate_llm_output(
        scene_text="You see a scary monster in the dark forest",
        choices=["Run away", "Hide", "Talk"],
        age_range="6-8"
    )

    assert is_valid is False
    assert violation.violation_type == ViolationType.BANNED_WORD


@pytest.mark.asyncio
async def test_validate_llm_output_blocks_banned_words_in_choices(safety_filter):
    """Test that banned words in choices are blocked."""
    is_valid, violation = await safety_filter.validate_llm_output(
        scene_text="You are in a peaceful meadow",
        choices=["Fight the dragon", "Rest", "Explore"],
        age_range="6-8"
    )

    assert is_valid is False
    assert violation.violation_type == ViolationType.BANNED_WORD


@pytest.mark.asyncio
async def test_validate_llm_output_blocks_negative_sentiment(safety_filter):
    """Test that overly negative sentiment is blocked."""
    # Use enough negative words to trigger sentiment < -0.3 without using banned words
    # lonely (-0.4) + lonely (-0.4) + sad (-0.3) + crying (-0.3) + failure (-0.3) = -1.7 / 5 = -0.34
    is_valid, violation = await safety_filter.validate_llm_output(
        scene_text="You are lonely and sad, crying about your failure. Feeling lonely again.",
        choices=["Sit quietly", "Think deeply", "Wait here"],
        age_range="6-8"
    )

    assert is_valid is False
    assert violation.violation_type == ViolationType.NEGATIVE_SENTIMENT


@pytest.mark.asyncio
async def test_validate_llm_output_allows_mildly_emotional_content(safety_filter):
    """Test that mildly emotional content with positive balance is allowed."""
    is_valid, violation = await safety_filter.validate_llm_output(
        scene_text="Though it's a bit dark, you see beautiful twinkling stars and feel excited to explore. "
                   "Your friendly robot companion makes you feel happy and brave!",
        choices=["Look at the stars", "Talk to robot", "Explore together"],
        age_range="6-8"
    )

    assert is_valid is True


@pytest.mark.asyncio
async def test_validate_llm_output_blocks_age_inappropriate_vocabulary(safety_filter):
    """Test that age-inappropriate vocabulary is blocked."""
    is_valid, violation = await safety_filter.validate_llm_output(
        scene_text="You face a complex philosophical betrayal that requires sophisticated analysis",
        choices=["Analyze", "Think", "Decide"],
        age_range="6-8"
    )

    assert is_valid is False
    assert violation.violation_type == ViolationType.AGE_INAPPROPRIATE


def test_get_fallback_response_for_all_themes(safety_filter):
    """Test that fallback responses exist for all themes."""
    themes = [
        "space_adventure",
        "magical_forest",
        "underwater_quest",
        "dinosaur_discovery",
        "castle_quest",
        "robot_city",
    ]

    for theme in themes:
        scene, choices = safety_filter.get_fallback_response(theme)
        assert isinstance(scene, str)
        assert len(scene) > 50  # Should be a meaningful scene
        assert isinstance(choices, list)
        assert len(choices) == 3
        assert all(isinstance(choice, str) for choice in choices)


def test_get_fallback_response_has_default(safety_filter):
    """Test that unknown themes get a default fallback."""
    scene, choices = safety_filter.get_fallback_response("unknown_theme")

    assert isinstance(scene, str)
    assert len(scene) > 50
    assert isinstance(choices, list)
    assert len(choices) == 3


def test_sentiment_analysis_positive(safety_filter):
    """Test sentiment analysis on positive text."""
    score = safety_filter._analyze_sentiment(
        "You're so happy and excited! Everything is wonderful, beautiful, and amazing. "
        "Your friends are helpful and kind, making you smile and laugh with joy!"
    )

    assert score > 0.3  # Should be clearly positive


def test_sentiment_analysis_negative(safety_filter):
    """Test sentiment analysis on negative text."""
    score = safety_filter._analyze_sentiment(
        "You feel sad and upset, crying and worried. You made a mistake and failed. "
        "You're lonely and nervous, feeling anxious. Everything feels wrong and you're mad and angry."
    )

    assert score < -0.25  # Should be clearly negative


def test_sentiment_analysis_neutral(safety_filter):
    """Test sentiment analysis on neutral text."""
    score = safety_filter._analyze_sentiment(
        "You are in a room. There is a door and a window. You can see a table."
    )

    assert -0.2 < score < 0.2  # Should be close to neutral


def test_get_violation_summary_when_empty(safety_filter):
    """Test violation summary with no violations."""
    summary = safety_filter.get_violation_summary()

    assert summary["total"] == 0
    assert summary["by_type"] == {}
    assert summary["by_severity"] == {}


@pytest.mark.asyncio
async def test_get_violation_summary_with_violations():
    """Test violation summary with logged violations."""
    safety_filter = EnhancedSafetyFilter(use_moderation_api=False, log_violations=True)

    # Generate some violations (empty input doesn't get logged to violations_log)
    await safety_filter.filter_user_input("I want to fight", age_range="6-8")
    await safety_filter.filter_user_input("Visit https://example.com", age_range="6-8")
    await safety_filter.filter_user_input("I hate this", age_range="6-8")

    summary = safety_filter.get_violation_summary()

    assert summary["total"] == 3
    assert "banned_word" in summary["by_type"]
    assert "inappropriate_pattern" in summary["by_type"]
    assert len(summary["recent"]) == 3


@pytest.mark.asyncio
async def test_moderation_api_integration_flagged_content():
    """Test OpenAI Moderation API integration with flagged content."""
    safety_filter = EnhancedSafetyFilter(
        use_moderation_api=True,
        openai_api_key="test-key",
        log_violations=False
    )

    # Mock the HTTP client
    mock_response = Mock()
    mock_response.json.return_value = {
        "results": [{
            "flagged": True,
            "categories": {
                "violence": True,
                "hate": False,
            }
        }]
    }
    mock_response.raise_for_status = Mock()

    with patch.object(safety_filter.moderation_client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        is_safe, reason, violation = await safety_filter.filter_user_input(
            "Some potentially inappropriate text"
        )

        assert is_safe is False
        assert violation.violation_type == ViolationType.MODERATION_API


@pytest.mark.asyncio
async def test_moderation_api_integration_safe_content():
    """Test OpenAI Moderation API integration with safe content."""
    safety_filter = EnhancedSafetyFilter(
        use_moderation_api=True,
        openai_api_key="test-key",
        log_violations=False
    )

    # Mock the HTTP client
    mock_response = Mock()
    mock_response.json.return_value = {
        "results": [{
            "flagged": False,
            "categories": {}
        }]
    }
    mock_response.raise_for_status = Mock()

    with patch.object(safety_filter.moderation_client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        is_safe, sanitized, violation = await safety_filter.filter_user_input(
            "I want to explore the castle"
        )

        assert is_safe is True
        assert violation is None


@pytest.mark.asyncio
async def test_moderation_api_fails_open_on_error():
    """Test that moderation API failures don't block content (fail open)."""
    safety_filter = EnhancedSafetyFilter(
        use_moderation_api=True,
        openai_api_key="test-key",
        log_violations=False
    )

    # Mock the HTTP client to raise an exception
    with patch.object(safety_filter.moderation_client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = Exception("API Error")

        is_safe, sanitized, violation = await safety_filter.filter_user_input(
            "I want to explore the castle"
        )

        # Should still allow the content (fail open)
        assert is_safe is True


@pytest.mark.asyncio
async def test_filter_blocks_repeated_characters(safety_filter):
    """Test that spam-like repeated characters are blocked."""
    is_safe, reason, violation = await safety_filter.filter_user_input(
        "aaaaaaaaaa I want to explore"
    )

    assert is_safe is False
    assert violation.violation_type == ViolationType.INAPPROPRIATE_PATTERN


@pytest.mark.asyncio
async def test_filter_blocks_social_media_handles(safety_filter):
    """Test that social media handles are blocked."""
    is_safe, reason, violation = await safety_filter.filter_user_input(
        "Follow me @username for more adventures"
    )

    assert is_safe is False
    assert violation.violation_type == ViolationType.INAPPROPRIATE_PATTERN


@pytest.mark.asyncio
async def test_close_moderation_client():
    """Test that moderation client is properly closed."""
    safety_filter = EnhancedSafetyFilter(
        use_moderation_api=True,
        openai_api_key="test-key"
    )

    # Mock the aclose method
    safety_filter.moderation_client.aclose = AsyncMock()

    await safety_filter.close()

    safety_filter.moderation_client.aclose.assert_called_once()


@pytest.mark.asyncio
async def test_close_without_moderation_client(safety_filter):
    """Test that close works when moderation API is not enabled."""
    # Should not raise an exception
    await safety_filter.close()


def test_banned_words_list_is_comprehensive(safety_filter):
    """Test that banned words list contains expected categories."""
    banned = safety_filter.banned_words

    # Should have violence words
    assert "fight" in banned
    assert "kill" in banned
    assert "weapon" in banned

    # Should have fear/horror words
    assert "scary" in banned
    assert "monster" in banned

    # Should have negative words
    assert "hate" in banned
    assert "stupid" in banned

    # Should have danger words
    assert "danger" in banned
    assert "trap" in banned

    # All should be lowercase
    assert all(word.islower() for word in banned)


def test_positive_words_list_exists(safety_filter):
    """Test that positive words list is defined."""
    positive = safety_filter.positive_words

    assert "happy" in positive
    assert "joy" in positive
    assert "fun" in positive
    assert "friend" in positive
    assert "explore" in positive
