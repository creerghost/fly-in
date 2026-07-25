"""Entry point for the fly-in simulation."""

from .app import Application


def main() -> None:
    """Execute the main application run method."""
    Application.run()


if __name__ == "__main__":
    main()
