from typing import List, Tuple
from ...models import Network, Zone
from .collision_manager import CollisionManager
from .a_star_algorithm import AStarAlgorithm, TemporalState


class CooperativeAStar(AStarAlgorithm):
    """
    Implements Cooperative Space-Time A* pathfinding algorithms respecting
    reservation constraints.
    """
    def __init__(self, network: Network,
                 reservations: CollisionManager) -> None:
        """
        Initialize the pathfinder with the network topology and global
        reservation table.
        """
        super().__init__(network)
        self.reservations = reservations

    def get_state_key(self, state: TemporalState) -> Tuple[str, int] | str:
        """
        Space-Time A* uses both zone_name and turn as the state key.
        """
        return (state.zone_name, state.turn)

    def on_path_found(self, path: List[Tuple[str, int]]) -> None:
        """
        Register the finalized path in the collision manager.
        """
        self.reservations.register_path(path)

    def generate_valid_neighbors(self,
                                 current_state: TemporalState,
                                 target_zone: str
                                 ) -> List[TemporalState]:
        """
        Generate all valid neighboring TemporalStates, considering wait
        actions, zone types, and capacity limits.
        """
        next_turn = current_state.turn + 1
        neighbors: List[TemporalState] = []
        current_zone: Zone = self.network.zones[current_state.zone_name]

        if self.reservations.is_zone_available(current_state.zone_name,
                                               next_turn,
                                               current_zone.max_drones):
            wait_state = TemporalState(
                f_cost=(current_state.g_cost + 1.0) + current_state.h_cost,
                g_cost=current_state.g_cost + 1.0,
                h_cost=current_state.h_cost,
                turn=next_turn,
                zone_name=current_state.zone_name,
                parent=current_state
            )
            neighbors.append(wait_state)

        for neighbor, connection in self.network.neighboring_zones[
                current_state.zone_name]:
            if neighbor.zone_type == "blocked":
                continue

            step_cost = 1.0
            if neighbor.zone_type == "normal":
                next_turn = current_state.turn + 1
            elif neighbor.zone_type == "priority":
                next_turn = current_state.turn + 1
                step_cost = 0.8
            elif neighbor.zone_type == "restricted":
                next_turn = current_state.turn + 2
                step_cost = 2.0

            link_available = True
            for t in range(current_state.turn + 1, next_turn + 1):
                if not self.reservations.is_link_available(
                        current_state.zone_name,
                        neighbor.name,
                        t,
                        connection.max_link_capacity):
                    link_available = False
                    break

            if link_available and self.reservations.is_zone_available(
                    neighbor.name,
                    next_turn,
                    neighbor.max_drones):

                new_g_cost = current_state.g_cost + step_cost
                new_h_cost = self._calculate_h(neighbor.name, target_zone)

                new_state = TemporalState(
                    f_cost=new_g_cost + new_h_cost,
                    g_cost=new_g_cost,
                    h_cost=new_h_cost,
                    turn=next_turn,
                    zone_name=neighbor.name,
                    parent=current_state
                )
                neighbors.append(new_state)

        return neighbors
