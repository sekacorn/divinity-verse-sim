from __future__ import annotations

import json
import sqlite3
from pathlib import Path


class WorldState:
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._seed_props()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS mortals (
                    name TEXT PRIMARY KEY,
                    archetype TEXT NOT NULL,
                    traits TEXT NOT NULL,
                    location TEXT NOT NULL,
                    needs TEXT NOT NULL,
                    alive INTEGER NOT NULL DEFAULT 1,
                    tick_born INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS world_props (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )

    def _seed_props(self) -> None:
        defaults = {
            "world_name": "Evershade",
            "population_limit": "10",
            "current_era": "Age of Embers",
            "current_tick": "0",
        }
        with self._connect() as conn:
            for key, value in defaults.items():
                conn.execute(
                    "INSERT OR IGNORE INTO world_props (key, value) VALUES (?, ?)",
                    (key, value),
                )

    def add_mortal(self, mortal: dict) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO mortals (
                    name, archetype, traits, location, needs, alive, tick_born
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    mortal["name"],
                    mortal["archetype"],
                    json.dumps(mortal["traits"]),
                    mortal["location"],
                    json.dumps(mortal["needs"]),
                    int(mortal.get("alive", 1)),
                    mortal.get("tick_born", 0),
                ),
            )

    def get_mortal(self, name: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM mortals WHERE name = ?",
                (name,),
            ).fetchone()
        return self._row_to_mortal(row) if row else None

    def get_all_mortals(self, alive_only: bool = True) -> list[dict]:
        query = "SELECT * FROM mortals"
        if alive_only:
            query += " WHERE alive = 1"
        query += " ORDER BY tick_born, name"
        with self._connect() as conn:
            rows = conn.execute(query).fetchall()
        return [self._row_to_mortal(row) for row in rows]

    def update_mortal(self, name: str, **fields) -> None:
        if not fields:
            return
        serialized = {}
        for key, value in fields.items():
            serialized[key] = json.dumps(value) if key in {"traits", "needs"} else value
        assignments = ", ".join(f"{key} = ?" for key in serialized)
        values = list(serialized.values()) + [name]
        with self._connect() as conn:
            conn.execute(f"UPDATE mortals SET {assignments} WHERE name = ?", values)

    def kill_mortal(self, name: str) -> None:
        self.update_mortal(name, alive=0)

    def get_prop(self, key: str, default: str | None = None) -> str | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT value FROM world_props WHERE key = ?",
                (key,),
            ).fetchone()
        return row["value"] if row else default

    def set_prop(self, key: str, value: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO world_props (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, value),
            )

    @staticmethod
    def _row_to_mortal(row: sqlite3.Row) -> dict:
        return {
            "name": row["name"],
            "archetype": row["archetype"],
            "traits": json.loads(row["traits"]),
            "location": row["location"],
            "needs": json.loads(row["needs"]),
            "alive": bool(row["alive"]),
            "tick_born": row["tick_born"],
        }
