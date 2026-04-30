"""backends package — factory function for the configured backend."""
from __future__ import annotations

from ..config import Config
from .base import AIBackend, PackageSuggestion, SuggestionResult
from .gemini import GeminiBackend
from .ollama import OllamaBackend
from .openai_compat import OpenAICompatBackend

__all__ = [
    "AIBackend",
    "PackageSuggestion",
    "SuggestionResult",
    "get_backend",
]

_GROQ_BASE = "https://api.groq.com/openai/v1"
_OPENAI_BASE = "https://api.openai.com/v1"


def get_backend(config: Config) -> AIBackend:
    """Return the correct backend instance based on config.ai.model."""
    ai = config.ai
    model = ai.model

    if model == "gemini":
        return GeminiBackend(api_key=ai.gemini_api_key, model=ai.gemini_model)

    if model == "openai":
        return OpenAICompatBackend(
            api_key=ai.openai_api_key,
            model=ai.openai_model,
            base_url=ai.openai_base_url or _OPENAI_BASE,
            provider_name="OpenAI",
        )

    if model == "groq":
        return OpenAICompatBackend(
            api_key=ai.groq_api_key,
            model=ai.groq_model,
            base_url=_GROQ_BASE,
            provider_name="Groq",
        )

    if model == "ollama":
        return OllamaBackend(base_url=ai.ollama_base_url, model=ai.ollama_model)

    # Fallback
    return GeminiBackend(api_key=ai.gemini_api_key, model=ai.gemini_model)
