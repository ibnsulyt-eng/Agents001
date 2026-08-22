"""Connects to one TikTok Live room and pushes normalized Events onto a shared queue.

Uses the unofficial `TikTokLive` client library (reverse-engineered, not an official
TikTok API — see https://github.com/isaackogan/TikTokLive). It only reads what's already
publicly visible to anyone watching the live room: comments, gifts, joins, likes — no
login or private data involved. Because it's unofficial, TikTok protocol changes can
break it; if events stop firing, check that project for updates.
"""

from __future__ import annotations

import asyncio
import time

from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent, ConnectEvent, DisconnectEvent, GiftEvent, JoinEvent, LikeEvent

from .store import Event


class RoomWatcher:
    def __init__(self, username: str, queue: "asyncio.Queue[Event]"):
        self.username = username.lstrip("@")
        self._queue = queue
        self._client = TikTokLiveClient(unique_id=f"@{self.username}")
        self._register_handlers()

    def _put(self, event: Event) -> None:
        try:
            self._queue.put_nowait(event)
        except asyncio.QueueFull:
            pass  # drop under extreme load rather than block the live feed

    def _register_handlers(self) -> None:
        client = self._client
        room = self.username

        @client.on(ConnectEvent)
        async def on_connect(_):
            print(f"[{room}] connected")

        @client.on(DisconnectEvent)
        async def on_disconnect(_):
            print(f"[{room}] disconnected (stream likely ended)")

        @client.on(CommentEvent)
        async def on_comment(event: CommentEvent):
            self._put(
                Event(
                    room=room,
                    event_type="comment",
                    user_id=str(getattr(event.user, "id", "")),
                    nickname=getattr(event.user, "nickname", ""),
                    text=event.content,
                    timestamp=time.time(),
                )
            )

        @client.on(GiftEvent)
        async def on_gift(event: GiftEvent):
            self._put(
                Event(
                    room=room,
                    event_type="gift",
                    user_id=str(getattr(event.user, "id", "")),
                    nickname=getattr(event.user, "nickname", ""),
                    text=getattr(getattr(event, "gift", None), "name", ""),
                    timestamp=time.time(),
                )
            )

        @client.on(JoinEvent)
        async def on_join(event: JoinEvent):
            self._put(
                Event(
                    room=room,
                    event_type="join",
                    user_id=str(getattr(event.user, "id", "")),
                    nickname=getattr(event.user, "nickname", ""),
                    text="",
                    timestamp=time.time(),
                )
            )

        @client.on(LikeEvent)
        async def on_like(event: LikeEvent):
            self._put(
                Event(
                    room=room,
                    event_type="like",
                    user_id=str(getattr(event.user, "id", "")),
                    nickname=getattr(event.user, "nickname", ""),
                    text=str(getattr(event, "count", "")),
                    timestamp=time.time(),
                )
            )

    async def run(self) -> None:
        """Connect and stay connected; reconnect with backoff if the room drops or errors."""
        while True:
            try:
                await self._client.start()
            except Exception as exc:  # noqa: BLE001 — one bad room must not kill the others
                print(f"[{self.username}] error: {exc}")
            print(f"[{self.username}] retrying in 30s...")
            await asyncio.sleep(30)
