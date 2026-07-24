from typing import List, Tuple
from enum import StrEnum
from dataclasses import dataclass, field


class DroneStatus(StrEnum):
    WAITING = "waiting"
    IN_FLIGHT = "in_flight"
    FINISHED = "finished"


@dataclass(slots=True)
class Drone:
    """
    Initialize a Drone with its unique ID and starting location.
    """
    id: str
    current_location: str
    path: List[Tuple[str, int]] = field(default_factory=list)
    status: DroneStatus = field(default=DroneStatus.WAITING)
    _draw_pos: Tuple[float, float] = field(default=(0.0, 0.0))
    _prev_pos: Tuple[float, float] = field(default=(0.0, 0.0))
    _next_pos: Tuple[float, float] = field(default=(0.0, 0.0))
    _animation_ready: bool = field(default=False)

    def __str__(self) -> str:
        return f"{self.id} @ {self.current_location} ({self.status.name})"

    def __repr__(self) -> str:
        return (f"Drone('{self.id}', loc='{self.current_location}', "
                f"status='{self.status.name}')")

    @classmethod
    def create_fleet(cls, count: int, start_location: str) -> List['Drone']:
        return [cls(f"D{i + 1}", start_location) for i in range(count)]

    def location_at_turn(self, turn: int) -> str:
        if not self.path or turn >= self.path[-1][1]:
            return self.path[-1][0] if self.path else self.current_location
        for curr_step, next_step in zip(self.path[:-1], self.path[1:]):
            curr_zone, curr_turn = curr_step
            next_zone, next_turn = next_step
            if turn == curr_turn:
                return curr_zone
            elif curr_turn < turn < next_turn:
                if curr_zone == next_zone:
                    return curr_zone
                else:
                    return f"{curr_zone}-{next_zone}"
        return self.path[-1][0]
