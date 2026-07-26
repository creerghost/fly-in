"""Simulation engine interface."""

from abc import ABC, abstractmethod

from ..models import Drone
from .runnable import Runnable


class Engine(Runnable, ABC):
    """Interface for the simulation engine."""

    @property
    @abstractmethod
    def drones(self) -> list[Drone]:
        """Return the list of drones managed by the engine."""
