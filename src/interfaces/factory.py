"""Interface for all factory classes."""

from abc import ABC, abstractmethod
from typing import Any


class Factory(ABC):
    """Abstract base class for factories."""

    @staticmethod
    @abstractmethod
    def create(*args: Any, **kwargs: Any) -> Any:
        """Create and return an instance of a domain object."""
