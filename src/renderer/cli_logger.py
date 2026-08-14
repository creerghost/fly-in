"""Command-line output logger for the simulation."""

from typing import Optional

from ..interfaces import Renderer
from ..models import Drone, Network


class CLILogger(Renderer):
    """
    Log drone movements to standard output as simulation time advances.

    Only prints when the time scrubs forward past a new integer turn.
    """

    def __init__(self, network: Optional[Network] = None) -> None:
        """Initialize the CLI logger."""
        self.highest_turn_printed = 0
        self.network = network

    def render(
        self, current_time: float, max_turn: float, drones: list[Drone]
    ) -> None:
        """Print turn output if a new integer turn is reached."""
        while self.highest_turn_printed < int(current_time):
            self.highest_turn_printed += 1
            t = self.highest_turn_printed
            turn_output = []

            for drone in drones:
                loc_now = drone.location_at_turn(t)
                loc_prev = drone.location_at_turn(t - 1)

                if loc_now != loc_prev:
                    turn_output.append(f"{drone.id}-{loc_now}")

            if turn_output:
                print(" ".join(turn_output))

    def reset(self) -> None:
        """Reset the internal state of the renderer."""
        self.highest_turn_printed = 0

    def cleanup(self) -> None:
        """Clean up renderer resources."""
        pass
