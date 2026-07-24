from abc import ABC, abstractmethod
from typing import List
from src.models import Drone


class AbstractRenderer(ABC):
    """
    Interface for the simulation renderer.
    """
    @abstractmethod
    def run(self, drones: List[Drone]) -> None:
        """
        Run the visualization using the provided drone states and paths.
        """
        pass
