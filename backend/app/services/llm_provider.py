"""
LLM Provider abstraction layer.
Phase 2: Swappable interface for local vs. cloud LLMs
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional

import httpx
from pydantic import ValidationError

from app.models.story import LLMStoryResponse

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate_story_continuation(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.8
    ) -> LLMStoryResponse:
        """
        Generate a story continuation from the LLM.

        Args:
            prompt: The prompt to send to the LLM
            system_message: Optional system message for the LLM
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation (0.0-1.0)

        Returns:
            LLMStoryResponse with scene_text, choices, and story_summary_update

        Raises:
            Exception: If LLM generation fails
        """
        pass

    @abstractmethod
    async def is_healthy(self) -> bool:
        """
        Check if the LLM service is available.

        Returns:
            True if healthy, False otherwise
        """
        pass

    def _parse_llm_response(self, response_text: str) -> LLMStoryResponse:
        """
        Parse and validate LLM response text into LLMStoryResponse.

        Args:
            response_text: Raw response text from LLM

        Returns:
            Validated LLMStoryResponse

        Raises:
            ValueError: If response is invalid or cannot be parsed
        """
        try:
            # Try to extract JSON from the response
            # Some LLMs might wrap JSON in markdown code blocks
            cleaned_text = response_text.strip()

            # Remove markdown code blocks if present
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]

            cleaned_text = cleaned_text.strip()

            # Parse JSON
            data = json.loads(cleaned_text)

            # Validate with Pydantic
            return LLMStoryResponse(**data)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response text: {response_text}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")
        except ValidationError as e:
            logger.error(f"LLM response validation failed: {e}")
            logger.error(f"Response text: {response_text}")
            raise ValueError(f"LLM response doesn't match expected format: {e}")


class OllamaProvider(LLMProvider):
    """LLM provider for Ollama (local LLM)."""

    def __init__(
        self,
        model: str = "llama3.2:3b",
        base_url: str = "http://localhost:11434"
    ):
        """
        Initialize Ollama provider.

        Args:
            model: Ollama model name (default: "llama3.2:3b")
            base_url: Ollama API base URL (default: "http://localhost:11434")
        """
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=60.0)

    async def generate_story_continuation(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.8
    ) -> LLMStoryResponse:
        """Generate story continuation using Ollama."""
        try:
            # Prepare the request
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            }

            # Add system message if provided
            if system_message:
                payload["system"] = system_message

            # Call Ollama API
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()

            # Parse response
            result = response.json()
            response_text = result.get("response", "")

            # Parse and validate
            return self._parse_llm_response(response_text)

        except httpx.HTTPError as e:
            logger.error(f"Ollama API error: {e}")
            raise Exception(f"Failed to generate story with Ollama: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in Ollama generation: {e}")
            raise

    async def is_healthy(self) -> bool:
        """Check if Ollama service is available."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            return False

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class OpenAIProvider(LLMProvider):
    """LLM provider for OpenAI."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini"
    ):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model name (default: "gpt-4o-mini")
        """
        self.api_key = api_key
        self.model = model
        self.client = httpx.AsyncClient(
            timeout=60.0,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )

    async def generate_story_continuation(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.8
    ) -> LLMStoryResponse:
        """Generate story continuation using OpenAI."""
        try:
            # Prepare messages
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})

            # Prepare request payload
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "response_format": {"type": "json_object"}
            }

            # Call OpenAI API
            response = await self.client.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload
            )
            response.raise_for_status()

            # Parse response
            result = response.json()
            response_text = result["choices"][0]["message"]["content"]

            # Parse and validate
            return self._parse_llm_response(response_text)

        except httpx.HTTPError as e:
            logger.error(f"OpenAI API error: {e}")
            raise Exception(f"Failed to generate story with OpenAI: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI generation: {e}")
            raise

    async def is_healthy(self) -> bool:
        """Check if OpenAI API is available."""
        try:
            response = await self.client.get("https://api.openai.com/v1/models")
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"OpenAI health check failed: {e}")
            return False

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class AnthropicProvider(LLMProvider):
    """LLM provider for Anthropic Claude."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-haiku-20241022"
    ):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key
            model: Model name (default: "claude-3-5-haiku-20241022")
        """
        self.api_key = api_key
        self.model = model
        self.client = httpx.AsyncClient(
            timeout=60.0,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
        )

    async def generate_story_continuation(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.8
    ) -> LLMStoryResponse:
        """Generate story continuation using Anthropic Claude."""
        try:
            # Prepare request payload
            payload = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }

            # Add system message if provided
            if system_message:
                payload["system"] = system_message

            # Call Anthropic API
            response = await self.client.post(
                "https://api.anthropic.com/v1/messages",
                json=payload
            )
            response.raise_for_status()

            # Parse response
            result = response.json()
            response_text = result["content"][0]["text"]

            # Parse and validate
            return self._parse_llm_response(response_text)

        except httpx.HTTPError as e:
            logger.error(f"Anthropic API error: {e}")
            raise Exception(f"Failed to generate story with Anthropic: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in Anthropic generation: {e}")
            raise

    async def is_healthy(self) -> bool:
        """
        Check if Anthropic API is available.

        Note: Anthropic doesn't have a dedicated health endpoint,
        so we just verify the API key format is valid.
        """
        return bool(self.api_key and len(self.api_key) > 0)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class GeminiProvider(LLMProvider):
    """LLM provider for Google Gemini."""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-1.5-flash",
        base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=60.0)

    async def generate_story_continuation(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.8
    ) -> LLMStoryResponse:
        """Generate story continuation using Gemini."""
        try:
            payload: Dict = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": prompt}]
                    }
                ],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                },
            }

            if system_message:
                payload["system_instruction"] = {
                    "role": "system",
                    "parts": [{"text": system_message}]
                }

            response = await self.client.post(
                f"{self.base_url}/models/{self.model}:generateContent",
                params={"key": self.api_key},
                json=payload,
            )
            response.raise_for_status()

            result = response.json()
            candidates = result.get("candidates", [])
            if not candidates:
                raise ValueError("Gemini did not return any candidates")
            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                raise ValueError("Gemini response missing content parts")
            response_text = parts[0].get("text", "")

            return self._parse_llm_response(response_text)

        except httpx.HTTPError as e:
            logger.error(f"Gemini API error: {e}")
            raise Exception(f"Failed to generate story with Gemini: {e}")
        except Exception:
            logger.exception("Unexpected error in Gemini generation")
            raise

    async def is_healthy(self) -> bool:
        """Check if Gemini API is available."""
        try:
            response = await self.client.get(
                f"{self.base_url}/models/{self.model}",
                params={"key": self.api_key},
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Gemini health check failed: {e}")
            return False

    async def close(self):
        await self.client.aclose()


class OpenRouterProvider(LLMProvider):
    """LLM provider for OpenRouter."""

    def __init__(
        self,
        api_key: str,
        model: str = "anthropic/claude-3.5-haiku",
        site_url: str = "https://storyquest.local",
        app_name: str = "StoryQuest",
    ):
        self.api_key = api_key
        self.model = model
        self.site_url = site_url
        self.app_name = app_name
        self.client = httpx.AsyncClient(
            timeout=60.0,
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": site_url,
                "X-Title": app_name,
                "Content-Type": "application/json",
            },
        )

    async def generate_story_continuation(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.8
    ) -> LLMStoryResponse:
        """Generate story continuation using OpenRouter."""
        try:
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "response_format": {"type": "json_object"},
            }

            response = await self.client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=payload,
            )
            response.raise_for_status()

            result = response.json()
            response_text = result["choices"][0]["message"]["content"]

            return self._parse_llm_response(response_text)

        except httpx.HTTPError as e:
            logger.error(f"OpenRouter API error: {e}")
            raise Exception(f"Failed to generate story with OpenRouter: {e}")
        except Exception:
            logger.exception("Unexpected error in OpenRouter generation")
            raise

    async def is_healthy(self) -> bool:
        """Check if OpenRouter API is available."""
        try:
            response = await self.client.get("https://openrouter.ai/api/v1/models")
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"OpenRouter health check failed: {e}")
            return False

    async def close(self):
        await self.client.aclose()
