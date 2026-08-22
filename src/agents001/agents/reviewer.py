"""Reviewer: checks whether the combined worker output satisfies the goal."""

from __future__ import annotations

import json

from .base import Agent

_SYSTEM = """You are the Reviewer in a multi-agent system. Given the original goal and
the results produced by the Worker for each subtask, judge whether the goal has been
fully and correctly satisfied.

Respond with ONLY a JSON object:
{"verdict": "PASS" or "REVISE", "feedback": "brief explanation; if REVISE, say exactly what's missing or wrong"}"""


class ReviewerAgent(Agent):
    role = "reviewer"
    system_prompt = _SYSTEM

    def review(self, goal: str, subtask_results: list[dict]) -> dict:
        prompt = (
            f"Goal: {goal}\n\n"
            f"Subtask results:\n{json.dumps(subtask_results, indent=2)}\n\n"
            "Does this fully satisfy the goal?"
        )
        return self._ask(prompt, as_json=True)
