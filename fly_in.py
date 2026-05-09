from src.Parser import Parser
import sys
from src.network import Network
from src.engine import Engine


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 fly_in.py <filename>")
        sys.exit(1)
    try:
        parser = Parser(sys.argv[1])
        parser.parse()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    try:
        network = Network(parser)
        engine = Engine(network)
        engine.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)




if __name__ == "__main__":
    main()
