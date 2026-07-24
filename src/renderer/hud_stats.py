from dataclasses import dataclass
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import Drone, Network


@dataclass
class HudStats:
    total_drones: int
    active_drones: int
    avg_turns: float
    total_cost: float

    def __str__(self) -> str:
        return (f"Stats(Total: {self.total_drones}, "
                f"Active: {self.active_drones}, "
                f"Avg Turns: {self.avg_turns:.1f}, "
                f"Cost: {self.total_cost:.1f})")

    def __repr__(self) -> str:
        return (f"HudStats(total={self.total_drones}, "
                f"active={self.active_drones}, "
                f"avg={self.avg_turns:.2f}, "
                f"cost={self.total_cost:.2f})")

    @classmethod
    def from_drones(
        cls, drones: List['Drone'], network: 'Network'
    ) -> 'HudStats':
        total_cost_stats: int = 0
        total_drones = len(drones)

        for d in drones:
            if not d.path:
                continue
            for curr_step, next_step in zip(d.path[:-1], d.path[1:]):
                prev_node = curr_step[0]
                next_node = next_step[0]
                if prev_node == next_node:
                    total_cost_stats += 1
                else:
                    zone = network[next_node]
                    total_cost_stats += zone.transit_time

        avg_turns = (sum(d.path[-1][1] for d in drones if d.path) /
                     total_drones if total_drones else 0.0)

        return cls(
            total_drones=total_drones,
            active_drones=0,
            avg_turns=avg_turns,
            total_cost=total_cost_stats
        )
