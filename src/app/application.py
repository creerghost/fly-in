"""Main application entry point for the simulation."""

import sys

from .controller import SimulationController
from ..algorithm.factory import PathfinderFactory
from ..engine import SimulationEngine
from ..interfaces import Engine, Pathfinder
from ..parsers import ArgParser, Parser
from ..renderer import RendererFactory


class Application:
    """Main application class."""

    @staticmethod
    def run() -> None:
        """Run the simulation application."""
        renderer_type = "cli"
        try:
            args = ArgParser.parse()
            renderer_type = args.renderer
            parser = Parser(args.filename)
            network = parser.parse()

            pathfinder: Pathfinder = PathfinderFactory.create(
                args.algo, network
            )

            engine: Engine = SimulationEngine(network, pathfinder)
            engine.run()

            renderers = RendererFactory.create(
                renderer_type, network, args.speed
            )

            controller = SimulationController(
                network=network,
                drones=engine.drones,
                renderers=renderers,
                play_speed=args.speed,
            )
            controller.run()

        except Exception as e:
            print(f"Error: {e}")
            if renderer_type == "pygame":
                import pygame

                pygame.quit()
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nBye!")
            if renderer_type == "pygame":
                import pygame

                pygame.quit()
            sys.exit(0)
