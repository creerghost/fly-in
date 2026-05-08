from typing import Tuple, Dict, List, Any, Optional
from dataclasses import dataclass, field
from src.network import Network


@dataclass(order=True)
class TemporalState:
    f_cost: int
    g_cost: int = field(compare=False)
    h_cost: int = field(compare=False)
    turn: int = field(compare=False)
    zone_name: str = field(compare=False)
    parent: Optional['TemporalState'] = field(default=None, compare=False)


class ReservationTable():
    def __init__(self) -> None:
        self.zone_schedule: Dict[Tuple[str, int], int] = {}
        self.link_schedule: Dict[Tuple[Tuple[str, str], int], int] = {}

    def is_zone_available(self, zone_name: str,
                          turn: int, max_capacity: int) -> bool:
        # Returns True if current reservations are below the max capacity
        current_occupancy = self.zone_schedule.get((zone_name, turn), 0)
        return current_occupancy < max_capacity

    def is_link_available(self, zone1: str, zone2: str,
                          turn: int, max_link_capacity: int) -> bool:
        # Sort to handle bidirectional connection names uniformly
        link = tuple(sorted([zone1, zone2]))
        current_traffic = self.link_schedule.get((link, turn), 0)
        return current_traffic < max_link_capacity

    def register_path(self, path: List[Tuple[str, int]]) -> None:
        for zone_name, turn in path:
            current_occupancy = self.zone_schedule.get((zone_name, turn), 0)
            self.zone_schedule[(zone_name, turn)] = current_occupancy + 1
        # Note: We will expand this to register link usage later when routing!


class SpaceTimePathfinder:
    def __init__(self, network: Network,
                 reservations: ReservationTable) -> None:
        self.network = network
        self.reservations = reservations

    def calc_heuristic(self, current_zone: str, target_zone: str) -> int:
        pass

    def generate_valid_neighbors(self,
                                 current_state: TemporalState
                                 ) -> List[TemporalState]:
        pass

    def find_routes(self,
                    start_zone: str,
                    end_zone: str
                    ) -> Optional[List[Tuple[str, int]]]:
        pass
