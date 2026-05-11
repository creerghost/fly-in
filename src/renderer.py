import os
import sys
import pygame
from collections import defaultdict
from src.network import Network
from src.drone import Drone

COLORS: dict[str, tuple[int, int, int]] = {
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
    "rainbow": (255, 105, 180),
}


class Renderer:
    def __init__(self, network: Network):
        self.network = network
        self.canvas_size()

        pygame.init()
        pygame.display.set_caption("Fly-in Drone Simulator")

        # Graphic sizing definitions
        self.tile_size = 80
        self.margin = 80

        self.width = (self.canvas_max_x - self.canvas_min_x) \
            * self.tile_size + 2 * self.margin
        self.height = (self.canvas_max_y - self.canvas_min_y) \
            * self.tile_size + 2 * self.margin

        self.screen = pygame.display.set_mode((self.width, self.height))
        self.font = pygame.font.SysFont(None, 20)
        self.large_font = pygame.font.SysFont(None, 36)

    def canvas_size(self) -> None:
        if not self.network.zones:
            raise ValueError("Zones not defined")

        x_coords = [zone.x for zone in self.network.zones.values()]
        y_coords = [zone.y for zone in self.network.zones.values()]

        self.canvas_min_x = min(x_coords)
        self.canvas_max_x = max(x_coords)
        self.canvas_min_y = min(y_coords)
        self.canvas_max_y = max(y_coords)

    def _get_pixel_coords(self, x: int, y: int) -> tuple[int, int]:
        px = (x - self.canvas_min_x) * self.tile_size + self.margin
        py = (self.canvas_max_y - y) * self.tile_size + self.margin

        # chessboard-like cords to prevent connection overlaps
        px += 30 if y % 2 == 0 else -10
        py += 30 if x % 2 != 0 else -10

        return px, py

    def render_step(
        self, turn: int, drones: list[Drone], turn_output: list[str]
    ) -> None:
        self.pause: bool = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
                (event.type == pygame.KEYDOWN and
                 event.key == pygame.K_ESCAPE):
                print("Bye!")
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.pause = True
                self._paused()

        self.screen.fill((35, 10, 10))

        # Draw the Turn overlay
        turn_text = self.large_font.render(
            f"Turn {turn}", True, COLORS["white"])
        app_name = self.large_font.render(
            "Fly-in visualizer", True, COLORS["white"])
        self.screen.blit(turn_text, (10, 10))
        self.screen.blit(app_name, (self.width // 2 - 100, 10))
        # 1. Draw Connection Lines
        for con in self.network.connections:
            z1 = self.network.zones.get(con.name1)
            z2 = self.network.zones.get(con.name2)
            if z1 and z2:
                p1 = self._get_pixel_coords(z1.x, z1.y)
                p2 = self._get_pixel_coords(z2.x, z2.y)
                pygame.draw.line(self.screen, COLORS["white"], p1, p2, 5)
                pygame.draw.line(self.screen, (100, 100, 100), p1, p2, 3)

        start_name = (self.network.parser.start_hub["name"]
                      if self.network.parser.start_hub else "")
        end_name = (self.network.parser.end_hub["name"]
                    if self.network.parser.end_hub else "")

        # 2. Draw Zones
        for zone in self.network.zones.values():
            px, py = self._get_pixel_coords(zone.x, zone.y)
            color_name = zone.color if zone.color else "white"
            rgb = COLORS.get(color_name.lower(), COLORS["white"])

            pygame.draw.circle(self.screen, COLORS["white"], (px, py), 24)
            pygame.draw.circle(self.screen, rgb, (px, py), 22)
            cords_text = self.font.render(f"{zone.x},{zone.y}", True,
                                          COLORS["white"])
            self.screen.blit(cords_text, (px - cords_text.get_width() // 2,
                                          py - cords_text.get_height() // 2
                                          - 30))
            if zone.name == start_name:
                lbl = self.font.render("Start", True, COLORS["black"])
                self.screen.blit(
                    lbl,
                    (px - lbl.get_width() // 2, py - lbl.get_height() // 2))
            elif zone.name == end_name:
                lbl = self.font.render("End", True, COLORS["black"])
                self.screen.blit(
                    lbl,
                    (px - lbl.get_width() // 2, py - lbl.get_height() // 2))
            elif zone.zone_type == "restricted":
                lbl = self.font.render("R", True, COLORS["black"])
                self.screen.blit(
                    lbl,
                    (px - lbl.get_width() // 2, py - lbl.get_height() // 2))
            elif zone.zone_type == "blocked":
                lbl = self.font.render("B", True, COLORS["black"])
                self.screen.blit(
                    lbl,
                    (px - lbl.get_width() // 2, py - lbl.get_height() // 2))
            elif zone.zone_type == "priority":
                lbl = self.font.render("P", True, COLORS["black"])
                self.screen.blit(
                    lbl,
                    (px - lbl.get_width() // 2, py - lbl.get_height() // 2))

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
            loc_zone = self.network.zones.get(loc)
            if loc_zone:
                px, py = self._get_pixel_coords(loc_zone.x, loc_zone.y)
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
                self._draw_drone_marker(mid_px, mid_py,
                                        drones_in_transit, transit=True)

        # Maintain text output format to standard terminal
        if turn_output:
            print(" ".join(turn_output))

        pygame.display.flip()

    def _paused(self) -> None:
        while self.pause:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and \
                        event.key == pygame.K_SPACE:
                    self.pause = False
                if event.type == pygame.QUIT or \
                    (event.type == pygame.KEYDOWN and
                     event.key == pygame.K_ESCAPE):
                    print("Bye!")
                    pygame.quit()
                    sys.exit(0)

    def _draw_drone_marker(
        self, px: int, py: int, drones_list: list[Drone], transit: bool = False
    ) -> None:
        label = (drones_list[0].id if len(drones_list) == 1
                 else f"{len(drones_list)}D")
        text = self.font.render(label, True, COLORS["white"])

        rect_w = text.get_width() + 5
        rect_h = text.get_height() + 5
        color = COLORS["red"] if not transit else COLORS["gray"]
        # Hover slightly above the node
        rect = pygame.Rect(0, 0, rect_w, rect_h)
        rect.center = (px, py - 25)
        rect_outline = pygame.Rect(0, 0, rect_w + 2, rect_h + 2)
        rect_outline.center = rect.center
        pygame.draw.rect(self.screen, COLORS["white"], rect_outline,
                         border_radius=4)
        pygame.draw.rect(self.screen, color, rect, border_radius=3)

        drn_0 = pygame.image.load(os.path.join("imgs", "drone.bmp"))
        drn = pygame.transform.scale(drn_0, (45, 45))
        drn_center = (px, py - 25)

        self.screen.blit(drn, (px - 23, py - 22))
        self.screen.blit(
            text,
            (drn_center[0] - text.get_width() // 2,
             drn_center[1] - text.get_height() // 2)
        )
