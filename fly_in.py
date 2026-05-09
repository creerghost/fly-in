from src.Parser import Parser
import sys
from src.network import Network


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

    network = Network(parser)
    for n, v in network.neighboring_zones.items():
        print(f"{n}: {v}\n")


if __name__ == "__main__":
    main()
