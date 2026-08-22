"""Monitor-specific configuration: watchlist, batching, alerting."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class MonitorConfig:
    watchlist: list[str]
    batch_seconds: float
    batch_size: int
    db_path: str
    alert_provider: str
    discord_webhook_url: str
    telegram_bot_token: str
    telegram_chat_id: str
    banned_keywords: list[str]


def load_monitor_config() -> MonitorConfig:
    watchlist_raw = os.getenv("TIKTOK_WATCHLIST", "")
    watchlist = [u.strip().lstrip("@") for u in watchlist_raw.split(",") if u.strip()]

    keywords_raw = os.getenv("MONITOR_BANNED_KEYWORDS", "")
    banned_keywords = [k.strip().lower() for k in keywords_raw.split(",") if k.strip()]

    return MonitorConfig(
        watchlist=watchlist,
        batch_seconds=float(os.getenv("MONITOR_BATCH_SECONDS", "10")),
        batch_size=int(os.getenv("MONITOR_BATCH_SIZE", "15")),
        db_path=os.getenv("MONITOR_LOG_DB", "monitor.sqlite3"),
        alert_provider=os.getenv("ALERT_PROVIDER", "none").strip().lower(),
        discord_webhook_url=os.getenv("ALERT_DISCORD_WEBHOOK_URL", "").strip(),
        telegram_bot_token=os.getenv("ALERT_TELEGRAM_BOT_TOKEN", "").strip(),
        telegram_chat_id=os.getenv("ALERT_TELEGRAM_CHAT_ID", "").strip(),
        banned_keywords=banned_keywords,
    )
