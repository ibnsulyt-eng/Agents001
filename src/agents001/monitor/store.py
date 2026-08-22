"""SQLite event log for monitored TikTok Live rooms — zero extra dependencies."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass
class Event:
    room: str
    event_type: str  # comment | gift | join | like | connect | disconnect
    user_id: str
    nickname: str
    text: str
    timestamp: float
    flagged: bool = False
    flag_reason: str = ""
    flag_severity: str = ""
    flag_source: str = ""


class EventStore:
    def __init__(self, db_path: str):
        self._conn = sqlite3.connect(db_path)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room TEXT NOT NULL,
                event_type TEXT NOT NULL,
                user_id TEXT,
                nickname TEXT,
                text TEXT,
                timestamp REAL NOT NULL,
                flagged INTEGER DEFAULT 0,
                flag_reason TEXT,
                flag_severity TEXT,
                flag_source TEXT
            )
            """
        )
        self._conn.commit()

    def add(self, event: Event) -> int:
        cur = self._conn.execute(
            """
            INSERT INTO events
                (room, event_type, user_id, nickname, text, timestamp,
                 flagged, flag_reason, flag_severity, flag_source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.room, event.event_type, event.user_id, event.nickname,
                event.text, event.timestamp, int(event.flagged),
                event.flag_reason, event.flag_severity, event.flag_source,
            ),
        )
        self._conn.commit()
        return cur.lastrowid

    def mark_flagged(self, event_id: int, reason: str, severity: str, source: str) -> None:
        self._conn.execute(
            "UPDATE events SET flagged=1, flag_reason=?, flag_severity=?, flag_source=? WHERE id=?",
            (reason, severity, source, event_id),
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()
