"""Interactive Pygame visualizer for the drone simulation."""


import pygame

from ...interfaces import Renderer
from ...models import Drone, Network
from ..hud_stats import HudStats
from .config import RendererConfig
from .drawers import DroneDrawer, HUDDrawer, NetworkDrawer


class PygameRenderer(Renderer):
    """
    Handle the graphical display of the simulation using Pygame.

    Delegates drawing to specific Drawer components.
    """

    def __init__(self, network: Network, play_speed: float = 1) -> None:
        """Initialize the Pygame window and calculate canvas bounds."""
        self.network = network
        self.play_speed = play_speed
        self.config = RendererConfig()

        pygame.init()
        pygame.display.set_caption("Fly-in Drone Simulator")

        self._canvas_size()

        self.width = (
            (self.canvas_max_x - self.canvas_min_x) * self.config.tile_size
            + 2 * self.config.margin
            + 50
        )
        self.height = (
            (self.canvas_max_y - self.canvas_min_y) * self.config.tile_size
            + 2 * self.config.margin
            + self.config.panel_height
        )
        self._extend_width()

        self.screen = pygame.display.set_mode((self.width, self.height))

        # Fonts
        self.font = pygame.font.SysFont(None, self.config.font_size_normal)
        self.large_font = pygame.font.SysFont(
            None, self.config.font_size_large)
        self.small_font = pygame.font.SysFont(
            None, self.config.font_size_small)
        self.hud_font = pygame.font.SysFont(None, self.config.font_size_hud)

        # Drawers
        self.network_drawer = NetworkDrawer(
            self.screen, self.config, self.font, self.small_font, self._get_pixel_coords
        )
        self.drone_drawer = DroneDrawer(
            self.screen, self.config, self.font, self._get_pixel_coords
        )
        self.hud_drawer = HUDDrawer(
            self.screen,
            self.config,
            self.large_font,
            self.hud_font,
            self.width,
            self.height,
        )

    def _extend_width(self) -> None:
        width = 650 - self.width
        if width <= 0:
            return
        self.width += width

    def _canvas_size(self) -> None:
        """Determine the boundaries of the grid based on zone coordinates."""
        if not self.network.zones:
            raise ValueError("Zones not defined")

        x_coords = [zone.x for zone in self.network.zones.values()]
        y_coords = [zone.y for zone in self.network.zones.values()]

        self.canvas_min_x = min(x_coords)
        self.canvas_max_x = max(x_coords)
        self.canvas_min_y = min(y_coords)
        self.canvas_max_y = max(y_coords)

    def _get_pixel_coords(self, x: float, y: float) -> tuple[int, int]:
        """Convert grid coordinates to Pygame pixel coordinates."""
        grid_center_x = (self.canvas_min_x + self.canvas_max_x) / 2
        grid_center_y = (self.canvas_min_y + self.canvas_max_y) / 2

        screen_center_x = self.width / 2
        screen_center_y = (self.height - self.config.panel_height) / 2

        px = (x - grid_center_x) * self.config.tile_size + screen_center_x
        py = (grid_center_y - y) * self.config.tile_size + screen_center_y

        # chessboard offset to prevent connection overlaps
        # For interpolation, we might need to cast to int if we want the exact offset,
        # but using float coordinates should be fine since the original used round x/y.
        px += 30 if round(y) % 2 == 0 else -10
        py += 30 if round(x) % 2 != 0 else -10

        return int(px), int(py)

    def handle_events(self, dt: float) -> dict:
        """
        Process keyboard events for pausing, scrubbing time, and quitting.

        Returns a dict of playback commands.
        """
        commands = {
            "quit": False,
            "toggle_pause": False,
            "reset": False,
            "scrub_delta": 0.0,
        }

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                commands["quit"] = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                commands["toggle_pause"] = True

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            commands["quit"] = True

        scrub_speed = self.play_speed * 3
        if keys[pygame.K_LEFT]:
            commands["scrub_delta"] = -(dt * scrub_speed * 0.65)
        elif keys[pygame.K_RIGHT]:
            commands["scrub_delta"] = dt * scrub_speed
        elif keys[pygame.K_r]:
            commands["reset"] = True

        return commands

    def render(self, current_time: float, max_turn: float, drones: list[Drone]) -> None:
        """
        Render the simulation frame.
        """
        self.screen.fill(self.config.bg_color)

        hud_stats = HudStats.from_drones(drones, self.network)

        self.hud_drawer.draw_overlays(current_time)
        self.network_drawer.draw_connections(self.network)
        self.network_drawer.draw_zones(self.network)

        active_drones = self.drone_drawer.draw_drones(
            current_time, drones, self.network
        )
        hud_stats.active_drones = active_drones

        self.hud_drawer.draw_hud(hud_stats)

        pygame.display.flip()
