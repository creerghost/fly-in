"""Pathfinding algorithm interface."""

from abc import ABC, abstractmethod


class Pathfinder(ABC):
    """Interface for Multi-Agent Pathfinding algorithms."""

    def __init__(self, max_turns: int = 1000) -> None:
        """Initialize the pathfinder with a maximum turn limit."""
        self.max_turns = max_turns

    @abstractmethod
    def find_routes(
        self, start_zone: str, end_zone: str
    ) -> list[tuple[str, int]] | None:
        """
        Find a valid path from start_zone to end_zone, avoiding collisions.

        Returns a list of (zone_name, turn) tuples representing the path,
        or None if no path is found.
        """
