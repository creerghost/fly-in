from typing import Optional
from dataclasses import dataclass, field


@dataclass(order=True, slots=True)
class TemporalState():
    """
    A node in the space-time A* search graph, representing a drone's
    position (zone) at a specific turn with associated path costs.
    Ordered by f_cost for priority queue usage.
    """
    f_cost: float
    g_cost: float = field(compare=False)
    h_cost: float = field(compare=False)
    turn: int = field(compare=False)
    zone_name: str = field(compare=False)
    parent: Optional['TemporalState'] = field(default=None, compare=False)

    def __str__(self) -> str:
        return f"State({self.zone_name} @ turn {self.turn})"

    def __repr__(self) -> str:
        return (f"<TemporalState {self.zone_name} T={self.turn} "
                f"f={self.f_cost} g={self.g_cost}>")
