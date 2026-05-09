from typing import List, Tuple


class Drone:
    def __init__(self, drone_id: str, start_location: str):
        self.id = drone_id
        self.current_location = start_location
        self.path: List[Tuple[str, int]] = []
        self.status = "waiting"  # waiting/in_flight/finished
