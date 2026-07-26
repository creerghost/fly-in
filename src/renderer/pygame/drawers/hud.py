"""HUD drawer component."""

import pygame

from ...hud_stats import HudStats
from ..colors import Colors
from ..config import RendererConfig


class HUDDrawer:
    """Draws the analytics HUD and text overlays."""

    def __init__(
        self,
        screen: pygame.Surface,
        config: RendererConfig,
        large_font: pygame.font.Font,
        hud_font: pygame.font.Font,
        width: int,
        height: int,
    ) -> None:
        """Initialize the HUD drawer."""
        self.screen = screen
        self.config = config
        self.large_font = large_font
        self.hud_font = hud_font
        self.width = width
        self.height = height

    def draw_overlays(self, current_time: float) -> None:
        """Render the global turn counter."""
        self.screen.blit(
            self.large_font.render(
                f"Turn {int(current_time)}", True, Colors.WHITE.value
            ),
            (10, 10),
        )

    def draw_hud(self, stats: HudStats) -> None:
        """Render the analytics panel and keyboard controls."""
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
