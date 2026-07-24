import argparse


class ArgParser():
    @staticmethod
    def parse() -> argparse.Namespace:
        argparser = argparse.ArgumentParser(
            description="Fly-in Drone Simulator"
            )
        argparser.add_argument(
            "filename",
            help="Path to the map file"
            )
        argparser.add_argument(
            "--visual", action="store_true",
            help="Enable the live terminal visualizer"
            )
        argparser.add_argument(
            "--speed", type=float, default=1,
            help="Set up the speed of the animation"
            )
        return argparser.parse_args()
