from abc import ABC, abstractmethod
from typing import List, Tuple


class Manager(ABC):
    """
    Interface for managing collision and reservation logic in pathfinding.
    """

    @abstractmethod
    def is_zone_available(self, zone_name: str,
                          turn: int, max_capacity: int) -> bool:
        """
        Check if a specific zone has remaining capacity during a given turn.
        """
        pass

    @abstractmethod
    def is_link_available(self, zone1: str, zone2: str,
                          turn: int, max_link_capacity: int) -> bool:
        """
        Check if a connection link between two zones has remaining
        capacity during a given turn.
        """
        pass

    @abstractmethod
    def register_path(self, path: List[Tuple[str, int]]) -> None:
        """
        Commit a path to the reservation table, locking zone and link
        capacities for specific turns.
        """
        pass
