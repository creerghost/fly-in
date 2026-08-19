"""Interactive Pygame visualizer for the drone simulation."""

import os
import sys
from typing import Any

import pygame
import pygame.gfxdraw

from ...models import Drone, Network
from ..hud_stats import HudStats
from .colors import Colors
from .config import RendererConfig


class PygameRenderer:
    """Handle graphical display and user interaction using Pygame."""

    def __init__(self, network: Network, play_speed: float = 1.0) -> None:
        """Initialize the Pygame window and calculate canvas bounds."""
        self.network = network
        self.play_speed = play_speed
        self.config = RendererConfig()

        self._init_pygame()
        self._canvas_size()
        self._setup_dimensions()
        self._init_fonts()

        self.drone_img = pygame.transform.scale(
            pygame.image.load(os.path.join("imgs", "drone.bmp")), (45, 45)
        )

    def _init_pygame(self) -> None:
        pygame.init()
        pygame.display.set_caption("Fly-in")
        self.width = self.config.screen_width
        self.height = self.config.screen_height
        self.screen = pygame.display.set_mode((self.width, self.height))

    def _setup_dimensions(self) -> None:
        map_w = max(1, self.canvas_max_x - self.canvas_min_x)
        map_h = max(1, self.canvas_max_y - self.canvas_min_y)

        play_w = self.width - (2 * self.config.margin)
        play_h = (
            self.height - self.config.panel_height - (2 * self.config.margin)
        )

        self.config.tile_size = max(
            10, int(min(play_w / map_w, play_h / map_h))
        )

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

    def _init_fonts(self) -> None:
        self.font = pygame.font.SysFont(None, self.config.font_size_normal)
        self.large_font = pygame.font.SysFont(
            None, self.config.font_size_large
        )
        self.small_font = pygame.font.SysFont(
            None, self.config.font_size_small
        )
        self.hud_font = pygame.font.SysFont(None, self.config.font_size_hud)

    def _get_pixel_coords(self, x: float, y: float) -> tuple[int, int]:
        """Convert grid coordinates to Pygame pixel coordinates."""
        grid_center_x = (self.canvas_min_x + self.canvas_max_x) / 2
        grid_center_y = (self.canvas_min_y + self.canvas_max_y) / 2

        screen_center_x = self.width / 2
        screen_center_y = (self.height - self.config.panel_height) / 2

        px = (x - grid_center_x) * self.config.tile_size + screen_center_x
        py = (grid_center_y - y) * self.config.tile_size + screen_center_y

        return int(px), int(py)

    def handle_events(self, dt: float) -> dict[str, Any]:
        """
        Process keyboard events for playback control.

        Handles pausing, scrubbing time, and quitting.
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

    def render(
        self, current_time: float, max_turn: float, drones: list[Drone]
    ) -> None:
        """Render the complete simulation frame."""
        self.screen.fill(self.config.bg_color)

        hud_stats = HudStats.from_drones(drones, self.network, current_time)

        self._draw_connections()
        self._draw_zones()
        self._draw_drones(current_time, drones)
        self._draw_hud(current_time, hud_stats)

        pygame.display.flip()

    def _draw_connections(self) -> None:
        """Render network edges between zones."""
        for con in self.network.connections:
            z1 = self.network[con.name1]
            z2 = self.network[con.name2]
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
            mlc_bg = self.small_font.render(mlc_text, True, Colors.BLACK.value)
            mlc_fg = self.small_font.render(mlc_text, True, Colors.WHITE.value)
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

    def _draw_zones(self) -> None:
        """Render network hubs and metadata."""
        for zone in self.network.zones.values():
            px, py = self._get_pixel_coords(float(zone.x), float(zone.y))
            color_name = zone.color if zone.color else "white"
            rgb = getattr(Colors, color_name.upper(), Colors.WHITE).value

            pygame.gfxdraw.aacircle(
                self.screen,
                px,
                py,
                self.config.zone_radius,
                Colors.WHITE.value,
            )
            pygame.gfxdraw.filled_circle(
                self.screen,
                px,
                py,
                self.config.zone_radius,
                Colors.WHITE.value,
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
            if (
                self.network.start_hub
                and zone.name == self.network.start_hub.name
            ):
                lbl_text = "Start"
            elif (
                self.network.end_hub and zone.name == self.network.end_hub.name
            ):
                lbl_text = "End"

            if zone.zone_type.display_label:
                if lbl_text:
                    lbl_text += f" ({zone.zone_type.display_label})"
                else:
                    lbl_text = zone.zone_type.display_label

            if lbl_text:
                lbl = self.font.render(lbl_text, True, Colors.BLACK.value)
                self.screen.blit(
                    lbl,
                    (
                        px - lbl.get_width() // 2,
                        py - lbl.get_height() // 2,
                    ),
                )

    def _draw_drones(self, t_current: float, drones: list[Drone]) -> None:
        """Calculate and draw drones on the network."""
        drone_groups: dict[tuple[int, int], list[Drone]] = {}
        drone_transits: dict[tuple[int, int], bool] = {}

        for drone in drones:
            start_zone_name, end_zone_name, t_smooth, transit = (
                drone.get_render_state(t_current)
            )

            z1 = self.network[start_zone_name]
            z2 = self.network[end_zone_name]

            start_x, start_y = self._get_pixel_coords(float(z1.x), float(z1.y))
            end_x, end_y = self._get_pixel_coords(float(z2.x), float(z2.y))

            px = int(start_x + (end_x - start_x) * t_smooth)
            py = int(start_y + (end_y - start_y) * t_smooth)

            coord = (px, py)
            if coord not in drone_groups:
                drone_groups[coord] = []
            drone_groups[coord].append(drone)
            drone_transits[coord] = transit

        for coord, d_list in drone_groups.items():
            self._draw_drone_marker(
                coord[0], coord[1], d_list, drone_transits[coord]
            )

    def _draw_drone_marker(
        self, px: int, py: int, drones_list: list[Drone], transit: bool
    ) -> None:
        """Render drone bitmap and label at given pixel position."""
        label = (
            drones_list[0].id
            if len(drones_list) == 1
            else f"{len(drones_list)}D"
        )
        text = self.font.render(label, True, Colors.WHITE.value)

        rect_w = text.get_width() + 5
        rect_h = text.get_height() + 5
        color = Colors.RED.value if not transit else Colors.GRAY.value

        rect = pygame.Rect(0, 0, rect_w, rect_h)
        rect.center = (px, py - 25)
        rect_outline = pygame.Rect(0, 0, rect_w + 2, rect_h + 2)
        rect_outline.center = rect.center

        pygame.draw.rect(
            self.screen, Colors.WHITE.value, rect_outline, border_radius=4
        )
        pygame.draw.rect(self.screen, color, rect, border_radius=3)

        self.screen.blit(self.drone_img, (px - 23, py - 22))
        self.screen.blit(
            text,
            (
                px - text.get_width() // 2,
                (py - 25) - text.get_height() // 2,
            ),
        )

    def _draw_hud(self, current_time: float, stats: HudStats) -> None:
        """Render turn counter, analytics panel, and keyboard controls."""
        self.screen.blit(
            self.large_font.render(
                f"Turn {int(current_time)}", True, Colors.WHITE.value
            ),
            (10, 10),
        )

        panel_rect = pygame.Rect(
            0,
            self.height - self.config.panel_height,
            self.width,
            self.config.panel_height,
        )
        pygame.draw.rect(self.screen, self.config.panel_bg_color, panel_rect)
        pygame.draw.line(
            self.screen,
            self.config.line_outline_color,
            (0, self.height - self.config.panel_height),
            (self.width, self.height - self.config.panel_height),
            2,
        )

        metrics = [
            ("Total Drones:", str(stats.total_drones)),
            ("Active Drones:", str(stats.active_drones)),
            ("Avg Turns per drone:", f"{stats.avg_turns:.1f}"),
            ("Total Cost:", f"{stats.total_cost}"),
        ]

        start_x = 40
        start_y = self.height - self.config.panel_height + 40

        for i, (label, value) in enumerate(metrics):
            lbl_surf = self.hud_font.render(label, True, Colors.WHITE.value)
            val_surf = self.hud_font.render(value, True, Colors.YELLOW.value)

            y_pos = start_y + (i * 35)
            self.screen.blit(lbl_surf, (start_x, y_pos))
            self.screen.blit(val_surf, (start_x + 200, y_pos))

        controls = [
            ("[LEFT] / [RIGHT]", "Scrub Time"),
            ("[SPACE]", "Play / Pause"),
            ("[R]", "Reset"),
            ("[ESC]", "Quit"),
        ]

        ctrl_x = self.width - 320
        for i, (key, desc) in enumerate(controls):
            key_surf = self.hud_font.render(key, True, Colors.YELLOW.value)
            desc_surf = self.hud_font.render(desc, True, Colors.WHITE.value)

            y_pos = start_y + (i * 35)
            self.screen.blit(key_surf, (ctrl_x, y_pos))
            self.screen.blit(desc_surf, (ctrl_x + 180, y_pos))

    def reset(self) -> None:
        """Reset internal state."""

    def cleanup(self) -> None:
        """Clean up renderer resources."""
        pygame.quit()
