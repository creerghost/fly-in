"""Factory for creating renderer instances."""


from ..interfaces import Factory, Renderer
from ..models import Network
from .cli_logger import CLILogger
from .pygame import PygameRenderer


class RendererFactory(Factory):
    """Factory class for instantiating renderers."""

    @staticmethod
    def create(
        renderer_type: str, network: Network, speed: float = 1.0
    ) -> list[Renderer]:
        """Create a list of renderer instances based on command line
        arguments.
        """
        if renderer_type == "pygame":
            return [CLILogger(), PygameRenderer(network, speed)]

        return [CLILogger()]
