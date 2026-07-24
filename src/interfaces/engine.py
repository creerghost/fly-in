from abc import ABC, abstractmethod
from .runnable import Runnable


class AbstractEngine(Runnable, ABC):
    """
    Interface for the simulation engine.
    """
    @abstractmethod
    def _plan_routes(self) -> None:
        """
        Plans the routes for all drones using the injected pathfinder.
        """
        pass
