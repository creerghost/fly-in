"""Main application entry point for the simulation."""

import sys

from pydantic import ValidationError

from .controller import SimulationController
from ..algorithm import PathfinderFactory
from ..engine import SimulationEngine
from ..interfaces import Engine, Pathfinder, Renderer
from ..parsers import ArgParser, Parser
from ..renderer import RendererFactory


class Application:
    """Main application class."""

    @staticmethod
    def run() -> None:
        """Run the simulation application."""
        renderers: list[Renderer] = []
        try:
            args = ArgParser.parse()
            parser = Parser(args.filename)
            network = parser.parse()

            pathfinder: Pathfinder = PathfinderFactory.create(
                args.algo, network
            )

            engine: Engine = SimulationEngine(network, pathfinder)
            engine.run()

            renderers = RendererFactory.create(
                args.renderer, network, args.speed
            )

            controller = SimulationController(
                network=network,
                drones=engine.drones,
                renderers=renderers,
                play_speed=args.speed,
            )
            controller.run()

        except ValidationError as e:
            error = e.errors()[0]
            msg = error['msg']
            if msg.startswith("Value error, "):
                msg = msg[len("Value error, "):]
            
            loc = error.get('loc', ())
            # ignore root model validations which don't have a specific field
            if loc and loc[0] != '__root__':
                loc_str = " -> ".join(str(x) for x in loc)
                print(f"Error in '{loc_str}': {msg}")
            else:
                print(f"Error: {msg}")
            for r in renderers:
                r.cleanup()
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            for r in renderers:
                r.cleanup()
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nBye!")
            for r in renderers:
                r.cleanup()
            sys.exit(0)
