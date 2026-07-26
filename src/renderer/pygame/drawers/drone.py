"""Drone drawer component."""

import os
from collections.abc import Callable

import pygame

from ....models import Drone, Network
from ..colors import Colors
from ..config import RendererConfig


class DroneDrawer:
    """Draws drones on the network."""

    def __init__(
        self,
        screen: pygame.Surface,
        config: RendererConfig,
        font: pygame.font.Font,
        coord_mapper: Callable[[float, float], tuple[int, int]],
    ) -> None:
        """Initialize the drone drawer."""
        self.screen = screen
        self.config = config
        self.font = font
        self._get_pixel_coords = coord_mapper
        self.drone_img = pygame.transform.scale(
            pygame.image.load(os.path.join("imgs", "drone.bmp")), (45, 45)
        )

    def draw_drones(
        self, t_current: float, drones: list[Drone], network: Network
    ) -> int:
        """
        Calculate and draw drones.

        Returns the number of active drones in transit.
        """
        drone_groups: dict[tuple[int, int], list[Drone]] = {}
        drone_transits: dict[tuple[int, int], bool] = {}
        active_drones = 0

        for drone in drones:
            start_zone_name, end_zone_name, t_smooth, transit = (
                drone.get_render_state(t_current)
            )

            z1 = network[start_zone_name]
            z2 = network[end_zone_name]

            start_x, start_y = self._get_pixel_coords(float(z1.x), float(z1.y))
            end_x, end_y = self._get_pixel_coords(float(z2.x), float(z2.y))

            px_f = start_x + (end_x - start_x) * t_smooth
            py_f = start_y + (end_y - start_y) * t_smooth

            px, py = int(px_f), int(py_f)

            if transit:
                active_drones += 1

            coord = (px, py)
            if coord not in drone_groups:
                drone_groups[coord] = []
            drone_groups[coord].append(drone)
            drone_transits[coord] = transit

        for coord, d_list in drone_groups.items():
            self._draw_drone_marker(
                coord[0], coord[1], d_list, drone_transits[coord])

        return active_drones

    def _draw_drone_marker(
        self, px: int, py: int, drones_list: list[Drone], transit: bool
    ) -> None:
        """Render the drone bitmap and label at the given pixel position."""
        label = drones_list[0].id if len(
            drones_list) == 1 else f"{len(drones_list)}D"
        text = self.font.render(label, True, Colors.WHITE.value)

        rect_w = text.get_width() + 5
        rect_h = text.get_height() + 5
        color = Colors.RED.value if not transit else Colors.GRAY.value

        rect = pygame.Rect(0, 0, rect_w, rect_h)
        rect.center = (px, py - 25)
        rect_outline = pygame.Rect(0, 0, rect_w + 2, rect_h + 2)
        rect_outline.center = rect.center

        pygame.draw.rect(self.screen, Colors.WHITE.value,
                         rect_outline, border_radius=4)
        pygame.draw.rect(self.screen, color, rect, border_radius=3)

        self.screen.blit(self.drone_img, (px - 23, py - 22))
        self.screen.blit(
            text, (px - text.get_width() // 2,
                   (py - 25) - text.get_height() // 2)
        )
