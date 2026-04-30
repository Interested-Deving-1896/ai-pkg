"""Ollama local backend."""
from __future__ import annotations

import logging

import httpx

from .base import AIBackend, SuggestionResult
from .common import SYSTEM_PROMPT, extract_json, parse_result

logger = logging.getLogger(__name__)


class OllamaBackend(AIBackend):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3") -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model

    @property
    def name(self) -> str:
        return f"Ollama ({self._model})"

    @property
    def is_configured(self) -> bool:
        return True  # no API key needed

    async def suggest(self, messages: list[dict[str, str]]) -> SuggestionResult:
        goal = messages[-1]["content"] if messages else ""
        url = f"{self._base_url}/api/chat"
        
        api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for m in messages:
            api_messages.append({"role": m["role"], "content": m["content"]})

        payload = {
            "model": self._model,
            "messages": api_messages,
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                body = resp.json()

            text = body["message"]["content"]
            parsed = extract_json(text)
            if parsed is None:
                return SuggestionResult([], [], goal, error="Ollama response was not valid JSON")
            return parse_result(parsed, goal)

        except httpx.ConnectError:
            return SuggestionResult(
                [], [], goal,
                error=f"Cannot connect to Ollama at {self._base_url} — is it running?"
            )
        except Exception as e:
            logger.exception("Ollama backend error")
            return SuggestionResult([], [], goal, error=str(e))
