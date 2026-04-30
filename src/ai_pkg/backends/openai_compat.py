"""OpenAI-compatible backend — handles OpenAI and Groq (same API shape)."""
from __future__ import annotations

import logging

import httpx

from .base import AIBackend, SuggestionResult
from .common import SYSTEM_PROMPT, extract_json, parse_result

logger = logging.getLogger(__name__)


class OpenAICompatBackend(AIBackend):
    """Works for any OpenAI-compatible endpoint (OpenAI, Groq, etc.)."""

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str,
        provider_name: str,
    ) -> None:
        self._key = api_key
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._provider = provider_name

    @property
    def name(self) -> str:
        return f"{self._provider} ({self._model})"

    @property
    def is_configured(self) -> bool:
        return bool(self._key)

    async def suggest(self, messages: list[dict[str, str]]) -> SuggestionResult:
        goal = messages[-1]["content"] if messages else ""
        if not self._key:
            return SuggestionResult([], [], goal, error=f"{self._provider} API key is not set")

        url = f"{self._base_url}/chat/completions"
        
        api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for m in messages:
            api_messages.append({"role": m["role"], "content": m["content"]})
            
        payload = {
            "model": self._model,
            "messages": api_messages,
            "temperature": 0.2,
            "max_tokens": 2048,
        }
        headers = {
            "Authorization": f"Bearer {self._key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                body = resp.json()

            text = body["choices"][0]["message"]["content"]
            parsed = extract_json(text)
            if parsed is None:
                return SuggestionResult([], [], goal, error="AI response was not valid JSON")
            return parse_result(parsed, goal)

        except httpx.HTTPStatusError as e:
            msg = f"{self._provider} HTTP {e.response.status_code}"
            try:
                msg = e.response.json()["error"]["message"]
            except Exception:
                pass
            return SuggestionResult([], [], goal, error=msg)
        except Exception as e:
            logger.exception("%s backend error", self._provider)
            return SuggestionResult([], [], goal, error=str(e))
