"""
Configuration management for StoryQuest.
Phase 2: Configuration system with YAML support
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OllamaConfig(BaseModel):
    """Configuration for Ollama LLM provider."""
    base_url: str = Field(default="http://localhost:11434")
    model: str = Field(default="llama3.2:3b")


class OpenAIConfig(BaseModel):
    """Configuration for OpenAI LLM provider."""
    api_key: str = Field(default="")
    model: str = Field(default="gpt-4o-mini")


class AnthropicConfig(BaseModel):
    """Configuration for Anthropic LLM provider."""
    api_key: str = Field(default="")
    model: str = Field(default="claude-3-5-haiku-20241022")


class GeminiConfig(BaseModel):
    """Configuration for Google Gemini LLM provider."""
    api_key: str = Field(default="")
    model: str = Field(default="gemini-1.5-flash")


class OpenRouterConfig(BaseModel):
    """Configuration for OpenRouter LLM provider."""
    api_key: str = Field(default="")
    model: str = Field(default="anthropic/claude-3.5-haiku")
    site_url: str = Field(
        default="https://storyquest.local",
        description="Site/Referer value required by OpenRouter"
    )
    app_name: str = Field(
        default="StoryQuest",
        description="X-Title header value required by OpenRouter"
    )


class LLMConfig(BaseModel):
    """LLM provider configuration."""
    provider: str = Field(
        default="ollama",
        description="LLM provider: 'ollama', 'openai', 'anthropic', 'gemini', or 'openrouter'"
    )
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    openai: OpenAIConfig = Field(default_factory=OpenAIConfig)
    anthropic: AnthropicConfig = Field(default_factory=AnthropicConfig)
    gemini: GeminiConfig = Field(default_factory=GeminiConfig)
    openrouter: OpenRouterConfig = Field(default_factory=OpenRouterConfig)


class StoryConfig(BaseModel):
    """Story engine configuration."""
    max_turns: int = Field(default=50, description="Maximum turns per session")
    themes: List[str] = Field(
        default_factory=lambda: [
            "magical_forest",
            "space_adventure",
            "underwater_quest",
            "dinosaur_discovery",
            "castle_quest",
            "robot_city"
        ],
        description="Available story themes"
    )
    default_age_range: str = Field(default="6-12", description="Default age range")


class DatabaseConfig(BaseModel):
    """Database configuration."""
    url: str = Field(
        default="sqlite:///./storyquest.db",
        description="Database URL (SQLite or PostgreSQL)"
    )
    echo: bool = Field(default=False, description="Echo SQL queries (for debugging)")


class SafetyConfig(BaseModel):
    """Safety and content moderation configuration."""
    use_enhanced_filter: bool = Field(
        default=True,
        description="Use enhanced safety filter with comprehensive checks"
    )
    use_moderation_api: bool = Field(
        default=False,
        description="Use OpenAI Moderation API for additional validation"
    )
    log_violations: bool = Field(
        default=True,
        description="Log safety violations for review"
    )
    enable_rate_limiting: bool = Field(
        default=True,
        description="Enable rate limiting to prevent abuse"
    )
    max_turns_per_session: int = Field(
        default=50,
        description="Maximum turns allowed per session"
    )
    max_custom_inputs_per_10min: int = Field(
        default=5,
        description="Maximum custom inputs per 10 minutes"
    )


class AppConfig(BaseModel):
    """Complete application configuration."""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    story: StoryConfig = Field(default_factory=StoryConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Environment variables take precedence
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None

    # Model names
    OLLAMA_MODEL: Optional[str] = None
    OPENAI_MODEL: Optional[str] = None
    ANTHROPIC_MODEL: Optional[str] = None
    GEMINI_MODEL: Optional[str] = None
    OPENROUTER_MODEL: Optional[str] = None

    # Provider-specific settings
    OLLAMA_BASE_URL: Optional[str] = None
    OPENROUTER_SITE_URL: Optional[str] = None
    OPENROUTER_APP_NAME: Optional[str] = None

    # Other settings
    DATABASE_URL: Optional[str] = None
    LLM_PROVIDER: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


def load_config(config_path: Optional[Path] = None) -> AppConfig:
    """
    Load configuration from YAML file and environment variables.

    Environment variables override config file values.

    Args:
        config_path: Path to config.yaml file (default: ./config.yaml)

    Returns:
        AppConfig instance
    """
    # Default config
    config_dict: Dict = {
        "llm": {},
        "story": {},
        "database": {},
        "safety": {}
    }

    # Load from YAML file if it exists
    if config_path is None:
        config_path = Path("config.yaml")

    if config_path.exists():
        with open(config_path, "r") as f:
            yaml_config = yaml.safe_load(f)
            if yaml_config:
                config_dict.update(yaml_config)

    # Load environment variables
    settings = Settings()

    # Override with environment variables
    if settings.LLM_PROVIDER:
        config_dict.setdefault("llm", {})
        config_dict["llm"]["provider"] = settings.LLM_PROVIDER

    # Ollama configuration
    if settings.OLLAMA_BASE_URL:
        config_dict.setdefault("llm", {}).setdefault("ollama", {})
        config_dict["llm"]["ollama"]["base_url"] = settings.OLLAMA_BASE_URL
    if settings.OLLAMA_MODEL:
        config_dict.setdefault("llm", {}).setdefault("ollama", {})
        config_dict["llm"]["ollama"]["model"] = settings.OLLAMA_MODEL

    # OpenAI configuration
    if settings.OPENAI_API_KEY:
        config_dict.setdefault("llm", {}).setdefault("openai", {})
        config_dict["llm"]["openai"]["api_key"] = settings.OPENAI_API_KEY
    if settings.OPENAI_MODEL:
        config_dict.setdefault("llm", {}).setdefault("openai", {})
        config_dict["llm"]["openai"]["model"] = settings.OPENAI_MODEL

    # Anthropic configuration
    if settings.ANTHROPIC_API_KEY:
        config_dict.setdefault("llm", {}).setdefault("anthropic", {})
        config_dict["llm"]["anthropic"]["api_key"] = settings.ANTHROPIC_API_KEY
    if settings.ANTHROPIC_MODEL:
        config_dict.setdefault("llm", {}).setdefault("anthropic", {})
        config_dict["llm"]["anthropic"]["model"] = settings.ANTHROPIC_MODEL

    # Gemini configuration
    if settings.GEMINI_API_KEY:
        config_dict.setdefault("llm", {}).setdefault("gemini", {})
        config_dict["llm"]["gemini"]["api_key"] = settings.GEMINI_API_KEY
    if settings.GEMINI_MODEL:
        config_dict.setdefault("llm", {}).setdefault("gemini", {})
        config_dict["llm"]["gemini"]["model"] = settings.GEMINI_MODEL

    # OpenRouter configuration
    if settings.OPENROUTER_API_KEY:
        config_dict.setdefault("llm", {}).setdefault("openrouter", {})
        config_dict["llm"]["openrouter"]["api_key"] = settings.OPENROUTER_API_KEY
    if settings.OPENROUTER_MODEL:
        config_dict.setdefault("llm", {}).setdefault("openrouter", {})
        config_dict["llm"]["openrouter"]["model"] = settings.OPENROUTER_MODEL
    if settings.OPENROUTER_SITE_URL:
        config_dict.setdefault("llm", {}).setdefault("openrouter", {})
        config_dict["llm"]["openrouter"]["site_url"] = settings.OPENROUTER_SITE_URL
    if settings.OPENROUTER_APP_NAME:
        config_dict.setdefault("llm", {}).setdefault("openrouter", {})
        config_dict["llm"]["openrouter"]["app_name"] = settings.OPENROUTER_APP_NAME

    if settings.DATABASE_URL:
        config_dict.setdefault("database", {})
        config_dict["database"]["url"] = settings.DATABASE_URL

    # Create and return config
    return AppConfig(**config_dict)


def save_config(config: AppConfig, config_path: Path = Path("config.yaml")) -> None:
    """
    Save configuration to YAML file.

    Args:
        config: AppConfig instance to save
        config_path: Path to save config.yaml file
    """
    config_dict = config.model_dump()

    # Remove sensitive data before saving
    if "llm" in config_dict:
        if "openai" in config_dict["llm"] and "api_key" in config_dict["llm"]["openai"]:
            config_dict["llm"]["openai"]["api_key"] = "${OPENAI_API_KEY}"
        if "anthropic" in config_dict["llm"] and "api_key" in config_dict["llm"]["anthropic"]:
            config_dict["llm"]["anthropic"]["api_key"] = "${ANTHROPIC_API_KEY}"
        if "gemini" in config_dict["llm"] and "api_key" in config_dict["llm"]["gemini"]:
            config_dict["llm"]["gemini"]["api_key"] = "${GEMINI_API_KEY}"
        if "openrouter" in config_dict["llm"] and "api_key" in config_dict["llm"]["openrouter"]:
            config_dict["llm"]["openrouter"]["api_key"] = "${OPENROUTER_API_KEY}"

    with open(config_path, "w") as f:
        yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)


# Global config instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """
    Get the global configuration instance.

    Returns:
        AppConfig instance
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config


def set_config(config: AppConfig) -> None:
    """
    Set the global configuration instance.

    Args:
        config: AppConfig instance to set
    """
    global _config
    _config = config
