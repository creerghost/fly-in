import sys
from typing import Tuple, List, Dict
import pygame
from collections import defaultdict
from src.network import Network
from src.drone import Drone

COLORS: Dict[str, Tuple[int, int, int]] = {
    "green": (34, 139, 34),
    "blue": (65, 105, 225),
    "red": (220, 20, 60),
    "yellow": (255, 215, 0),
    "orange": (255, 140, 0),
    "cyan": (0, 255, 255),
    "purple": (128, 0, 128),
    "brown": (139, 69, 19),
    "lime": (50, 205, 50),
    "magenta": (255, 0, 255),
    "gold": (255, 215, 0),
    "black": (40, 40, 40),
    "darkred": (139, 0, 0),
    "maroon": (128, 0, 0),
    "crimson": (220, 20, 60),
    "violet": (238, 130, 238),
    "white": (255, 255, 255),
    "gray": (128, 128, 128),
    "rainbow": (255, 105, 180),  # Hot pink fallback
}


class Renderer:
    def __init__(self, network: Network):
        self.network = network
        self.network.canvas_size()  # Initialize the min/max coordinate properties
        
        pygame.init()
        pygame.display.set_caption("Fly-in Drone Simulator")
        
        # Graphic sizing definitions
        self.tile_size = 80
        self.margin = 60
        
        width = (self.network.canvas_max_x - self.network.canvas_min_x) * self.tile_size + 2 * self.margin
        height = (self.network.canvas_max_y - self.network.canvas_min_y) * self.tile_size + 2 * self.margin
        
        self.screen = pygame.display.set_mode((width, height))
        self.font = pygame.font.SysFont(None, 24)
        self.large_font = pygame.font.SysFont(None, 36)

    def _get_pixel_coords(self, x: int, y: int) -> Tuple[int, int]:
        px = (x - self.network.canvas_min_x) * self.tile_size + self.margin
        py = (self.network.canvas_max_y - y) * self.tile_size + self.margin
        return px, py

    def render_step(self, turn: int, drones: List[Drone], turn_output: List[str]) -> None:
        # Event pump required to prevent OS "Application Not Responding" crashes
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

        # Fill screen with dark gray background
        self.screen.fill((30, 30, 30))
        
        # Draw the Turn overlay
        turn_text = self.large_font.render(f"Turn {turn}", True, (255, 255, 255))
        self.screen.blit(turn_text, (20, 20))

        # 1. Draw Connection Lines
        for con in self.network.connections:
            z1 = self.network.zones.get(con.name1)
            z2 = self.network.zones.get(con.name2)
            if z1 and z2:
                p1 = self._get_pixel_coords(z1.x, z1.y)
                p2 = self._get_pixel_coords(z2.x, z2.y)
                pygame.draw.line(self.screen, (100, 100, 100), p1, p2, 3)

        start_name = self.network.parser.start_hub["name"] if self.network.parser.start_hub else ""
        end_name = self.network.parser.end_hub["name"] if self.network.parser.end_hub else ""

        # 2. Draw Zones (Nodes)
        for zone in self.network.zones.values():
            px, py = self._get_pixel_coords(zone.x, zone.y)
            color_name = zone.color if zone.color else "white"
            rgb = COLORS.get(color_name.lower(), (255, 255, 255))
            
            pygame.draw.circle(self.screen, rgb, (px, py), 18)
            
            if zone.name == start_name:
                lbl = self.font.render("S", True, (0, 0, 0))
                self.screen.blit(lbl, (px - lbl.get_width()//2, py - lbl.get_height()//2))
            elif zone.name == end_name:
                lbl = self.font.render("E", True, (0, 0, 0))
                self.screen.blit(lbl, (px - lbl.get_width()//2, py - lbl.get_height()//2))

        # Group drones by their current location
        location_counts = defaultdict(list)
        transit_counts = defaultdict(list)
        for drone in drones:
            if "-" not in drone.current_location:
                location_counts[drone.current_location].append(drone)
            else:
                transit_counts[drone.current_location].append(drone)

        # 3. Draw Drones on exact locations
        for loc, drones_in_loc in location_counts.items():
            zone = self.network.zones.get(loc)
            if zone:
                px, py = self._get_pixel_coords(zone.x, zone.y)
                self._draw_drone_marker(px, py, drones_in_loc)

        # 4. Draw mid-transit Drones between locations
        for loc, drones_in_transit in transit_counts.items():
            z1_name, z2_name = loc.split("-")
            z1 = self.network.zones.get(z1_name)
            z2 = self.network.zones.get(z2_name)
            if z1 and z2:
                p1 = self._get_pixel_coords(z1.x, z1.y)
                p2 = self._get_pixel_coords(z2.x, z2.y)
                mid_px = (p1[0] + p2[0]) // 2
                mid_py = (p1[1] + p2[1]) // 2
                self._draw_drone_marker(mid_px, mid_py, drones_in_transit)

        # Maintain text output format to standard terminal
        if turn_output:
            print(" ".join(turn_output))

        pygame.display.flip()

    def _draw_drone_marker(self, px: int, py: int, drones_list: List[Drone]) -> None:
        label = drones_list[0].id if len(drones_list) == 1 else f"{len(drones_list)}D"
        text = self.font.render(label, True, (255, 255, 255))
        
        rect_w = text.get_width() + 10
        rect_h = text.get_height() + 6
        
        # Hover slightly above the node
        rect = pygame.Rect(0, 0, rect_w, rect_h)
        rect.center = (px, py - 25)
        
        pygame.draw.rect(self.screen, (220, 20, 20), rect, border_radius=3)
        self.screen.blit(text, (rect.centerx - text.get_width()//2, rect.centery - text.get_height()//2))
