"""Entrypoint: python chat_main.py — interactive chat with memory across the session.

For structured multi-step tasks (planning + execution + review), use main.py instead.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents001.chat import ChatSession  # noqa: E402
from agents001.config import load_config  # noqa: E402
from agents001.llm_client import LLMClient, LLMError  # noqa: E402


def main() -> int:
    config = load_config()
    session = ChatSession(LLMClient(config))

    print(f"Agents001 chat ({config.provider}: {config.model})")
    print("Type your message, or 'exit'/'quit' to leave.\n")

    while True:
        try:
            user_input = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            return 0

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Exiting.")
            return 0

        try:
            reply = session.send(user_input)
        except LLMError as exc:
            print(f"[error] {exc}")
            continue

        print(f"agent> {reply}\n")


if __name__ == "__main__":
    raise SystemExit(main())
