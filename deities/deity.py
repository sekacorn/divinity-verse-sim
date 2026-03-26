from __future__ import annotations

from dataclasses import dataclass, field


VALID_DOMAINS = {"knowledge", "chaos", "harvest", "war", "fate"}


@dataclass
class Deity:
    name: str
    title: str
    domain: str
    divine_energy: int = 100
    max_energy: int = 100
    color: str = "white"
    interventions: list[dict] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.domain not in VALID_DOMAINS:
            raise ValueError(f"Invalid domain: {self.domain}")

    def can_act(self, cost: int) -> bool:
        return self.divine_energy >= cost

    def spend_energy(self, cost: int) -> None:
        if not self.can_act(cost):
            raise ValueError("Insufficient divine energy.")
        self.divine_energy = max(0, self.divine_energy - cost)

    def restore_energy(self, amount: int = 5) -> None:
        self.divine_energy = min(self.max_energy, self.divine_energy + amount)

    def log_intervention(
        self,
        tick: int,
        action_type: str,
        target: str,
        description: str,
    ) -> None:
        self.interventions.append(
            {
                "tick": tick,
                "action_type": action_type,
                "target": target,
                "description": description,
            }
        )
