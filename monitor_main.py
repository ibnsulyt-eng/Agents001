"""Entrypoint: python monitor_main.py [username-or-tiktok-url ...]

With no arguments, reads TIKTOK_WATCHLIST from .env. Pass one or more usernames or
TikTok URLs (e.g. https://www.tiktok.com/@someaccount/live) to watch them instead,
without needing to edit .env first — handy for a quick one-off test.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents001.monitor import run_monitor  # noqa: E402

if __name__ == "__main__":
    override = sys.argv[1:] or None
    try:
        asyncio.run(run_monitor(override))
    except KeyboardInterrupt:
        print("\nStopped.")
        sys.exit(0)
