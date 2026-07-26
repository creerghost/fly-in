"""Pathfinding algorithm interface."""

from abc import ABC, abstractmethod


class Pathfinder(ABC):
    """Interface for Multi-Agent Pathfinding algorithms."""

    @abstractmethod
    def find_routes(
        self, start_zone: str, end_zone: str
    ) -> list[tuple[str, int]] | None:
        """
        Find a valid path from start_zone to end_zone, avoiding collisions.

        Returns a list of (zone_name, turn) tuples representing the path,
        or None if no path is found.
        """
