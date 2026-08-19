"""Drone models for the simulation."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class Drone:
    """
    Represent a single drone entity in the simulation.

    Holds its unique ID and full planned path.
    """

    id: str
    current_location: str
    path: list[tuple[str, int]] = field(default_factory=list)

    def __str__(self) -> str:
        """Return a string representation of the drone."""
        return f"{self.id} @ {self.current_location}"

    def __repr__(self) -> str:
        """Return a detailed string representation of the drone."""
        return f"Drone('{self.id}', loc='{self.current_location}')"

    @classmethod
    def create_fleet(cls, count: int, start_location: str) -> list["Drone"]:
        """Generate a fleet of drones starting at the specified location."""
        return [cls(f"D{i + 1}", start_location) for i in range(count)]

    def location_at_turn(self, turn: int) -> str:
        """Determine the exact string location of the drone at a given turn."""
        if not self.path or turn >= self.path[-1][1]:
            return self.path[-1][0] if self.path else self.current_location
        for curr_step, next_step in zip(self.path[:-1], self.path[1:]):
            curr_zone, curr_turn = curr_step
            next_zone, next_turn = next_step
            if turn == curr_turn:
                return curr_zone
            elif curr_turn < turn < next_turn:
                if curr_zone == next_zone:
                    return curr_zone
                else:
                    return f"{curr_zone}-{next_zone}"
        return self.path[-1][0]

    def get_render_state(self, t: float) -> tuple[str, str, float, bool]:
        """
        Determine the logical render state at time t.

        Returns:
            Tuple[str, str, float, bool]:
            (start_zone_name, end_zone_name, progress_fraction, is_transit)
        """
        if not self.path:
            return self.current_location, self.current_location, 0.0, False

        if t >= self.path[-1][1]:
            zone = self.path[-1][0]
            return zone, zone, 0.0, False

        if t <= self.path[0][1]:
            zone = self.path[0][0]
            return zone, zone, 0.0, False

        for curr_step, next_step in zip(self.path[:-1], self.path[1:]):
            curr_zone_name, curr_turn = curr_step
            next_zone_name, next_turn = next_step

            if curr_turn <= t < next_turn:
                t_frac = (t - curr_turn) / (next_turn - curr_turn)
                t_smooth = t_frac * t_frac * (3.0 - 2.0 * t_frac)

                is_transit = (curr_zone_name != next_zone_name) and (
                    0.05 < t_smooth < 0.95
                )

                return curr_zone_name, next_zone_name, t_smooth, is_transit

        # fallback
        zone = self.path[-1][0]
        return zone, zone, 0.0, False
