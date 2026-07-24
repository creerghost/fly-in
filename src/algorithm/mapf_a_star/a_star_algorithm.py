from typing import List, Optional, Tuple, Set
from heapq import heappop, heappush
from ...models import Network, TemporalState
from ...interfaces import Pathfinder


class AStarAlgorithm(Pathfinder):
    """
    Implements standard A* pathfinding algorithm without
    collision or capacity constraints.
    """
    def __init__(self, network: Network) -> None:
        """
        Initialize the pathfinder with the network topology.
        """
        self.network = network

    def _calculate_h(self, current_zone: str, target_zone: str) -> float:
        """
        Calculate a scaled Manhattan distance heuristic to maintain
        admissibility.
        """
        return float(abs(self.network[current_zone].x -
                     self.network[target_zone].x) +
                     abs(self.network[current_zone].y -
                     self.network[target_zone].y)) * 0.25

    def generate_valid_neighbors(self,
                                 current_state: TemporalState,
                                 target_zone: str
                                 ) -> List[TemporalState]:
        """
        Generate all valid neighboring TemporalStates without checking
        capacities.
        """
        neighbors: List[TemporalState] = []

        for neighbor, connection in self.network.neighboring_zones[
                current_state.zone_name]:
            if not neighbor.is_traversable:
                continue

            next_turn = current_state.turn + neighbor.transit_time
            step_cost = neighbor.movement_cost

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

    def get_state_key(self, state: TemporalState) -> Tuple[str, int] | str:
        """
        Hook for subclasses to define what makes a state unique in the
        visited set. Standard A* just uses the zone name.
        """
        return state.zone_name

    def on_path_found(self, path: List[Tuple[str, int]]) -> None:
        """
        Hook for subclasses to act when a path is successfully found.
        """
        pass

    def find_routes(self,
                    start_zone: str,
                    end_zone: str
                    ) -> Optional[List[Tuple[str, int]]]:
        """
        Run the A* search from start_zone to end_zone,
        returning a list of (zone_name, turn) states if a path exists.
        """
        start_state = TemporalState(
            f_cost=0.0,
            g_cost=0.0,
            h_cost=self._calculate_h(start_zone, end_zone),
            turn=0,
            zone_name=start_zone
            )

        open_set: List[TemporalState] = []
        visited: Set[Tuple[str, int] | str] = set()
        heappush(open_set, start_state)

        while open_set:
            current_state = heappop(open_set)

            if current_state.zone_name == end_zone:
                path = []
                curr: Optional[TemporalState] = current_state
                while curr:
                    path.append((curr.zone_name, curr.turn))
                    curr = curr.parent

                final_path = path[::-1]
                self.on_path_found(final_path)
                return final_path

            state_key = self.get_state_key(current_state)
            if state_key in visited:
                continue
            visited.add(state_key)

            for neighbor in self.generate_valid_neighbors(current_state,
                                                          end_zone):
                neighbor_key = self.get_state_key(neighbor)
                if neighbor_key not in visited:
                    heappush(open_set, neighbor)

        return None
