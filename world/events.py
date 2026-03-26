from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


@dataclass
class WorldEvent:
    tick: int
    source_type: str
    source_name: str
    event_type: str
    description: str
    target_name: str | None = None
    metadata: dict = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class EventBus:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.subscribers: list[Callable[[WorldEvent], None]] = []
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tick INTEGER NOT NULL,
                    source_type TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    target_name TEXT,
                    metadata TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
                """
            )

    def emit(self, event: WorldEvent) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO events (
                    tick, source_type, source_name, event_type, description,
                    target_name, metadata, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.tick,
                    event.source_type,
                    event.source_name,
                    event.event_type,
                    event.description,
                    event.target_name,
                    json.dumps(event.metadata),
                    event.timestamp,
                ),
            )
        for callback in list(self.subscribers):
            callback(event)

    def subscribe(self, callback: Callable[[WorldEvent], None]) -> None:
        self.subscribers.append(callback)

    def get_recent(self, limit: int = 20) -> list[WorldEvent]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT tick, source_type, source_name, event_type, description,
                       target_name, metadata, timestamp
                FROM events
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            WorldEvent(
                tick=row["tick"],
                source_type=row["source_type"],
                source_name=row["source_name"],
                event_type=row["event_type"],
                description=row["description"],
                target_name=row["target_name"],
                metadata=json.loads(row["metadata"] or "{}"),
                timestamp=row["timestamp"],
            )
            for row in rows
        ]

    def get_lore(self, limit: int = 50) -> str:
        events = reversed(self.get_recent(limit=limit))
        return "\n".join(
            f"[Tick {event.tick}] {event.source_name}: {event.description}"
            for event in events
        )

    def get_latest_tick(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT MAX(tick) AS latest_tick FROM events").fetchone()
        latest = row["latest_tick"] if row else None
        return int(latest or 0)
