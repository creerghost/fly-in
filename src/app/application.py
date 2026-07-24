from ..parsers import Parser, ArgParser
from ..engine import Engine
from ..models import Network
from ..algorithm import CooperativeAStar, CollisionManager
import sys


class Application():
    @staticmethod
    def run() -> None:
        try:
            args = ArgParser.parse()
            parser = Parser(args.filename)
            parser.parse()

            network = Network(
                nb_drones=parser.nb_drones,
                start_hub=parser.start_hub,  # type: ignore
                end_hub=parser.end_hub,      # type: ignore
                hubs=parser.hubs,            # type: ignore
                connections=parser.connections  # type: ignore
            )

            collision_manager = CollisionManager()
            pathfinder = CooperativeAStar(network, collision_manager)

            engine = Engine(network, pathfinder)
            engine.run()

            if args.visual:
                from ..renderer import Renderer
                renderer = Renderer(network, args.speed)
                renderer.run(engine.drones)

        except Exception as e:
            print(f"Error: {e}")
            if args.visual:
                import pygame
                pygame.quit()
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nBye!")
            if args.visual:
                import pygame
                pygame.quit()
            sys.exit(0)
