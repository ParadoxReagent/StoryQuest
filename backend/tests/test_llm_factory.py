"""
Tests for LLM provider factory.
"""

import pytest
from app.config import (
    AnthropicConfig,
    AppConfig,
    GeminiConfig,
    LLMConfig,
    OllamaConfig,
    OpenAIConfig,
    OpenRouterConfig,
)
from app.services.llm_factory import create_llm_provider
from app.services.llm_provider import (
    AnthropicProvider,
    GeminiProvider,
    OllamaProvider,
    OpenAIProvider,
    OpenRouterProvider,
)


def test_create_ollama_provider():
    """Test creating Ollama provider."""
    config = AppConfig(
        llm=LLMConfig(
            provider="ollama",
            ollama=OllamaConfig(base_url="http://localhost:11434", model="llama3.2:3b")
        )
    )

    provider = create_llm_provider(config)

    assert isinstance(provider, OllamaProvider)
    assert provider.model == "llama3.2:3b"
    assert provider.base_url == "http://localhost:11434"


def test_create_openai_provider():
    """Test creating OpenAI provider."""
    config = AppConfig(
        llm=LLMConfig(
            provider="openai",
            openai=OpenAIConfig(api_key="test-key", model="gpt-4o-mini")
        )
    )

    provider = create_llm_provider(config)

    assert isinstance(provider, OpenAIProvider)
    assert provider.model == "gpt-4o-mini"
    assert provider.api_key == "test-key"


def test_create_anthropic_provider():
    """Test creating Anthropic provider."""
    config = AppConfig(
        llm=LLMConfig(
            provider="anthropic",
            anthropic=AnthropicConfig(api_key="test-key", model="claude-3-5-haiku-20241022")
        )
    )

    provider = create_llm_provider(config)

    assert isinstance(provider, AnthropicProvider)
    assert provider.model == "claude-3-5-haiku-20241022"
    assert provider.api_key == "test-key"


def test_create_gemini_provider():
    """Test creating Gemini provider."""
    config = AppConfig(
        llm=LLMConfig(
            provider="gemini",
            gemini=GeminiConfig(api_key="gem-key", model="gemini-1.5-flash")
        )
    )

    provider = create_llm_provider(config)

    assert isinstance(provider, GeminiProvider)
    assert provider.model == "gemini-1.5-flash"
    assert provider.api_key == "gem-key"


def test_create_openrouter_provider():
    """Test creating OpenRouter provider."""
    config = AppConfig(
        llm=LLMConfig(
            provider="openrouter",
            openrouter=OpenRouterConfig(
                api_key="router-key",
                model="anthropic/claude-3.5-haiku",
                site_url="https://example.com",
                app_name="StoryQuest",
            )
        )
    )

    provider = create_llm_provider(config)

    assert isinstance(provider, OpenRouterProvider)
    assert provider.model == "anthropic/claude-3.5-haiku"
    assert provider.api_key == "router-key"


def test_create_unknown_provider():
    """Test that unknown provider raises ValueError."""
    config = AppConfig(
        llm=LLMConfig(provider="unknown")
    )

    with pytest.raises(ValueError, match="Unknown LLM provider"):
        create_llm_provider(config)


def test_create_openai_provider_without_api_key():
    """Test that OpenAI provider without API key raises ValueError."""
    config = AppConfig(
        llm=LLMConfig(
            provider="openai",
            openai=OpenAIConfig(api_key="", model="gpt-4o-mini")
        )
    )

    with pytest.raises(ValueError, match="OpenAI API key not configured"):
        create_llm_provider(config)


def test_create_gemini_provider_without_api_key():
    """Test that Gemini provider without API key raises ValueError."""
    config = AppConfig(
        llm=LLMConfig(
            provider="gemini",
            gemini=GeminiConfig(api_key="", model="gemini-1.5-flash")
        )
    )

    with pytest.raises(ValueError, match="Gemini API key not configured"):
        create_llm_provider(config)


def test_create_openrouter_provider_without_api_key():
    """Test that OpenRouter provider without API key raises ValueError."""
    config = AppConfig(
        llm=LLMConfig(
            provider="openrouter",
            openrouter=OpenRouterConfig(api_key="", model="anthropic/claude-3.5-haiku")
        )
    )

    with pytest.raises(ValueError, match="OpenRouter API key not configured"):
        create_llm_provider(config)
