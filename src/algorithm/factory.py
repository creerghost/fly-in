"""Factory for creating pathfinding algorithms."""

from ..interfaces import Factory, Pathfinder
from ..models import Network
from .coop_a_star import CollisionManager, CooperativeAStar


class PathfinderFactory(Factory):
    """Factory class for instantiating pathfinders."""

    @staticmethod
    def create(algo: str, network: Network) -> Pathfinder:
        """Create a pathfinder instance based on algorithm name."""
        if algo == "coop":
            collision_manager = CollisionManager()
            return CooperativeAStar(network, collision_manager)
        else:
            raise ValueError(f"Unknown algorithm: {algo}")
