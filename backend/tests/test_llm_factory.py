"""
Tests for LLM provider factory.
"""

import pytest
from app.config import AppConfig, LLMConfig, OllamaConfig, OpenAIConfig, AnthropicConfig
from app.services.llm_factory import create_llm_provider
from app.services.llm_provider import OllamaProvider, OpenAIProvider, AnthropicProvider


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
