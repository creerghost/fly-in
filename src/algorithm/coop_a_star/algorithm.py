"""Cooperative A* pathfinding algorithm implementation."""

from heapq import heappop, heappush

from ...models import Network, TemporalState, Zone
from .manager import CollisionManager


class CooperativeAStar:
    """
    Implement Cooperative Space-Time A* pathfinding.

    Respects reservation constraints and dynamic link capacities.
    """

    def __init__(
        self,
        network: Network,
        reservations: CollisionManager,
        max_turns: int = 1000,
    ) -> None:
        """
        Initialize the pathfinder with the network topology.

        Uses the global reservation table and max turn limit.
        """
        self.network = network

        self.reservations = reservations
        self.max_turns = max_turns

    def _calculate_h(self, current_zone: str, target_zone: str) -> float:
        """Calculate scaled Manhattan distance heuristic."""
        dx = abs(self.network[current_zone].x - self.network[target_zone].x)
        dy = abs(self.network[current_zone].y - self.network[target_zone].y)
        return float(dx + dy) * 0.25

    def _generate_valid_neighbors(
        self, current_state: TemporalState, target_zone: str
    ) -> list[TemporalState]:
        """Generate all valid neighboring TemporalStates."""
        next_turn = current_state.turn + 1
        neighbors: list[TemporalState] = []
        current_zone: Zone = self.network[current_state.zone_name]

        if self.reservations.is_zone_available(
            current_state.zone_name, next_turn, current_zone.max_drones
        ):
            wait_state = TemporalState(
                f_cost=(current_state.g_cost + 1.0) + current_state.h_cost,
                g_cost=current_state.g_cost + 1.0,
                h_cost=current_state.h_cost,
                turn=next_turn,
                zone_name=current_state.zone_name,
                parent=current_state,
            )
            neighbors.append(wait_state)

        for neighbor, connection in self.network.neighboring_zones[
            current_state.zone_name
        ]:
            if not neighbor.is_traversable:
                continue

            next_turn = current_state.turn + neighbor.transit_time
            step_cost = neighbor.movement_cost

            link_available = True
            for t in range(current_state.turn + 1, next_turn + 1):
                if not self.reservations.is_link_available(
                    current_state.zone_name,
                    neighbor.name,
                    t,
                    connection.max_link_capacity,
                ):
                    link_available = False
                    break

            if link_available and self.reservations.is_zone_available(
                neighbor.name, next_turn, neighbor.max_drones
            ):
                new_g_cost = current_state.g_cost + step_cost

                # Penalize revisiting a zone to prevent back-and-forth loops
                curr: TemporalState | None = current_state
                while curr:
                    if curr.zone_name == neighbor.name:
                        new_g_cost += 10
                        break
                    curr = curr.parent

                new_h_cost = self._calculate_h(neighbor.name, target_zone)

                new_state = TemporalState(
                    f_cost=new_g_cost + new_h_cost,
                    g_cost=new_g_cost,
                    h_cost=new_h_cost,
                    turn=next_turn,
                    zone_name=neighbor.name,
                    parent=current_state,
                )
                neighbors.append(new_state)

        return neighbors

    def find_routes(
        self, start_zone: str, end_zone: str
    ) -> list[tuple[str, int]] | None:
        """Run the Cooperative A* search and commit path reservations."""
        start_state = TemporalState(
            f_cost=0.0,
            g_cost=0.0,
            h_cost=self._calculate_h(start_zone, end_zone),
            turn=0,
            zone_name=start_zone,
        )

        heap: list[TemporalState] = []
        visited: set[tuple[str, int]] = set()
        heappush(heap, start_state)

        while heap:
            current_state = heappop(heap)

            if current_state.zone_name == end_zone:
                path = []
                curr: TemporalState | None = current_state
                while curr:
                    path.append((curr.zone_name, curr.turn))
                    curr = curr.parent

                final_path = path[::-1]
                self.reservations.register_path(final_path)
                return final_path

            state_key = (current_state.zone_name, current_state.turn)
            if state_key in visited:
                continue
            visited.add(state_key)

            for neighbor in self._generate_valid_neighbors(
                current_state, end_zone
            ):
                neighbor_key = (neighbor.zone_name, neighbor.turn)
                if (
                    neighbor_key not in visited
                    and neighbor.turn <= self.max_turns
                ):
                    heappush(heap, neighbor)

        return None
