"""Factory for creating renderer instances."""


from ..interfaces import Factory, Renderer
from ..models import Network


class RendererFactory(Factory):
    """Factory class for instantiating renderers."""

    @staticmethod
    def create(
        visual: bool, network: Network, speed: float = 1.0
    ) -> list[Renderer]:
        """Create a list of renderer instances based on command line arguments."""
        from .cli_logger import CLILogger

        renderers: list[Renderer] = [CLILogger()]

        if visual:
            from .pygame import PygameRenderer

            renderers.append(PygameRenderer(network, speed))

        return renderers
