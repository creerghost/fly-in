"""Simulation controller managing playback and rendering loop."""

import sys
import time

from ..interfaces import Renderer
from ..models import Drone, Network


class SimulationController:
    """
    Main controller for simulation playback.

    Manages the simulation clock and orchestrates registered renderers.
    """

    def __init__(
        self,
        network: Network,
        drones: list[Drone],
        renderers: list[Renderer],
        play_speed: float = 1.0,
    ) -> None:
        """Initialize the simulation controller."""
        self.network = network
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

        # Determine if we have a real-time requirement (visual mode)
        # If no renderers return a scrub delta, it means we don't have a UI,
        # so we can just blast through time if we want, or run turn-by-turn.
        # But since we use CLILogger alongside PygameRenderer (optionally),
        # we need a standard loop. If there's no UI,
        # we can just run to the end instantly.

        has_interactive_renderer = any(
            type(r).__name__ == "PygameRenderer"
            for r in self.renderers
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
        """Gather commands from renderers and process them."""
        for r in self.renderers:
            commands = r.handle_events(dt)

            if commands.get("quit"):
                print("Bye!")
                for renderer in self.renderers:
                    if renderer.__class__.__name__ == "PygameRenderer":
                        import pygame

                        pygame.quit()
                sys.exit(0)

            if commands.get("toggle_pause"):
                self.is_paused = not self.is_paused

            if commands.get("reset"):
                self.current_time = 0.0
                # We need to also reset CLILogger's highest turn printed
                for renderer in self.renderers:
                    if hasattr(renderer, "highest_turn_printed"):
                        renderer.highest_turn_printed = 0

            if scrub_delta := commands.get("scrub_delta", 0.0):
                self.current_time += scrub_delta

    def _update_time(self, dt: float) -> None:
        """Advance time if playing, and bound it within limits."""
        play_speed = 0.0 if self.is_paused else self.play_speed

        # Only advance time if we didn't already scrub in handle_events
        # If we are playing, time should advance normally even if scrubbing?
        # Typically we just add dt * play_speed
        self.current_time += dt * play_speed

        # Bound current time
        self.current_time = max(0.0, min(self.max_turn, self.current_time))
