"""Network drawer component."""

from collections.abc import Callable

import sys
import pygame
import pygame.gfxdraw

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

                mlc_text = f"{con.max_link_capacity}"
                mlc_bg = self.small_font.render(
                    mlc_text, True, Colors.BLACK.value
                )
                mlc_fg = self.small_font.render(
                    mlc_text, True, Colors.WHITE.value
                )
                z_x = (p1[0] + p2[0]) // 2
                z_y = (p1[1] + p2[1]) // 2
                self.screen.blit(
                    mlc_bg,
                    (
                        z_x - mlc_bg.get_width() // 2 + 1,
                        z_y - mlc_bg.get_height() // 2 + 1,
                    ),
                )
                self.screen.blit(
                    mlc_fg,
                    (
                        z_x - mlc_fg.get_width() // 2,
                        z_y - mlc_fg.get_height() // 2,
                    ),
                )

    def draw_zones(self, network: Network) -> None:
        """Render the network nodes (hubs) and metadata."""
        for zone in network.zones.values():
            px, py = self._get_pixel_coords(float(zone.x), float(zone.y))
            color_name = zone.color if zone.color else "white"
            rgb = getattr(Colors, color_name.upper(), Colors.WHITE).value

            pygame.gfxdraw.aacircle(
                self.screen, px, py, self.config.zone_radius,
                Colors.WHITE.value
            )
            pygame.gfxdraw.filled_circle(
                self.screen, px, py, self.config.zone_radius,
                Colors.WHITE.value
            )

            pygame.gfxdraw.aacircle(
                self.screen, px, py, self.config.zone_inner_radius, rgb
            )
            pygame.gfxdraw.filled_circle(
                self.screen, px, py, self.config.zone_inner_radius, rgb
            )

            cords_text = f"{zone.x},{zone.y}"
            cords_bg = self.font.render(cords_text, True, Colors.BLACK.value)
            cords_fg = self.font.render(cords_text, True, Colors.WHITE.value)
            self.screen.blit(
                cords_bg,
                (
                    px - cords_fg.get_width() // 2 + 1,
                    py - cords_fg.get_height() // 2 - 30 + 1,
                ),
            )
            self.screen.blit(
                cords_fg,
                (
                    px - cords_fg.get_width() // 2,
                    py - cords_fg.get_height() // 2 - 30,
                ),
            )

            if zone.max_drones == sys.maxsize:
                cap_text = "inf"
            else:
                cap_text = f"{zone.max_drones}"
            cap_bg = self.font.render(cap_text, True, Colors.BLACK.value)
            cap_fg = self.font.render(cap_text, True, Colors.WHITE.value)
            self.screen.blit(
                cap_bg,
                (
                    px - cap_fg.get_width() // 2 + 1,
                    py - cap_fg.get_height() // 2 + 14 + 1,
                ),
            )
            self.screen.blit(
                cap_fg,
                (
                    px - cap_fg.get_width() // 2,
                    py - cap_fg.get_height() // 2 + 14,
                ),
            )

            lbl_text = ""
            if network.start_hub and zone.name == network.start_hub.name:
                lbl_text = "Start"
            elif network.end_hub and zone.name == network.end_hub.name:
                lbl_text = "End"

            if zone.zone_type.display_label:
                if lbl_text:
                    lbl_text += f" ({zone.zone_type.display_label})"
                else:
                    lbl_text = zone.zone_type.display_label

            lbl: pygame.Surface | None = None
            if lbl_text:
                lbl = self.font.render(lbl_text, True, Colors.BLACK.value)

            if lbl:
                self.screen.blit(
                    lbl, (px - lbl.get_width() // 2,
                          py - lbl.get_height() // 2)
                )
