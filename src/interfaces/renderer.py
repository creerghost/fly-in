"""Renderer interface."""

from abc import ABC, abstractmethod

from typing import List
from ..models import Drone


class Renderer(ABC):
    """Interface for the simulation renderer."""

    @abstractmethod
    def render(
        self, current_time: float, max_turn: float, drones: List[Drone]
    ) -> None:
        """Render the simulation state at a specific point in time."""

    @abstractmethod
    def handle_events(self, dt: float) -> dict:
        """
        Handle input events and return playback commands.

        Returns a dictionary with keys such as 'scrub_delta',
        'toggle_pause', 'reset', 'quit'.
        """
