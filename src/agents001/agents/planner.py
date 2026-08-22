"""Planner: breaks a high-level goal into an ordered list of subtasks."""

from __future__ import annotations

import json

from .base import Agent

_SYSTEM = """You are the Planner in a multi-agent system. Given a user's goal, break it
into a short ordered list of concrete, independently executable subtasks for a Worker
agent. The Worker has access to these tools:
- calculator(expression): arithmetic only
- write_note(text) / read_notes(): a shared scratchpad

Respond with ONLY a JSON object of the form:
{"subtasks": ["first subtask", "second subtask", ...]}

Keep the list short (2-5 items). Do not include any text outside the JSON object."""

_REVISE_SYSTEM = """You are the Planner in a multi-agent system, revising a plan after
reviewer feedback. Given the original goal, the previous subtasks, and the reviewer's
feedback, produce a corrected short ordered list of subtasks that addresses the feedback.

Respond with ONLY a JSON object of the form:
{"subtasks": ["first subtask", "second subtask", ...]}"""


class PlannerAgent(Agent):
    role = "planner"
    system_prompt = _SYSTEM

    def plan(self, goal: str) -> list[str]:
        result = self._ask(f"Goal: {goal}", as_json=True)
        return list(result.get("subtasks", []))

    def revise(self, goal: str, previous_subtasks: list[str], feedback: str) -> list[str]:
        self.system_prompt = _REVISE_SYSTEM
        prompt = (
            f"Original goal: {goal}\n"
            f"Previous subtasks: {json.dumps(previous_subtasks)}\n"
            f"Reviewer feedback: {feedback}\n\n"
            "Produce a revised subtask list that addresses the feedback."
        )
        result = self._ask(prompt, as_json=True)
        self.system_prompt = _SYSTEM
        return list(result.get("subtasks", []))
