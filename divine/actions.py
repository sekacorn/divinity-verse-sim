from __future__ import annotations

import random

from mortals.agent import Mortal
from mortals.archetypes import list_archetypes
from world.events import WorldEvent


ACTION_COSTS = {
    "smite": 20,
    "bless": 15,
    "decree": 10,
    "spawn": 25,
    "curse": 20,
    "inspire": 10,
}

NAME_PARTS = {
    "first": ["Ael", "Bram", "Cira", "Dain", "Elra", "Fen", "Galen", "Hollis"],
    "last": ["wick", "mere", "thorn", "vale", "croft", "shade", "briar", "fall"],
}


def _generate_name(world_state) -> str:
    existing = {mortal["name"] for mortal in world_state.get_all_mortals(alive_only=False)}
    for _ in range(50):
        name = random.choice(NAME_PARTS["first"]) + random.choice(NAME_PARTS["last"])
        if name not in existing:
            return name
    return f"Nameless{len(existing) + 1}"


def smite(deity, target_or_message, world_state, event_bus, tick, **kwargs) -> str:
    target = world_state.get_mortal(target_or_message)
    if not target or not target["alive"]:
        raise ValueError("Target mortal not found.")
    deity.spend_energy(ACTION_COSTS["smite"])
    world_state.kill_mortal(target["name"])
    description = f"{target['name']} was struck down by {deity.name}."
    deity.log_intervention(tick, "smite", target["name"], description)
    event_bus.emit(
        WorldEvent(
            tick=tick,
            source_type="deity",
            source_name=deity.name,
            event_type="death",
            description=description,
            target_name=target["name"],
            metadata={"action": "smite"},
        )
    )
    return description


def bless(deity, target_or_message, world_state, event_bus, tick, **kwargs) -> str:
    target = world_state.get_mortal(target_or_message)
    if not target or not target["alive"]:
        raise ValueError("Target mortal not found.")
    deity.spend_energy(ACTION_COSTS["bless"])
    gift = kwargs.get("message", "").strip()
    target["needs"]["purpose"] = min(100, target["needs"]["purpose"] + 30)
    target["needs"]["rest"] = min(100, target["needs"]["rest"] + 20)
    world_state.update_mortal(target["name"], needs=target["needs"])
    mortal = Mortal(target["name"], target["archetype"], world_state.db_path, target["tick_born"])
    mortal.needs = target["needs"]
    mortal.receive_divine_act("blessing", gift or "Warm favor descends from above.", tick)
    description = f"{deity.name} blessed {target['name']}."
    if gift:
        description += f" Gift: {gift}"
    deity.log_intervention(tick, "bless", target["name"], description)
    event_bus.emit(
        WorldEvent(
            tick=tick,
            source_type="deity",
            source_name=deity.name,
            event_type="divine_act",
            description=description,
            target_name=target["name"],
            metadata={"action": "bless", "gift": gift},
        )
    )
    return description


def decree(deity, target_or_message, world_state, event_bus, tick, **kwargs) -> str:
    message = (target_or_message or kwargs.get("message") or "").strip()
    if not message:
        raise ValueError("Decree requires a message.")
    deity.spend_energy(ACTION_COSTS["decree"])
    description = f"Decree of {deity.name}: {message}"
    deity.log_intervention(tick, "decree", "*", description)
    event_bus.emit(
        WorldEvent(
            tick=tick,
            source_type="deity",
            source_name=deity.name,
            event_type="decree",
            description=description,
            metadata={"action": "decree"},
        )
    )
    return description


def spawn(deity, target_or_message, world_state, event_bus, tick, **kwargs) -> str:
    archetype = (target_or_message or "").strip().lower()
    if archetype not in list_archetypes():
        raise ValueError("Spawn requires a valid archetype.")
    deity.spend_energy(ACTION_COSTS["spawn"])
    name = _generate_name(world_state)
    mortal = Mortal(name, archetype, world_state.db_path, tick_born=tick)
    world_state.add_mortal(mortal.to_dict())
    description = f"{deity.name} shaped {name}, a new {archetype}, into the world."
    deity.log_intervention(tick, "spawn", name, description)
    event_bus.emit(
        WorldEvent(
            tick=tick,
            source_type="deity",
            source_name=deity.name,
            event_type="birth",
            description=description,
            target_name=name,
            metadata={"action": "spawn", "archetype": archetype},
        )
    )
    return description


def curse(deity, target_or_message, world_state, event_bus, tick, **kwargs) -> str:
    target = world_state.get_mortal(target_or_message)
    if not target or not target["alive"]:
        raise ValueError("Target mortal not found.")
    deity.spend_energy(ACTION_COSTS["curse"])
    target["needs"] = {key: max(0, value - 40) for key, value in target["needs"].items()}
    world_state.update_mortal(target["name"], needs=target["needs"])
    mortal = Mortal(target["name"], target["archetype"], world_state.db_path, target["tick_born"])
    mortal.needs = target["needs"]
    mortal.receive_divine_act("curse", "A cold misfortune grips my body and spirit.", tick)
    description = f"{deity.name} cursed {target['name']}."
    deity.log_intervention(tick, "curse", target["name"], description)
    event_bus.emit(
        WorldEvent(
            tick=tick,
            source_type="deity",
            source_name=deity.name,
            event_type="divine_act",
            description=description,
            target_name=target["name"],
            metadata={"action": "curse"},
        )
    )
    return description


def inspire(deity, target_or_message, world_state, event_bus, tick, **kwargs) -> str:
    target = world_state.get_mortal(target_or_message)
    if not target or not target["alive"]:
        raise ValueError("Target mortal not found.")
    deity.spend_energy(ACTION_COSTS["inspire"])
    target["needs"]["purpose"] = min(100, target["needs"]["purpose"] + 50)
    world_state.update_mortal(target["name"], needs=target["needs"])
    mortal = Mortal(target["name"], target["archetype"], world_state.db_path, target["tick_born"])
    mortal.needs = target["needs"]
    mortal.receive_divine_act(
        "inspiration",
        "A blazing certainty fills me with purpose.",
        tick,
        importance=9,
    )
    description = f"{deity.name} inspired {target['name']} with fierce purpose."
    deity.log_intervention(tick, "inspire", target["name"], description)
    event_bus.emit(
        WorldEvent(
            tick=tick,
            source_type="deity",
            source_name=deity.name,
            event_type="divine_act",
            description=description,
            target_name=target["name"],
            metadata={"action": "inspire"},
        )
    )
    return description


DIVINE_ACTIONS = {
    "smite": smite,
    "bless": bless,
    "decree": decree,
    "spawn": spawn,
    "curse": curse,
    "inspire": inspire,
}


def get_action(name: str):
    return DIVINE_ACTIONS[name]


def list_actions() -> list[str]:
    return sorted(DIVINE_ACTIONS.keys())
