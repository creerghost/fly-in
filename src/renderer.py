import os
import sys
import pygame
from enum import Enum
from src.network import Network
from src.drone import Drone
from typing import List, Tuple, Optional


class Colors(Enum):
    """
    Stores colors used for rendering.
    """
    GREEN = (34, 139, 34)
    BLUE = (65, 105, 225)
    RED = (220, 20, 60)
    YELLOW = (255, 215, 0)
    ORANGE = (255, 140, 0)
    CYAN = (0, 255, 255)
    PURPLE = (128, 0, 128)
    BROWN = (139, 69, 19)
    LIME = (50, 205, 50)
    MAGENTA = (255, 0, 255)
    GOLD = (255, 215, 0)
    BLACK = (40, 40, 40)
    DARKRED = (139, 0, 0)
    MAROON = (128, 0, 0)
    CRIMSON = (220, 20, 60)
    VIOLET = (238, 130, 238)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    RAINBOW = (255, 105, 180)


class Renderer:
    """
    Handles the graphical display of the simulation using Pygame.
    """
    def __init__(self, network: Network, delay: float) -> None:
        """
        Initialize the Pygame window and calculate canvas bounds.
        """
        self.network = network
        self.canvas_size()

        pygame.init()
        pygame.display.set_caption("Fly-in Drone Simulator")

        self.tile_size = 80
        self.margin = 80

        self.width = (self.canvas_max_x - self.canvas_min_x) \
            * self.tile_size + 2 * self.margin
        self.height = (self.canvas_max_y - self.canvas_min_y) \
            * self.tile_size + 2 * self.margin

        self.screen = pygame.display.set_mode((self.width, self.height))
        self.font = pygame.font.SysFont(None, 20)
        self.large_font = pygame.font.SysFont(None, 36)
        self.clock = pygame.time.Clock()
        self.turn_duration = delay

        self.drone_img = pygame.transform.scale(
            pygame.image.load(os.path.join("imgs", "drone.bmp")), (45, 45)
        )

    def canvas_size(self) -> None:
        """
        Determine the boundaries of the grid based on zone coordinates.
        """
        if not self.network.zones:
            raise ValueError("Zones not defined")

        x_coords = [zone.x for zone in self.network.zones.values()]
        y_coords = [zone.y for zone in self.network.zones.values()]

        self.canvas_min_x = min(x_coords)
        self.canvas_max_x = max(x_coords)
        self.canvas_min_y = min(y_coords)
        self.canvas_max_y = max(y_coords)

    def _get_pixel_coords(self, x: int, y: int) -> Tuple[int, int]:
        """
        Convert grid coordinates to Pygame pixel coordinates.
        """
        px = (x - self.canvas_min_x) * self.tile_size + self.margin
        py = (self.canvas_max_y - y) * self.tile_size + self.margin

        # chessboard offset to prevent connection overlaps
        px += 30 if y % 2 == 0 else -10
        py += 30 if x % 2 != 0 else -10

        return px, py

    def _get_drone_target(self, drone: Drone) -> Tuple[float, float]:
        """
        Compute the target pixel position for a drone from current_location.
        Returns pixel coords if at a node, or the midpoint if in transit.
        """
        loc = drone.current_location
        if "-" not in loc:
            zone = self.network.zones.get(loc)
            if zone:
                px, py = self._get_pixel_coords(zone.x, zone.y)
                return float(px), float(py)
        else:
            z1_name, z2_name = loc.split("-")
            z1 = self.network.zones.get(z1_name)
            z2 = self.network.zones.get(z2_name)
            if z1 and z2:
                p1 = self._get_pixel_coords(z1.x, z1.y)
                p2 = self._get_pixel_coords(z2.x, z2.y)
                return (p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0
        return 0.0, 0.0

    def animate_turn(
        self, turn: int, drones: List[Drone], turn_output: List[str]
    ) -> None:
        """
        Animate all drones moving from prev_pos to next_pos over
        self.turn_duration seconds at 60fps.
        """
        for drone in drones:
            target = self._get_drone_target(drone)
            if not drone.animation_ready:
                # first call: seed everything so the lerp has valid endpoints
                drone.prev_pos = target
                drone.next_pos = target
                drone.draw_pos = target
                drone.animation_ready = True
            else:
                drone.prev_pos = drone.next_pos
                drone.next_pos = target

        # print terminal output once before the animation starts
        if turn_output:
            print(" ".join(turn_output))

        start_name = (self.network.parser.start_hub["name"]
                      if self.network.parser.start_hub else "")
        end_name = (self.network.parser.end_hub["name"]
                    if self.network.parser.end_hub else "")

        # all drawing is inside this loop so the window rerenders every frame
        elapsed = 0.0
        while elapsed < self.turn_duration:
            dt = self.clock.tick(60) / 1000.0
            elapsed += dt
            t = min(elapsed / self.turn_duration, 1.0)
            # smooth step - eases in and out at each node
            t_smooth = t * t * (3.0 - 2.0 * t)

            # lerp every drone toward its target this frame
            for drone in drones:
                sx, sy = drone.prev_pos
                ex, ey = drone.next_pos
                drone.draw_pos = (
                    sx + (ex - sx) * t_smooth,
                    sy + (ey - sy) * t_smooth,
                )

            # event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE
                ):
                    print("Bye!")
                    pygame.quit()
                    sys.exit(0)
                if (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_SPACE):
                    self._paused()
                    self.clock.tick()

            # background
            self.screen.fill((35, 10, 10))

            # turn and title overlay
            self.screen.blit(
                self.large_font.render(
                    f"Turn {turn}", True, Colors.WHITE.value),
                (10, 10))
            self.screen.blit(
                self.large_font.render(
                    "Fly-in visualizer", True, Colors.WHITE.value),
                (self.width // 2 - 100, 10))

            # connection lines
            for con in self.network.connections:
                z1 = self.network.zones.get(con.name1)
                z2 = self.network.zones.get(con.name2)
                if z1 and z2:
                    p1 = self._get_pixel_coords(z1.x, z1.y)
                    p2 = self._get_pixel_coords(z2.x, z2.y)
                    pygame.draw.line(
                        self.screen, Colors.WHITE.value, p1, p2, 5)
                    pygame.draw.line(
                        self.screen, (100, 100, 100), p1, p2, 3)

            # zones
            for zone in self.network.zones.values():
                px, py = self._get_pixel_coords(zone.x, zone.y)
                color_name = zone.color if zone.color else "white"
                rgb = getattr(Colors, color_name.upper(), Colors.WHITE).value

                pygame.draw.circle(
                    self.screen, Colors.WHITE.value, (px, py), 24)
                pygame.draw.circle(self.screen, rgb, (px, py), 22)

                cords = self.font.render(
                    f"{zone.x},{zone.y}", True, Colors.WHITE.value)
                self.screen.blit(
                    cords,
                    (px - cords.get_width() // 2,
                     py - cords.get_height() // 2 - 30))

                cap = self.font.render(
                    f"{zone.max_drones}", True, Colors.BLACK.value)
                self.screen.blit(
                    cap,
                    (px - cap.get_width() // 2,
                     py - cap.get_height() // 2 + 14))

                if zone.name == start_name:
                    lbl: Optional[pygame.Surface] = self.font.render(
                        "Start", True, Colors.BLACK.value)
                elif zone.name == end_name:
                    lbl = self.font.render("End", True, Colors.BLACK.value)
                elif zone.zone_type == "restricted":
                    lbl = self.font.render("R", True, Colors.BLACK.value)
                elif zone.zone_type == "blocked":
                    lbl = self.font.render("B", True, Colors.BLACK.value)
                elif zone.zone_type == "priority":
                    lbl = self.font.render("P", True, Colors.BLACK.value)
                else:
                    lbl = None

                if lbl:
                    self.screen.blit(
                        lbl,
                        (px - lbl.get_width() // 2,
                         py - lbl.get_height() // 2))

            # drones at their interpolated position
            for drone in drones:
                dpx, dpy = drone.draw_pos
                transit = "-" in drone.current_location
                self._draw_drone_marker(int(dpx), int(dpy), [drone], transit)

            pygame.display.flip()

        # snap prev_pos to next_pos once animation completes
        for drone in drones:
            drone.prev_pos = drone.next_pos

    def _paused(self) -> None:
        """
        Halt the render loop until Space is pressed again.
        """
        paused = True
        while paused:
            for event in pygame.event.get():
                if (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_SPACE):
                    paused = False
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE
                ):
                    print("Bye!")
                    pygame.quit()
                    sys.exit(0)

    def _draw_drone_marker(
        self, px: int, py: int, drones_list: List[Drone],
        transit: bool = False
    ) -> None:
        """
        Render the drone bitmap and label at the given pixel position.
        Red marker for nodes, gray for in-transit.
        """
        label = (drones_list[0].id if len(drones_list) == 1
                 else f"{len(drones_list)}D")
        text = self.font.render(label, True, Colors.WHITE.value)

        rect_w = text.get_width() + 5
        rect_h = text.get_height() + 5
        color = Colors.RED.value if not transit else Colors.GRAY.value

        rect = pygame.Rect(0, 0, rect_w, rect_h)
        rect.center = (px, py - 25)
        rect_outline = pygame.Rect(0, 0, rect_w + 2, rect_h + 2)
        rect_outline.center = rect.center

        pygame.draw.rect(
            self.screen, Colors.WHITE.value, rect_outline, border_radius=4)
        pygame.draw.rect(self.screen, color, rect, border_radius=3)

        self.screen.blit(self.drone_img, (px - 23, py - 22))
        self.screen.blit(
            text,
            (px - text.get_width() // 2,
             (py - 25) - text.get_height() // 2))
