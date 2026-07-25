from ..parsers import Parser, ArgParser
from ..algorithm.factory import PathfinderFactory
from ..interfaces import Pathfinder, Engine, Renderer
from ..engine import SimulationEngine
import sys


class Application():
    @staticmethod
    def run() -> None:
        visual = False
        try:
            args = ArgParser.parse()
            visual = args.visual
            parser = Parser(args.filename)
            network = parser.parse()

            pathfinder: Pathfinder = PathfinderFactory.create(
                args.algo, network
            )

            engine: Engine = SimulationEngine(network, pathfinder)
            engine.run()

            if not visual:
                from ..renderer import ConsoleRenderer
                renderer: Renderer = ConsoleRenderer()
            else:
                from ..renderer import PygameRenderer
                renderer = PygameRenderer(network, args.speed)

            renderer.run(engine.drones)

        except Exception as e:
            print(f"Error: {e}")
            if visual:
                import pygame
                pygame.quit()
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nBye!")
            if visual:
                import pygame
                pygame.quit()
            sys.exit(0)
