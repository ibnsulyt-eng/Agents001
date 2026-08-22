"""A conversational chat agent that remembers the whole session — distinct from the
Planner/Worker/Reviewer pipeline in orchestrator.py, which is for one-shot structured
tasks. This is for actual back-and-forth conversation."""

from __future__ import annotations

from .llm_client import LLMClient

_SYSTEM = """You are a helpful, direct assistant having an ongoing conversation. Give
clear, concise answers. You have no tools in this mode — for multi-step tasks that need
planning and execution, tell the user to run `python main.py "<goal>"` instead."""

# Keep the LLM call cheap and within small free models' context limits: cap how much
# history gets sent, rather than letting it grow unbounded over a long session.
_MAX_HISTORY_MESSAGES = 20


class ChatSession:
    def __init__(self, llm: LLMClient, system_prompt: str = _SYSTEM):
        self._llm = llm
        self._system_prompt = system_prompt
        self.history: list[dict[str, str]] = []

    def send(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})

        messages = [{"role": "system", "content": self._system_prompt}] + self.history[
            -_MAX_HISTORY_MESSAGES:
        ]
        reply = self._llm.chat(messages)

        self.history.append({"role": "assistant", "content": reply})
        return reply
