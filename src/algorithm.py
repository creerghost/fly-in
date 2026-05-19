from typing import Tuple, Dict, List, Optional, Set
from dataclasses import dataclass, field
from heapq import heappop, heappush
from src.network import Network, Zone


@dataclass(order=True)
class TemporalState:
    """
    Storing data for each TemporalState object.
    """
    f_cost: float
    g_cost: float = field(compare=False)
    h_cost: float = field(compare=False)
    turn: int = field(compare=False)
    zone_name: str = field(compare=False)
    parent: Optional['TemporalState'] = field(default=None, compare=False)


class ReservationTable():
    """
    Maintains a schedule of zone and link capacities per turn
    to prevent collisions.
    """
    def __init__(self) -> None:
        """
        Initialize empty schedules for zones and links.
        """
        self.zone_schedule: Dict[Tuple[str, int], int] = {}
        self.link_schedule: Dict[Tuple[Tuple[str, str], int], int] = {}

    def is_zone_available(self, zone_name: str,
                          turn: int, max_capacity: int) -> bool:
        """
        Check if a specific zone has remaining capacity during a given turn.
        """
        current_occupancy = self.zone_schedule.get((zone_name, turn), 0)
        return current_occupancy < max_capacity

    def is_link_available(self, zone1: str, zone2: str,
                          turn: int, max_link_capacity: int) -> bool:
        """
        Check if a connection link between two zones has remaining
        capacity during a given turn.
        """
        link: Tuple[str, str] = (min(zone1, zone2), max(zone1, zone2))
        current_traffic = self.link_schedule.get((link, turn), 0)
        return current_traffic < max_link_capacity

    def register_path(self, path: List[Tuple[str, int]]) -> None:
        """
        Commit a path to the reservation table, locking zone and link
        capacities for specific turns.
        """
        # register the zone occupancy for each turn
        for zone_name, turn in path:
            current_occupancy = self.zone_schedule.get((zone_name, turn), 0)
            self.zone_schedule[(zone_name, turn)] = current_occupancy + 1
        # look at consecutive steps to register link (connection) usage
        for curr_step, next_step in zip(path[:-1], path[1:]):
            curr_zone_name, curr_turn = curr_step
            next_zone_name, next_turn = next_step
        # Ignore wait actions
            if curr_zone_name == next_zone_name:
                continue
            link: Tuple[str, str] = (min(curr_zone_name, next_zone_name),
                                     max(curr_zone_name, next_zone_name))
        # Reserve the link for all turns spent in transit
            for t in range(curr_turn + 1, next_turn + 1):
                current_traffic = self.link_schedule.get((link, t), 0)
                self.link_schedule[(link, t)] = current_traffic + 1


class SpaceTimePathfinder:
    """
    Implements Cooperative Space-Time A* pathfinding algorithms respecting
    reservation constraints.
    """
    def __init__(self, network: Network,
                 reservations: ReservationTable) -> None:
        """
        Initialize the pathfinder with the network topology and global
        reservation table.
        """
        self.network = network
        self.reservations = reservations

    def _calculate_h(self, current_zone: str, target_zone: str) -> float:
        """
        Calculate a scaled Manhattan distance heuristic to maintain
        admissibility.
        """
        return float(abs(self.network.zones[current_zone].x -
                     self.network.zones[target_zone].x) +
                     abs(self.network.zones[current_zone].y -
                     self.network.zones[target_zone].y)) * 0.25

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
        visited: Set[Tuple[str, int]] = set()
        heappush(open_set, start_state)

        while open_set:
            current_state = heappop(open_set)

            if current_state.zone_name == end_zone:
                path = []
                curr: Optional[TemporalState] = current_state
                while curr:
                    path.append((curr.zone_name, curr.turn))
                    curr = curr.parent
                return path[::-1]

            space_time_key = (current_state.zone_name, current_state.turn)
            if space_time_key in visited:
                continue
            visited.add(space_time_key)

            for neighbor in self.generate_valid_neighbors(current_state,
                                                          end_zone):
                neighbor_key: Tuple[str, int] = (neighbor.zone_name,
                                                 neighbor.turn)
                if neighbor_key not in visited:
                    heappush(open_set, neighbor)

        return None
