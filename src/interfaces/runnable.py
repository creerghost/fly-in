"""Runnable interface."""

from abc import ABC, abstractmethod


class Runnable(ABC):
    """Interface for components that can be executed."""

    @abstractmethod
    def run(self) -> None:
        """Execute the component."""
        pass
