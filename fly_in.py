from src.parser import Parser
import sys
import argparse
from src.network import Network
from src.engine import Engine


def main() -> None:
    """
    Parse command line arguments and execute the drone simulation.
    """
    argparser = argparse.ArgumentParser(description="Fly-in Drone Simulator")
    argparser.add_argument("filename", help="Path to the map file")
    argparser.add_argument("--visual", action="store_true",
                           help="Enable the live terminal visualizer")
    argparser.add_argument("--speed", type=float, default=1,
                           help="Set up the speed of the animation")
    args = argparser.parse_args()

    try:
        parser = Parser(args.filename)
        parser.parse()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    try:
        network = Network(parser)
        engine = Engine(network, visualize=args.visual, play_speed=args.speed)
        engine.run()
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


if __name__ == "__main__":
    main()
