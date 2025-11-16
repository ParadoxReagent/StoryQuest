"""
Factory pattern for creating LLM providers.
Phase 2: LLM abstraction layer
"""

import logging
from typing import Optional

from app.config import AppConfig, get_config
from app.services.llm_provider import (
    AnthropicProvider,
    GeminiProvider,
    LLMProvider,
    LMStudioProvider,
    OllamaProvider,
    OpenAIProvider,
    OpenRouterProvider,
)

logger = logging.getLogger(__name__)


def create_llm_provider(config: Optional[AppConfig] = None) -> LLMProvider:
    """
    Create an LLM provider based on configuration.

    Args:
        config: Application configuration (uses global config if not provided)

    Returns:
        LLMProvider instance (Ollama, OpenAI, or Anthropic)

    Raises:
        ValueError: If provider type is unknown or configuration is invalid
    """
    if config is None:
        config = get_config()

    provider_type = config.llm.provider.lower()

    logger.info(f"Creating LLM provider: {provider_type}")

    if provider_type == "ollama":
        return OllamaProvider(
            model=config.llm.ollama.model,
            base_url=config.llm.ollama.base_url
        )

    elif provider_type == "openai":
        api_key = config.llm.openai.api_key
        if not api_key:
            raise ValueError(
                "OpenAI API key not configured. "
                "Set OPENAI_API_KEY environment variable or add to config.yaml"
            )
        return OpenAIProvider(
            api_key=api_key,
            model=config.llm.openai.model
        )

    elif provider_type == "anthropic":
        api_key = config.llm.anthropic.api_key
        if not api_key:
            raise ValueError(
                "Anthropic API key not configured. "
                "Set ANTHROPIC_API_KEY environment variable or add to config.yaml"
            )
        return AnthropicProvider(
            api_key=api_key,
            model=config.llm.anthropic.model
        )

    elif provider_type == "gemini":
        api_key = config.llm.gemini.api_key
        if not api_key:
            raise ValueError(
                "Gemini API key not configured. "
                "Set GEMINI_API_KEY environment variable or add to config.yaml"
            )
        return GeminiProvider(
            api_key=api_key,
            model=config.llm.gemini.model
        )

    elif provider_type == "openrouter":
        api_key = config.llm.openrouter.api_key
        if not api_key:
            raise ValueError(
                "OpenRouter API key not configured. "
                "Set OPENROUTER_API_KEY environment variable or add to config.yaml"
            )
        return OpenRouterProvider(
            api_key=api_key,
            model=config.llm.openrouter.model,
            site_url=config.llm.openrouter.site_url,
            app_name=config.llm.openrouter.app_name,
        )

    elif provider_type == "lmstudio":
        return LMStudioProvider(
            model=config.llm.lmstudio.model,
            base_url=config.llm.lmstudio.base_url
        )

    else:
        raise ValueError(
            f"Unknown LLM provider: {provider_type}. "
            f"Must be one of: ollama, openai, anthropic, gemini, openrouter, lmstudio"
        )


# Global LLM provider instance
_llm_provider: Optional[LLMProvider] = None


def get_llm_provider() -> LLMProvider:
    """
    Get the global LLM provider instance.

    Creates the provider on first call using the global configuration.

    Returns:
        LLMProvider instance
    """
    global _llm_provider
    if _llm_provider is None:
        _llm_provider = create_llm_provider()
    return _llm_provider


def set_llm_provider(provider: LLMProvider) -> None:
    """
    Set the global LLM provider instance.

    Useful for testing or dynamic provider switching.

    Args:
        provider: LLMProvider instance to set
    """
    global _llm_provider
    _llm_provider = provider


def reset_llm_provider() -> None:
    """
    Reset the global LLM provider instance.

    Forces recreation on next call to get_llm_provider().
    """
    global _llm_provider
    if _llm_provider is not None:
        # Close existing provider if it has a close method
        if hasattr(_llm_provider, 'close'):
            try:
                import asyncio
                asyncio.create_task(_llm_provider.close())
            except Exception as e:
                logger.warning(f"Error closing LLM provider: {e}")
    _llm_provider = None
