from ..parsers import Parser, ArgParser
from ..engine import SimulationEngine
from ..algorithm import CooperativeAStar, CollisionManager
from ..interfaces import Pathfinder, Engine, Manager
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

            collision_manager: Manager = CollisionManager()
            pathfinder: Pathfinder = CooperativeAStar(
                network, collision_manager)

            engine: Engine = SimulationEngine(network, pathfinder)
            engine.run()

            if visual:
                from ..renderer import PygameRenderer
                from ..interfaces import Renderer
                renderer: Renderer = PygameRenderer(network, args.speed)
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
