"""Coordinates Planner -> Worker(s) -> Reviewer, looping on revision feedback."""

from __future__ import annotations

from dataclasses import dataclass, field

from .agents import PlannerAgent, ReviewerAgent, WorkerAgent
from .config import Config
from .llm_client import LLMClient


@dataclass
class RunResult:
    goal: str
    iterations: list[dict] = field(default_factory=list)
    final_verdict: str = "REVISE"
    final_feedback: str = ""

    @property
    def passed(self) -> bool:
        return self.final_verdict == "PASS"


class Orchestrator:
    def __init__(self, config: Config, *, on_event=None):
        llm = LLMClient(config)
        self._config = config
        self._planner = PlannerAgent(llm)
        self._worker = WorkerAgent(llm)
        self._reviewer = ReviewerAgent(llm)
        self._on_event = on_event or (lambda *_: None)

    def _emit(self, event: str, payload: dict) -> None:
        self._on_event(event, payload)

    def run(self, goal: str) -> RunResult:
        result = RunResult(goal=goal)
        subtasks = self._planner.plan(goal)
        self._emit("plan", {"subtasks": subtasks})

        for loop in range(self._config.max_revision_loops + 1):
            subtask_results = []
            context = ""
            for subtask in subtasks:
                output = self._worker.execute(subtask, context=context)
                subtask_results.append({"subtask": subtask, "result": output})
                context += f"- {subtask}: {output}\n"
                self._emit("subtask_done", {"subtask": subtask, "result": output})

            review = self._reviewer.review(goal, subtask_results)
            verdict = review.get("verdict", "REVISE")
            feedback = review.get("feedback", "")

            result.iterations.append(
                {"subtasks": subtasks, "results": subtask_results, "review": review}
            )
            result.final_verdict = verdict
            result.final_feedback = feedback
            self._emit("review", {"verdict": verdict, "feedback": feedback})

            if verdict == "PASS" or loop == self._config.max_revision_loops:
                break

            subtasks = self._planner.revise(goal, subtasks, feedback)
            self._emit("replan", {"subtasks": subtasks})

        return result
