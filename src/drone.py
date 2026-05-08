from typing import List, Any


class Drone:
    def __init__(self, drone_id: str, start_location: str):
        self.id = drone_id
        self.current_location = start_location
        self.path: List[Any] = []
        self.status = "waiting"  # waiting/in_flight/finished
