from typing import Dict, Tuple, List
from collections import defaultdict
from ...interfaces import Manager


class CollisionManager(Manager):
    """
    Maintains a schedule of zone and link capacities per turn
    to prevent collisions.
    """
    def __init__(self) -> None:
        """
        Initialize empty schedules for zones and links.
        """
        self.zone_schedule: Dict[Tuple[str, int], int] = defaultdict(int)
        self.link_schedule: Dict[Tuple[Tuple[str, str], int], int] = \
            defaultdict(int)

    @staticmethod
    def _normalize_link(zone1: str, zone2: str) -> Tuple[str, str]:
        """
        Normalize a link key so that (A, B) and (B, A) map to the same
        entry.
        """
        return (min(zone1, zone2), max(zone1, zone2))

    def is_zone_available(self, zone_name: str,
                          turn: int, max_capacity: int) -> bool:
        """
        Check if a specific zone has remaining capacity during a given turn.
        """
        return self.zone_schedule[(zone_name, turn)] < max_capacity

    def is_link_available(self, zone1: str, zone2: str,
                          turn: int, max_link_capacity: int) -> bool:
        """
        Check if a connection link between two zones has remaining
        capacity during a given turn.
        """
        link = self._normalize_link(zone1, zone2)
        return self.link_schedule[(link, turn)] < max_link_capacity

    def register_path(self, path: List[Tuple[str, int]]) -> None:
        """
        Commit a path to the reservation table, locking zone and link
        capacities for specific turns.
        """
        # register the zone occupancy for each turn
        for zone_name, turn in path:
            self.zone_schedule[(zone_name, turn)] += 1

        # look at consecutive steps to register link (connection) usage
        for curr_step, next_step in zip(path[:-1], path[1:]):
            curr_zone_name, curr_turn = curr_step
            next_zone_name, next_turn = next_step

            # Ignore wait actions
            if curr_zone_name == next_zone_name:
                continue

            link = self._normalize_link(curr_zone_name, next_zone_name)
            # Reserve the link for all turns spent in transit
            for t in range(curr_turn + 1, next_turn + 1):
                self.link_schedule[(link, t)] += 1
