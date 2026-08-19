"""Command line argument parser for the simulator."""

import argparse


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Fly-in Drone Simulator")
    parser.add_argument("filename", help="Path to the map file")
    parser.add_argument(
        "--renderer",
        choices=["cli", "pygame"],
        default="cli",
        help="Select the renderer to use",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Set up the speed of the animation",
    )
    return parser.parse_args()
