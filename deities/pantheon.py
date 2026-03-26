from __future__ import annotations

import json
from pathlib import Path

from deities.deity import Deity


class Pantheon:
    def __init__(self, contributors_dir: str):
        self.contributors_dir = Path(contributors_dir)
        self.deities: dict[str, Deity] = {}

    def load_all(self) -> list[Deity]:
        self.contributors_dir.mkdir(parents=True, exist_ok=True)
        for path in self.contributors_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if data.get("name") == "YourNameHere":
                    continue
                deity = Deity(**data)
                self.deities[deity.name] = deity
            except Exception:
                continue
        return self.list_deities()

    def get(self, name: str) -> Deity | None:
        return self.deities.get(name)

    def add(self, deity: Deity) -> None:
        self.deities[deity.name] = deity

    def list_deities(self) -> list[Deity]:
        return list(self.deities.values())

    def tick_restore(self) -> None:
        for deity in self.deities.values():
            deity.restore_energy(5)
