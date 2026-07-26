"""Configuration for the Pygame renderer."""

from dataclasses import dataclass


@dataclass
class RendererConfig:
    """Configuration settings for Pygame rendering to remove magic numbers."""

    tile_size: int = 80
    margin: int = 80
    panel_height: int = 200

    # Colors
    bg_color: tuple[int, int, int] = (35, 25, 25)
    panel_bg_color: tuple[int, int, int] = (20, 10, 10)
    line_outline_color: tuple[int, int, int] = (100, 100, 100)

    # Font sizes
    font_size_small: int = 14
    font_size_normal: int = 20
    font_size_hud: int = 26
    font_size_large: int = 36

    # Render styles
    connection_line_width: int = 11
    connection_outline_width: int = 8
    zone_radius: int = 24
    zone_inner_radius: int = 22
