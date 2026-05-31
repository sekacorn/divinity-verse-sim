from __future__ import annotations

import asyncio
import os
import time
from dataclasses import dataclass
from pathlib import Path

from api.sse import push_event
from deities.deity import Deity
from deities.pantheon import Pantheon
from divine.actions import ACTION_COSTS, get_action
from mortals.agent import Mortal
from world.clock import SimClock
from world.events import EventBus, WorldEvent
from world.state import WorldState


@dataclass
class SimulationRuntime:
    world: WorldState
    clock: SimClock
    events: EventBus
    pantheon: Pantheon
    db_path: str
    contributors_dir: str
    active_deity_name: str

    @property
    def active_deity(self) -> Deity:
        deity = self.pantheon.get(self.active_deity_name)
        if deity is None:
            raise ValueError("Active deity is not configured.")
        return deity


def create_runtime(base_dir: str) -> SimulationRuntime:
    data_dir = Path(base_dir) / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    db_path = str(data_dir / "world.db")
    world = WorldState(db_path=db_path)
    events = EventBus(db_path=db_path)
    saved_tick = int(world.get_prop("current_tick", "0") or 0)
    latest_tick = events.get_latest_tick()
    clock = SimClock(tick=max(saved_tick, latest_tick))
    world.set_prop("current_tick", str(clock.tick))
    pantheon = Pantheon(str(Path(base_dir) / "contributors"))
    pantheon.load_all()
    if not pantheon.list_deities():
        pantheon.add(Deity(name="Corn", title="The Architect", domain="knowledge"))
    runtime = SimulationRuntime(
        world=world,
        clock=clock,
        events=events,
        pantheon=pantheon,
        db_path=db_path,
        contributors_dir=str(Path(base_dir) / "contributors"),
        active_deity_name=pantheon.list_deities()[0].name,
    )
    seed_world(runtime)
    return runtime


def seed_world(runtime: SimulationRuntime) -> None:
    if runtime.world.get_all_mortals(alive_only=False):
        return
    starters = [
        ("Aldric", "farmer"),
        ("Mira", "merchant"),
        ("Oswin", "scholar"),
        ("Brin", "guard"),
    ]
    for name, archetype in starters:
        mortal = Mortal(name, archetype, runtime.db_path, tick_born=0)
        runtime.world.add_mortal(mortal.to_dict())


def world_context(runtime: SimulationRuntime) -> str:
    world_name = runtime.world.get_prop("world_name", "Evershade")
    era = runtime.world.get_prop("current_era", "Age of Embers")
    return f"World: {world_name}\nEra: {era}\nTime: {runtime.clock}"


def recent_event_context(runtime: SimulationRuntime, limit: int = 8) -> str:
    recent = reversed(runtime.events.get_recent(limit=limit))
    lines = [f"- [Tick {event.tick}] {event.source_name}: {event.description}" for event in recent]
    return "\n".join(lines)


def mortal_from_record(runtime: SimulationRuntime, record: dict) -> Mortal:
    mortal = Mortal(record["name"], record["archetype"], runtime.db_path, record["tick_born"])
    mortal.location = record["location"]
    mortal.needs = record["needs"]
    return mortal


def _push_sync(data: dict) -> None:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(push_event(data))
        return
    loop.create_task(push_event(data))


def run_ticks(runtime: SimulationRuntime, n: int = 1) -> list[str]:
    if n < 0:
        raise ValueError("Tick count cannot be negative.")
    if n == 0:
        return []
    outputs: list[str] = []
    delay = float(os.getenv("SIM_TICK_DELAY", "0") or 0)
    for _ in range(n):
        runtime.clock.advance(1)
        runtime.world.set_prop("current_tick", str(runtime.clock.tick))
        runtime.pantheon.tick_restore()
        current_tick = runtime.clock.tick
        living = runtime.world.get_all_mortals(alive_only=True)
        for record in living:
            mortal = mortal_from_record(runtime, record)
            action_text = mortal.think_and_act(
                current_tick=current_tick,
                world_context=world_context(runtime),
                recent_events=recent_event_context(runtime),
            )
            mortal.update_needs({"hunger": -3, "rest": -2, "purpose": -1})
            runtime.world.update_mortal(record["name"], needs=mortal.needs)
            runtime.events.emit(
                WorldEvent(
                    tick=current_tick,
                    source_type="mortal",
                    source_name=mortal.name,
                    event_type="action",
                    description=action_text,
                    metadata={"archetype": mortal.archetype},
                )
            )
            outputs.append(f"[Tick {current_tick}] {mortal.name}: {action_text}")
            _push_sync({"type": "action", "tick": current_tick, "mortal": mortal.name, "text": action_text})
        _push_sync({"type": "tick", "tick": current_tick})
        if delay > 0:
            time.sleep(delay)
    return outputs


def execute_divine_action(
    runtime: SimulationRuntime,
    deity_name: str,
    action_name: str,
    target: str = "",
    message: str = "",
) -> str:
    if action_name not in ACTION_COSTS:
        raise ValueError(f"Unknown divine action: {action_name}")
    deity = runtime.pantheon.get(deity_name)
    if deity is None:
        raise ValueError(f"Deity '{deity_name}' not found.")
    cost = ACTION_COSTS[action_name]
    if not deity.can_act(cost):
        raise ValueError(
            f"{deity.name} lacks the energy for {action_name} ({deity.divine_energy}/{cost})."
        )
    if action_name == "spawn":
        population_limit = int(
            os.getenv("SIM_MAX_MORTALS", runtime.world.get_prop("population_limit", "10"))
        )
        if len(runtime.world.get_all_mortals(alive_only=True)) >= population_limit:
            raise ValueError("Population cap reached. Spawn is blocked.")
    action = get_action(action_name)
    result = action(
        deity,
        message if action_name == "decree" else target,
        runtime.world,
        runtime.events,
        runtime.clock.tick,
        message=message,
    )
    _push_sync(
        {
            "type": "divine_act",
            "tick": runtime.clock.tick,
            "mortal": target,
            "text": result,
            "action": action_name,
        }
    )
    return result
