"""Simulation controller managing playback and rendering loop."""

import sys
import time
from typing import Any

from ..models import Drone


class SimulationController:
    """
    Main controller for simulation playback.

    Manages the simulation clock and orchestrates registered renderers.
    """

    def __init__(
        self,
        drones: list[Drone],
        renderers: list[Any],
        play_speed: float = 1.0,
    ) -> None:
        """Initialize the simulation controller."""
        self.drones = drones
        self.renderers = renderers
        self.play_speed = play_speed

        self.current_time = 0.0
        self.is_paused = False

        # Calculate maximum turn based on the longest path
        self.max_turn = float(
            max((d.path[-1][1] for d in self.drones if d.path), default=0)
        )

    def run(self) -> None:
        """
        Run the main simulation loop.

        Processes time deltas, gathers input commands from renderers,
        and updates all renderers with the current state.
        """
        last_time = time.time()

        has_interactive_renderer = any(
            hasattr(r, "handle_events") for r in self.renderers
        )

        if not has_interactive_renderer:
            # Fast-forward simulation for CLI only
            while self.current_time <= self.max_turn:
                self.current_time += 1.0
                for r in self.renderers:
                    r.render(self.current_time, self.max_turn, self.drones)
            return

        # Interactive real-time loop
        while True:
            current_sys_time = time.time()
            dt = current_sys_time - last_time
            last_time = current_sys_time

            # Cap dt to avoid large jumps if window is moved/paused
            dt = min(dt, 0.1)

            self._handle_events(dt)
            self._update_time(dt)

            for r in self.renderers:
                r.render(self.current_time, self.max_turn, self.drones)

            # Sleep slightly to prevent maxing out CPU
            time.sleep(1 / 60.0)

    def _handle_events(self, dt: float) -> None:
        """Gather commands from interactive renderers and process them."""
        for r in self.renderers:
            if not hasattr(r, "handle_events"):
                continue

            commands = r.handle_events(dt)

            if commands.get("quit"):
                print("Bye!")
                for renderer in self.renderers:
                    renderer.cleanup()
                sys.exit(0)

            if commands.get("toggle_pause"):
                self.is_paused = not self.is_paused

            if commands.get("reset"):
                self.current_time = 0.0
                for renderer in self.renderers:
                    renderer.reset()

            if scrub_delta := commands.get("scrub_delta", 0.0):
                self.current_time += scrub_delta

    def _update_time(self, dt: float) -> None:
        """Advance time if playing, and bound it within limits."""
        play_speed = 0.0 if self.is_paused else self.play_speed

        self.current_time += dt * play_speed

        # Bound current time
        self.current_time = max(0.0, min(self.max_turn, self.current_time))
