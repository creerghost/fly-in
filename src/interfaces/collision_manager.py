"""Collision manager interface."""

from abc import ABC, abstractmethod


class Manager(ABC):
    """Interface for managing collision and reservation logic."""

    @abstractmethod
    def is_zone_available(
        self,
        zone_name: str,
        turn: int,
        max_capacity: int,
    ) -> bool:
        """Check if a specific zone has remaining capacity for a given turn."""

    @abstractmethod
    def is_link_available(
        self,
        zone1: str,
        zone2: str,
        turn: int,
        max_link_capacity: int,
    ) -> bool:
        """
        Check if a connection link between two zones has remaining capacity.

        Checks if it has remaining capacity during a given turn.
        """

    @abstractmethod
    def register_path(self, path: list[tuple[str, int]]) -> None:
        """
        Commit a path to the reservation table.

        Locks zone and link capacities for specific turns.
        """
