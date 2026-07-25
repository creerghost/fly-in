from ..models import Network
from ..interfaces import Pathfinder
from .coop_a_star.algorithm import CooperativeAStar
from .coop_a_star.manager import CollisionManager


class PathfinderFactory:
    @staticmethod
    def create(algo: str, network: Network) -> Pathfinder:
        if algo == "coop":
            collision_manager = CollisionManager()
            return CooperativeAStar(network, collision_manager)
        else:
            raise ValueError(f"Unknown algorithm: {algo}")
