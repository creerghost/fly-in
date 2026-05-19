from typing import List, Tuple


class Drone:
    def __init__(self, drone_id: str, start_location: str) -> None:
        """
        Initialize a Drone with its unique ID and starting location.
        """
        self.id = drone_id
        self.current_location = start_location
        self.path: List[Tuple[str, int]] = []
        self.status = "waiting"  # waiting/in_flight/finished
        self.draw_pos: Tuple[float, float] = (0.0, 0.0)
        self.prev_pos: Tuple[float, float] = (0.0, 0.0)
        self.next_pos: Tuple[float, float] = (0.0, 0.0)
        self.animation_ready = False
