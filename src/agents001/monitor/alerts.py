"""Push a flagged event to Discord or Telegram, if configured. Both are free webhooks."""

from __future__ import annotations

import requests

from .config import MonitorConfig


def send_alert(config: MonitorConfig, message: str) -> None:
    if config.alert_provider == "discord" and config.discord_webhook_url:
        try:
            requests.post(
                config.discord_webhook_url, json={"content": message[:1900]}, timeout=10
            )
        except requests.RequestException as exc:
            print(f"[alerts] Discord send failed: {exc}")

    elif config.alert_provider == "telegram" and config.telegram_bot_token and config.telegram_chat_id:
        url = f"https://api.telegram.org/bot{config.telegram_bot_token}/sendMessage"
        try:
            requests.post(
                url,
                json={"chat_id": config.telegram_chat_id, "text": message[:4000]},
                timeout=10,
            )
        except requests.RequestException as exc:
            print(f"[alerts] Telegram send failed: {exc}")

    # alert_provider == "none" (or misconfigured) -> no-op; events are still logged to SQLite.
