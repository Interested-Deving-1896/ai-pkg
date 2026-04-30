"""Gemini backend — pure REST, no SDK."""
from __future__ import annotations

import logging

import httpx

from .base import AIBackend, SuggestionResult
from .common import SYSTEM_PROMPT, extract_json, parse_result

logger = logging.getLogger(__name__)

_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models"
    "/{model}:generateContent?key={key}"
)

_USER_PROMPT = "User goal: {goal}\n\nReturn JSON only."


class GeminiBackend(AIBackend):
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash") -> None:
        self._key = api_key
        self._model = model

    @property
    def name(self) -> str:
        return f"Gemini ({self._model})"

    @property
    def is_configured(self) -> bool:
        return bool(self._key)

    async def suggest(self, messages: list[dict[str, str]]) -> SuggestionResult:
        goal = messages[-1]["content"] if messages else ""
        if not self._key:
            return SuggestionResult([], [], goal, error="Gemini API key is not set")

        url = _API_URL.format(model=self._model, key=self._key)
        
        contents = []
        for i, m in enumerate(messages):
            role = "model" if m["role"] == "assistant" else "user"
            text = m["content"]
            if i == 0 and role == "user":
                text = f"{SYSTEM_PROMPT}\n\nUser goal: {text}\n\nReturn JSON only."
            contents.append({"role": role, "parts": [{"text": text}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.2, 
                "maxOutputTokens": 4096,
                "responseMimeType": "application/json"
            },
        }

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                body = resp.json()

            text = body["candidates"][0]["content"]["parts"][0]["text"]
            parsed = extract_json(text)
            if parsed is None:
                return SuggestionResult([], [], goal, error=f"AI response was not valid JSON:\n{text[:500]}...")
            return parse_result(parsed, goal)

        except httpx.HTTPStatusError as e:
            msg = f"Gemini HTTP {e.response.status_code}"
            try:
                msg = e.response.json()["error"]["message"]
            except Exception:
                pass
            return SuggestionResult([], [], goal, error=msg)
        except Exception as e:
            logger.exception("Gemini backend error")
            return SuggestionResult([], [], goal, error=str(e))
