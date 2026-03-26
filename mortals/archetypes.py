from __future__ import annotations

import random


ARCHETYPES = {
    "farmer": {
        "traits": ["hardworking", "superstitious", "patient"],
        "location": "wheat fields",
        "description": "Tends the valley soil and watches the skies for omens.",
    },
    "merchant": {
        "traits": ["shrewd", "sociable", "greedy"],
        "location": "market square",
        "description": "Trades with charm, caution, and a sharp eye for profit.",
    },
    "scholar": {
        "traits": ["curious", "bookish", "skeptical"],
        "location": "library",
        "description": "Seeks truth in brittle scrolls and quiet observation.",
    },
    "guard": {
        "traits": ["loyal", "suspicious", "disciplined"],
        "location": "city gate",
        "description": "Keeps watch over the town and mistrusts easy answers.",
    },
    "wanderer": {
        "traits": ["restless", "perceptive", "unlucky"],
        "location": "road outside town",
        "description": "Moves with the horizon and survives by instinct.",
    },
    "priest": {
        "traits": ["devout", "manipulative", "comforting"],
        "location": "temple",
        "description": "Guides souls while quietly shaping belief to advantage.",
    },
    "blacksmith": {
        "traits": ["strong", "pragmatic", "stubborn"],
        "location": "forge",
        "description": "Works iron, fire, and long grudges into useful forms.",
    },
    "thief": {
        "traits": ["cunning", "cowardly", "opportunistic"],
        "location": "shadows near the market",
        "description": "Lives on whispers, shortcuts, and narrow escapes.",
    },
}


def get_archetype(name: str) -> dict:
    return ARCHETYPES[name]


def random_archetype() -> tuple[str, dict]:
    name = random.choice(list(ARCHETYPES.keys()))
    return name, ARCHETYPES[name]


def list_archetypes() -> list[str]:
    return sorted(ARCHETYPES.keys())
