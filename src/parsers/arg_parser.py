"""Command line argument parser for the simulator."""

import argparse


class ArgParser():
    """Parser wrapper for command line arguments."""

    @staticmethod
    def parse() -> argparse.Namespace:
        """Parse arguments and return a namespace."""
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
        argparser.add_argument(
            "--algo", type=str, choices=["coop"], default="coop",
            help="Select the pathfinding algorithm to use"
            )
        return argparser.parse_args()
