"""Factory for creating renderer instances."""

from ..interfaces import Renderer, Factory
from ..models import Network


class RendererFactory(Factory):
    """Factory class for instantiating renderers."""

    @staticmethod
    def create(visual: bool, network: Network, speed: float = 1.0) -> Renderer:
        """Create a renderer instance based on command line arguments."""
        if not visual:
            from .console_renderer import ConsoleRenderer
            return ConsoleRenderer()
        else:
            from .pygame import PygameRenderer
            return PygameRenderer(network, speed)
