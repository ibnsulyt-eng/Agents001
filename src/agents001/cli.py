"""Command-line entrypoint: `python main.py "your goal here"`."""

from __future__ import annotations

import sys

from .config import load_config
from .orchestrator import Orchestrator


def _print_event(event: str, payload: dict) -> None:
    if event == "plan":
        print("\n[Planner] subtasks:")
        for i, task in enumerate(payload["subtasks"], 1):
            print(f"  {i}. {task}")
    elif event == "subtask_done":
        print(f"\n[Worker] {payload['subtask']}\n  -> {payload['result']}")
    elif event == "review":
        print(f"\n[Reviewer] verdict={payload['verdict']}\n  feedback: {payload['feedback']}")
    elif event == "replan":
        print("\n[Planner] revised subtasks:")
        for i, task in enumerate(payload["subtasks"], 1):
            print(f"  {i}. {task}")


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print('Usage: python main.py "your goal here"')
        return 1

    goal = " ".join(argv)
    config = load_config()
    orchestrator = Orchestrator(config, on_event=_print_event)

    print(f"Goal: {goal}")
    print(f"Provider: {config.provider} ({config.model})")

    result = orchestrator.run(goal)

    print("\n" + "=" * 60)
    print("PASSED" if result.passed else "STOPPED (max revisions reached)")
    print("=" * 60)
    return 0 if result.passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
