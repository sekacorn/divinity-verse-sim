from dataclasses import dataclass


@dataclass
class SimClock:
    tick: int = 0

    @property
    def day(self) -> int:
        return self.tick // 24

    @property
    def hour(self) -> int:
        return self.tick % 24

    @property
    def time_of_day(self) -> str:
        hour = self.hour
        if 6 <= hour < 12:
            return "morning"
        if 12 <= hour < 17:
            return "afternoon"
        if 17 <= hour < 21:
            return "evening"
        return "night"

    def advance(self, n: int = 1) -> int:
        self.tick += max(0, int(n))
        return self.tick

    def __str__(self) -> str:
        return f"Day {self.day}, Hour {self.hour:02d}:00 ({self.time_of_day})"
