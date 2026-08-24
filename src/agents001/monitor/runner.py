"""Runs a RoomWatcher per watchlist account, plus one batch-triage loop that logs
everything, filters cheaply with rules first, and escalates ambiguous comments to the
LLM Monitor agent in batches (keeps free-tier LLM usage low)."""

from __future__ import annotations

import asyncio
import time

from ..config import load_config
from ..llm_client import LLMClient
from .agent import MonitorAgent
from .alerts import send_alert
from .config import MonitorConfig, load_monitor_config
from .rules import check_keywords, looks_like_spam
from .store import Event, EventStore
from .watcher import RoomWatcher


async def _batch_flusher(
    queue: "asyncio.Queue[Event]",
    store: EventStore,
    monitor_config: MonitorConfig,
    monitor_agent: MonitorAgent,
) -> None:
    pending: list[tuple[int, Event]] = []  # (db_id, event) awaiting LLM review
    last_flush = time.monotonic()

    while True:
        timeout = max(0.1, monitor_config.batch_seconds - (time.monotonic() - last_flush))
        try:
            event = await asyncio.wait_for(queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            event = None

        if event is not None:
            db_id = store.add(event)
            print(f"[{event.room}] {event.event_type} {event.nickname}: {event.text}")

            if event.event_type == "comment" and event.text:
                kw = check_keywords(event.text, monitor_config.banned_keywords)
                spam = looks_like_spam(event.text)
                if kw:
                    store.mark_flagged(db_id, f"banned keyword: {kw}", "medium", "rule")
                    send_alert(
                        monitor_config,
                        f"[{event.room}] {event.nickname}: {event.text} (keyword: {kw})",
                    )
                elif spam:
                    store.mark_flagged(db_id, spam, "low", "rule")
                else:
                    pending.append((db_id, event))

        should_flush = pending and (
            len(pending) >= monitor_config.batch_size
            or (time.monotonic() - last_flush) >= monitor_config.batch_seconds
        )
        if should_flush:
            comments = [e.text for _, e in pending]
            try:
                flags = monitor_agent.review_batch(comments)
            except Exception as exc:  # noqa: BLE001 — an LLM hiccup must not kill the monitor
                print(f"[monitor] LLM review failed: {exc}")
                flags = []

            for flag in flags:
                idx = flag.get("index")
                if idx is None or not (0 <= idx < len(pending)):
                    continue
                db_id, event = pending[idx]
                reason = flag.get("reason", "")
                severity = flag.get("severity", "medium")
                store.mark_flagged(db_id, reason, severity, "llm")
                send_alert(
                    monitor_config,
                    f"[{event.room}] {event.nickname}: {event.text} ({severity}: {reason})",
                )

            pending = []
            last_flush = time.monotonic()


async def run_monitor(watchlist_override: list[str] | None = None) -> None:
    llm_config = load_config()
    monitor_config = load_monitor_config(watchlist_override)

    if not monitor_config.watchlist:
        raise ValueError(
            "No accounts to watch — pass one on the command line "
            "(python monitor_main.py <username-or-tiktok-url>) or set "
            "TIKTOK_WATCHLIST in .env"
        )

    queue: "asyncio.Queue[Event]" = asyncio.Queue(maxsize=1000)
    store = EventStore(monitor_config.db_path)
    monitor_agent = MonitorAgent(LLMClient(llm_config))

    watchers = [RoomWatcher(username, queue) for username in monitor_config.watchlist]
    print(f"Watching: {', '.join(monitor_config.watchlist)}")
    print(f"Logging to: {monitor_config.db_path}")

    tasks = [asyncio.create_task(w.run()) for w in watchers]
    tasks.append(asyncio.create_task(_batch_flusher(queue, store, monitor_config, monitor_agent)))

    try:
        await asyncio.gather(*tasks)
    finally:
        store.close()
