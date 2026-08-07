"""Base A* pathfinding algorithm implementation."""

from abc import abstractmethod
from heapq import heappop, heappush

from ...interfaces import Pathfinder
from ...models import Network, TemporalState


class AStarAlgorithm(Pathfinder):
    """Abstract base class for A* based pathfinding algorithms."""

    def __init__(self, network: Network, max_turns: int = 1000) -> None:
        """Initialize the pathfinder with the network topology."""
        super().__init__(max_turns)
        self.network = network

    def _calculate_h(self, current_zone: str, target_zone: str) -> float:
        """
        Calculate a scaled Manhattan distance heuristic.

        This maintains admissibility.
        """
        dx = abs(self.network[current_zone].x - self.network[target_zone].x)
        dy = abs(self.network[current_zone].y - self.network[target_zone].y)
        return float(dx + dy) * 0.25

    @abstractmethod
    def generate_valid_neighbors(
        self, current_state: TemporalState, target_zone: str
    ) -> list[TemporalState]:
        """
        Generate all valid neighboring TemporalStates.

        Must be implemented by subclasses.
        """

    def get_state_key(self, state: TemporalState) -> tuple[str, int] | str:
        """Return a state key for Space-Time A* using zone_name and turn."""
        return (state.zone_name, state.turn)

    @abstractmethod
    def on_path_found(self, path: list[tuple[str, int]]) -> None:
        """Execute a hook for subclasses to act when a path is found."""

    def find_routes(
        self, start_zone: str, end_zone: str
    ) -> list[tuple[str, int]] | None:
        """
        Run the A* search from start_zone to end_zone.

        Returns a list of (zone_name, turn) states if a path exists.
        """
        start_state = TemporalState(
            f_cost=0.0,
            move_penalty=0,
            g_cost=0.0,
            h_cost=self._calculate_h(start_zone, end_zone),
            turn=0,
            zone_name=start_zone,
        )

        heap: list[TemporalState] = []
        visited: set[tuple[str, int] | str] = set()
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
                self.on_path_found(final_path)
                return final_path

            state_key = self.get_state_key(current_state)
            if state_key in visited:
                continue
            visited.add(state_key)

            for neighbor in self.generate_valid_neighbors(
                current_state, end_zone
            ):
                neighbor_key = self.get_state_key(neighbor)
                if (neighbor_key not in visited and
                        neighbor.turn <= self.max_turns):
                    heappush(heap, neighbor)

        return None
