"""Simulation engine interface."""

from abc import ABC, abstractmethod

from ..models import Drone


class Engine(ABC):
    """Interface for the simulation engine."""

    @abstractmethod
    def run(self) -> None:
        """Execute the simulation."""

    @property
    @abstractmethod
    def drones(self) -> list[Drone]:
        """Return the list of drones managed by the engine."""
