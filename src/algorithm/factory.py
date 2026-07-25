from ..models import Network
from ..interfaces import Pathfinder
from .mapf_a_star.cooperative_a_star import CooperativeAStar
from .mapf_a_star.collision_manager import CollisionManager


class PathfinderFactory:
    @staticmethod
    def create(algo: str, network: Network) -> Pathfinder:
        if algo == "coop":
            collision_manager = CollisionManager()
            return CooperativeAStar(network, collision_manager)
        else:
            raise ValueError(f"Unknown algorithm: {algo}")
