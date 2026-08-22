"""Thin HTTP client for OpenAI-compatible chat-completions endpoints.

Both Groq and OpenRouter's free tiers speak this same wire format, so one
client works for either — swap providers by changing LLM_PROVIDER in .env.
"""

from __future__ import annotations

import json
import time
from typing import Any

import requests

from .config import Config


class LLMError(RuntimeError):
    pass


class LLMClient:
    def __init__(self, config: Config):
        self._config = config

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.3,
        max_retries: int = 3,
    ) -> str:
        """Send a chat-completions request and return the assistant's text reply."""
        headers = {
            "Authorization": f"Bearer {self._config.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._config.model,
            "messages": messages,
            "temperature": temperature,
        }

        last_error: Exception | None = None
        for attempt in range(1, max_retries + 1):
            try:
                resp = requests.post(
                    self._config.api_base, headers=headers, json=payload, timeout=60
                )
                if resp.status_code == 429:
                    # Free-tier rate limit — back off and retry.
                    wait = min(2**attempt, 20)
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            except (requests.RequestException, KeyError, json.JSONDecodeError) as exc:
                last_error = exc
                time.sleep(min(2**attempt, 10))

        raise LLMError(f"LLM request failed after {max_retries} attempts: {last_error}")

    def chat_json(self, messages: list[dict[str, str]], **kwargs: Any) -> dict:
        """Chat, then parse the reply as JSON (tolerating ```json fences)."""
        raw = self.chat(messages, **kwargs)
        text = raw.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:]
            text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise LLMError(f"Model did not return valid JSON:\n{raw}") from exc
