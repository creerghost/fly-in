from src.parser import Parser
from src.arg_parser import ArgParser
from src.network import Network
from src.engine import Engine
import sys


def main() -> None:
    """
    Parse command line arguments and execute the drone simulation.
    """
    try:
        args = ArgParser.parse()
        parser = Parser(args.filename)
        parser.parse()

        network = Network(parser=parser)

        engine = Engine(
            network=network,
            visualize=args.visual,
            play_speed=args.speed
            )

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
