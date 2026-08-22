"""Worker: executes a single subtask, optionally invoking a tool."""

from __future__ import annotations

from ..tools import TOOL_DESCRIPTIONS, TOOLS
from .base import Agent

_SYSTEM = f"""You are the Worker in a multi-agent system. You execute ONE subtask at a
time and report the result.

{TOOL_DESCRIPTIONS}

Respond with ONLY a JSON object:
{{"tool": "<tool name or null>", "tool_input": "<string argument or null>", "result": "<your final answer/result for this subtask, in plain text>"}}

If you need a tool, set "tool" and "tool_input", and leave "result" as your best answer
assuming the tool succeeds (the system will re-run you with the real tool output if it
differs meaningfully). If no tool is needed, set "tool" to null and just fill "result"."""


class WorkerAgent(Agent):
    role = "worker"
    system_prompt = _SYSTEM

    def execute(self, subtask: str, context: str = "") -> str:
        prompt = f"Subtask: {subtask}"
        if context:
            prompt += f"\n\nContext from previous subtasks:\n{context}"

        response = self._ask(prompt, as_json=True)
        tool_name = response.get("tool")
        tool_input = response.get("tool_input")
        result = response.get("result", "")

        if tool_name and tool_name in TOOLS:
            tool_output = TOOLS[tool_name](tool_input or "")
            result = f"{result}\n(tool `{tool_name}` output: {tool_output})".strip()

        return result
