"""Simulation engine module."""

from ..interfaces import Engine, Pathfinder
from ..models import Drone, Network


class SimulationEngine(Engine):
    """
    Core simulation engine.

    Handles drone lifecycle, routing, and turn-by-turn execution.
    """

    def __init__(self, network: Network, pathfinder: Pathfinder) -> None:
        """Initialize the engine with a network and pathfinder."""
        self.network = network
        self.pathfinder = pathfinder
        self._drones: list[Drone] = []

    @property
    def drones(self) -> list[Drone]:
        """Return the list of drones in the simulation."""
        return self._drones

    def _init_drones(self) -> None:
        """Instantiate the drone objects based on network specifications."""
        if self.network.start_hub is None:
            raise ValueError("Start hub is not defined in the network")
        self._drones = Drone.create_fleet(
            self.network.nb_drones, self.network.start_hub.name
        )

    def _plan_routes(self) -> None:
        """Execute pathfinding for all drones and register their paths."""
        if self.network.end_hub is None:
            raise ValueError("End hub is not defined in the network")
        for drone in self._drones:
            path = self.pathfinder.find_routes(
                drone.current_location, self.network.end_hub.name
            )
            if path is None:
                raise ValueError(f"No valid path found for drone {drone.id}")
            drone.path = path

    def run(self) -> None:
        """Run the simulation by initializing drones and planning routes."""
        self._init_drones()
        self._plan_routes()
