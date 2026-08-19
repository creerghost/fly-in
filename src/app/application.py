"""Main application entry point for the simulation."""

import sys
from typing import Any

from pydantic import ValidationError

from ..algorithm import CollisionManager, CooperativeAStar
from ..models import Drone
from ..parsers import Parser, parse_args
from ..renderer import CLILogger, PygameRenderer
from .controller import SimulationController


class Application:
    """Main application class."""

    @staticmethod
    def run() -> None:
        """Run the simulation application."""
        renderers: list[Any] = []
        try:
            args = parse_args()
            network = Parser(args.filename).parse()

            if network.start_hub is None or network.end_hub is None:
                raise ValueError("Start and end hubs must be defined")

            drones = Drone.create_fleet(
                network.nb_drones, network.start_hub.name
            )
            pathfinder = CooperativeAStar(network, CollisionManager())
            for drone in drones:
                path = pathfinder.find_routes(
                    drone.current_location, network.end_hub.name
                )
                if path is None:
                    raise ValueError(
                        f"No valid path found for drone {drone.id}"
                    )
                drone.path = path

            renderers = [CLILogger()]
            if args.renderer == "pygame":
                renderers.append(PygameRenderer(network, args.speed))

            controller = SimulationController(
                drones=drones,
                renderers=renderers,
                play_speed=args.speed,
            )
            controller.run()

        except ValidationError as e:
            error = e.errors()[0]
            msg = error["msg"]
            msg = msg.removeprefix("Value error, ")

            loc = error.get("loc", ())
            if loc and loc[0] != "__root__":
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
