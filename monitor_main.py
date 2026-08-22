"""Entrypoint: python monitor_main.py  (reads TIKTOK_WATCHLIST etc. from .env)"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents001.monitor import run_monitor  # noqa: E402

if __name__ == "__main__":
    try:
        asyncio.run(run_monitor())
    except KeyboardInterrupt:
        print("\nStopped.")
        sys.exit(0)
