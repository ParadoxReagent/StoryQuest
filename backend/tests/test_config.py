"""
Tests for configuration management.
"""

import pytest
from app.config import AppConfig, LLMConfig, StoryConfig, load_config


def test_default_config():
    """Test that default configuration loads correctly."""
    config = AppConfig()

    assert config.llm.provider == "ollama"
    assert config.llm.ollama.base_url == "http://localhost:11434"
    assert config.llm.ollama.model == "llama3.2:3b"
    assert config.story.max_turns == 50
    assert len(config.story.themes) > 0


def test_llm_config():
    """Test LLM configuration."""
    llm_config = LLMConfig(provider="openai")

    assert llm_config.provider == "openai"
    assert llm_config.ollama.base_url == "http://localhost:11434"
    assert llm_config.openai.model == "gpt-4o-mini"


def test_story_config():
    """Test story configuration."""
    story_config = StoryConfig(max_turns=100)

    assert story_config.max_turns == 100
    assert "magical_forest" in story_config.themes
    assert "space_adventure" in story_config.themes
