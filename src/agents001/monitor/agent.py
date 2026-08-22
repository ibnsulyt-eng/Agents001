"""LLM-based Monitor agent: reviews a batch of live comments for moderation issues."""

from __future__ import annotations

from ..agents.base import Agent

_SYSTEM = """You are a live-stream comment moderation assistant. You will be given a
numbered batch of recent comments from a TikTok Live room. Flag ONLY comments that show
clear signs of: spam/scam links, harassment or hate speech, self-harm risk, sexual
solicitation, or coordinated inauthentic/bot-like behavior. Do not flag ordinary chat,
jokes, disagreement, or slang that isn't actually abusive — false positives waste the
moderator's time.

Respond with ONLY a JSON object:
{"flags": [{"index": <int>, "reason": "<short reason>", "severity": "low"|"medium"|"high"}]}

If nothing needs flagging, respond with {"flags": []}."""


class MonitorAgent(Agent):
    role = "monitor"
    system_prompt = _SYSTEM

    def review_batch(self, comments: list[str]) -> list[dict]:
        if not comments:
            return []
        numbered = "\n".join(f"{i}: {c}" for i, c in enumerate(comments))
        result = self._ask(f"Comments:\n{numbered}", as_json=True)
        return result.get("flags", [])
