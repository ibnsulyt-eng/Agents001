"""Shared base class for the demo agents."""

from __future__ import annotations

from ..llm_client import LLMClient


class Agent:
    role: str = "agent"
    system_prompt: str = "You are a helpful assistant."

    def __init__(self, llm: LLMClient):
        self._llm = llm

    def _ask(self, user_message: str, *, as_json: bool = False):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message},
        ]
        if as_json:
            return self._llm.chat_json(messages)
        return self._llm.chat(messages)
