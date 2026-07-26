"""Network drawer component."""

import sys
from collections.abc import Callable

import pygame

from ....models import Network
from ..colors import Colors
from ..config import RendererConfig


class NetworkDrawer:
    """Draws the network zones and connections."""

    def __init__(
        self,
        screen: pygame.Surface,
        config: RendererConfig,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
        coord_mapper: Callable[[float, float], tuple[int, int]],
    ) -> None:
        """Initialize the network drawer."""
        self.screen = screen
        self.config = config
        self.font = font
        self.small_font = small_font
        self._get_pixel_coords = coord_mapper

    def draw_connections(self, network: Network) -> None:
        """Render the network edges between zones."""
        for con in network.connections:
            z1 = network[con.name1]
            z2 = network[con.name2]
            if z1 and z2:
                p1 = self._get_pixel_coords(float(z1.x), float(z1.y))
                p2 = self._get_pixel_coords(float(z2.x), float(z2.y))

                pygame.draw.line(
                    self.screen,
                    Colors.WHITE.value,
                    p1,
                    p2,
                    self.config.connection_line_width,
                )
                pygame.draw.line(
                    self.screen,
                    self.config.line_outline_color,
                    p1,
                    p2,
                    self.config.connection_outline_width,
                )

                mlc = self.small_font.render(
                    f"{con.max_link_capacity}", True, Colors.WHITE.value
                )
                z_x = (p1[0] + p2[0]) // 2
                z_y = (p1[1] + p2[1]) // 2
                self.screen.blit(
                    mlc, (z_x - mlc.get_width() // 2,
                          z_y - mlc.get_height() // 2)
                )

    def draw_zones(self, network: Network) -> None:
        """Render the network nodes (hubs) and metadata."""
        for zone in network.zones.values():
            px, py = self._get_pixel_coords(float(zone.x), float(zone.y))
            color_name = zone.color if zone.color else "white"
            rgb = getattr(Colors, color_name.upper(), Colors.WHITE).value

            pygame.draw.circle(
                self.screen,
                Colors.WHITE.value,
                (px, py),
                self.config.zone_radius,
            )
            pygame.draw.circle(
                self.screen, rgb, (px, py), self.config.zone_inner_radius
            )

            cords = self.font.render(
                f"{zone.x},{zone.y}", True, Colors.WHITE.value)
            self.screen.blit(
                cords,
                (
                    px - cords.get_width() // 2,
                    py - cords.get_height() // 2 - 30,
                ),
            )

            if zone.max_drones == sys.maxsize:
                cap_text = "inf"
            else:
                cap_text = f"{zone.max_drones}"
            cap = self.font.render(cap_text, True, Colors.BLACK.value)
            self.screen.blit(
                cap, (px - cap.get_width() // 2,
                      py - cap.get_height() // 2 + 14)
            )

            lbl: pygame.Surface | None = None
            if network.start_hub and zone.name == network.start_hub.name:
                lbl = self.font.render("Start", True, Colors.BLACK.value)
            elif network.end_hub and zone.name == network.end_hub.name:
                lbl = self.font.render("End", True, Colors.BLACK.value)
            elif zone.zone_type.display_label:
                lbl = self.font.render(
                    zone.zone_type.display_label, True, Colors.BLACK.value
                )

            if lbl:
                self.screen.blit(
                    lbl, (px - lbl.get_width() // 2,
                          py - lbl.get_height() // 2)
                )
