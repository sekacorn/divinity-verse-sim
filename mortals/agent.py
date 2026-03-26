from __future__ import annotations

import os

from anthropic import Anthropic

from mortals.archetypes import get_archetype
from mortals.memory import MemoryStream


class Mortal:
    def __init__(self, name: str, archetype: str, db_path: str, tick_born: int = 0):
        data = get_archetype(archetype)
        self.name = name
        self.archetype = archetype
        self.traits = list(data["traits"])
        self.location = data["location"]
        self.description = data["description"]
        self.tick_born = tick_born
        self.needs = {"hunger": 80, "rest": 80, "purpose": 80}
        self.memory = MemoryStream(db_path=db_path, mortal_name=name)
        self.model = os.getenv("SIM_MODEL", "claude-haiku-4-5-20251001")
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.client = Anthropic(api_key=api_key) if api_key else None

    def think_and_act(
        self,
        current_tick: int,
        world_context: str,
        recent_events: str,
    ) -> str:
        memory_context = self.memory.to_context_string(current_tick=current_tick, limit=8)
        prompt = f"""
You are {self.name}, a mortal in a fantasy village simulation.
Stay in character. Respond in 1-2 sentences. No fourth-wall breaking. No references to being AI.

Identity:
- Name: {self.name}
- Archetype: {self.archetype}
- Traits: {", ".join(self.traits)}
- Description: {self.description}
- Location: {self.location}
- Needs: hunger={self.needs['hunger']}, rest={self.needs['rest']}, purpose={self.needs['purpose']}
- Current tick: {current_tick}

World context:
{world_context}

Recent world events:
{recent_events or "- Nothing notable has happened yet."}

Memories:
{memory_context}

What do you do or say right now?
""".strip()

        fallback = f"{self.name} stands still, lost in thought."
        action = fallback
        if self.client:
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=150,
                    messages=[{"role": "user", "content": prompt}],
                )
                text_parts = [
                    block.text
                    for block in response.content
                    if getattr(block, "type", "") == "text"
                ]
                candidate = " ".join(part.strip() for part in text_parts).strip()
                if candidate:
                    action = candidate
            except Exception:
                action = fallback
        self.memory.add(
            tick=current_tick,
            description=action,
            importance=3,
            tags=["action", self.archetype],
        )
        return action

    def receive_divine_act(
        self,
        act_type: str,
        description: str,
        tick: int,
        importance: int = 8,
    ) -> None:
        self.memory.add(
            tick=tick,
            description=f"A divine {act_type} touched my life: {description}",
            importance=importance,
            tags=["divine", act_type],
        )

    def update_needs(self, delta: dict) -> dict:
        for key, change in delta.items():
            current = self.needs.get(key, 0)
            self.needs[key] = max(0, min(100, current + change))
        return self.needs

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "archetype": self.archetype,
            "traits": self.traits,
            "location": self.location,
            "needs": self.needs,
            "alive": True,
            "tick_born": self.tick_born,
        }
