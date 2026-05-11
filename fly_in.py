from src.Parser import Parser
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
    argparser.add_argument("--delay", type=float, default=0.5,
                           help="Setup delay for the visualizer")
    args = argparser.parse_args()

    if args.delay < 0:
        print("Error: Delay must be a non-negative value.")
        sys.exit(1)

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
        engine = Engine(network, visualize=args.visual, delay=args.delay)
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
