from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Memory:
    tick: int
    description: str
    importance: int = 5
    tags: list[str] = field(default_factory=list)


class MemoryStream:
    def __init__(self, db_path: str, mortal_name: str):
        self.db_path = db_path
        self.mortal_name = mortal_name
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
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mortal_name TEXT NOT NULL,
                    tick INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    importance INTEGER NOT NULL,
                    tags TEXT NOT NULL
                )
                """
            )

    def add(
        self,
        tick: int,
        description: str,
        importance: int = 5,
        tags: list[str] | None = None,
    ) -> None:
        tags = tags or []
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO memories (mortal_name, tick, description, importance, tags)
                VALUES (?, ?, ?, ?, ?)
                """,
                (self.mortal_name, tick, description, importance, json.dumps(tags)),
            )

    def retrieve(self, current_tick: int, limit: int = 10) -> list[Memory]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT tick, description, importance, tags
                FROM memories
                WHERE mortal_name = ?
                """,
                (self.mortal_name,),
            ).fetchall()
        scored = []
        for row in rows:
            age = max(0, current_tick - row["tick"])
            score = row["importance"] + (1.0 / (1 + age * 0.1))
            scored.append(
                (
                    score,
                    Memory(
                        tick=row["tick"],
                        description=row["description"],
                        importance=row["importance"],
                        tags=json.loads(row["tags"]),
                    ),
                )
            )
        scored.sort(key=lambda item: item[0], reverse=True)
        return [memory for _, memory in scored[:limit]]

    def to_context_string(self, current_tick: int, limit: int = 8) -> str:
        memories = self.retrieve(current_tick=current_tick, limit=limit)
        if not memories:
            return "- No significant memories yet."
        return "\n".join(
            f"- [Tick {memory.tick}] {memory.description} (importance {memory.importance})"
            for memory in memories
        )

    def count(self) -> int:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS total FROM memories WHERE mortal_name = ?",
                (self.mortal_name,),
            ).fetchone()
        return int(row["total"])

    def recent(self, limit: int = 20) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT tick, description, importance, tags
                FROM memories
                WHERE mortal_name = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (self.mortal_name, limit),
            ).fetchall()
        return [
            {
                "tick": row["tick"],
                "description": row["description"],
                "importance": row["importance"],
                "tags": json.loads(row["tags"]),
            }
            for row in rows
        ]
