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
