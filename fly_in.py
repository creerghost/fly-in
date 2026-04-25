from src.Parser import Parser
import sys
from src.Zone import Zone


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 fly_in.py <filename>")
        sys.exit(1)
    filename: str = sys.argv[1]
    parser = Parser(filename)
    try:
        parser.parse()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    print("all good")
    zones = {}
    for hub_data in parser.hubs:
        zone = Zone(**hub_data)
        zones[zone.name] = zone



if __name__ == "__main__":
    main()
