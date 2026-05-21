import os
import sys
import math
import pygame
from enum import Enum
from src.network import Network
from src.drone import Drone
from typing import List, Tuple, Optional, Dict


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
    Features an interactive time-scrubbing loop and a Heads-Up Display (HUD)
    for simulation analytics.
    """
    def __init__(self, network: Network, play_speed: float = 1) -> None:
        """
        Initialize the Pygame window and calculate canvas bounds.
        """
        self.network = network
        self._canvas_size()
        self.play_speed = play_speed

        pygame.init()
        pygame.display.set_caption("Fly-in Drone Simulator")

        self.tile_size = 80
        self.margin = 80
        self.panel_height = 200

        self.width = (self.canvas_max_x - self.canvas_min_x) \
            * self.tile_size + 2 * self.margin + 50
        self.height = (self.canvas_max_y - self.canvas_min_y) \
            * self.tile_size + 2 * self.margin + self.panel_height
        self._extend_width()
        # self._adjust_tile_size()
        self.current_time = 0.0
        # ensures turn outputs are printed only when going forward in time
        self.highest_turn_printed = 0
        self.scrub_speed = self.play_speed * 3
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.font = pygame.font.SysFont(None, 20)
        self.large_font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 14)
        self.hud_font = pygame.font.SysFont(None, 26)
        self.clock = pygame.time.Clock()
        self.drone_img = pygame.transform.scale(
            pygame.image.load(os.path.join("imgs", "drone.bmp")), (45, 45)
        )

    def _extend_width(self) -> None:
        width = 650 - self.width
        if width <= 0:
            return
        self.width += width

    def _canvas_size(self) -> None:
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
        grid_center_x = (self.canvas_min_x + self.canvas_max_x) / 2
        grid_center_y = (self.canvas_min_y + self.canvas_max_y) / 2

        screen_center_x = self.width / 2
        screen_center_y = (self.height - self.panel_height) / 2

        px = (x - grid_center_x) * self.tile_size + screen_center_x
        py = (grid_center_y - y) * self.tile_size + screen_center_y

        # chessboard offset to prevent connection overlaps
        px += 30 if y % 2 == 0 else -10
        py += 30 if x % 2 != 0 else -10

        return int(px), int(py)

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

    def run(self, drones: List[Drone]) -> None:
        """
        Start the interactive visualizer loop.
        Calculates HUD metrics and continuously renders drones, maps,
        and analytics while processing user inputs.
        """
        max_turn = max(d.path[-1][1] for d in drones)
        total_cost: float = 0.0
        total_cost_stats: int = 0
        for d in drones:
            for i in range(0, len(d.path) - 1):
                prev_node = d.path[i][0]
                next_node = d.path[i + 1][0]
                if prev_node == next_node:
                    total_cost += 1
                    total_cost_stats += 1
                else:
                    if self.network.zones[next_node].zone_type == "restricted":
                        total_cost += 2
                        total_cost_stats += 2
                    elif self.network.zones[next_node].zone_type == "normal":
                        total_cost += 1
                        total_cost_stats += 1
                    elif self.network.zones[next_node].zone_type == "priority":
                        total_cost += 0.8
                        total_cost_stats += 1

        self.total_cost = total_cost_stats
        self.total_drones = len(drones)
        self.avg_turns = (sum(d.path[-1][1] for d in drones) /
                          self.total_drones if self.total_drones else 0.0)

        self.is_paused = False

        while True:
            dt = self.clock.tick(60) / 1000.0

            self._handle_time_and_events(max_turn, dt)
            self._print_turn_output(drones)

            self.screen.fill((35, 25, 25))

            self._draw_overlays()
            self._draw_connections()
            self._draw_zones()
            self._draw_drones(drones)
            self._draw_hud()

            pygame.display.flip()

    def _handle_time_and_events(self, max_turn: float, dt: float) -> None:
        """
        Process keyboard events for pausing, scrubbing time, and quitting.
        Updates the global `current_time` based on user input and delta time.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Bye!")
                pygame.quit()
                sys.exit(0)
            if (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_SPACE):
                self.is_paused = not self.is_paused

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            print("Bye!")
            pygame.quit()
            sys.exit(0)

        play_speed = 0.0 if self.is_paused else self.play_speed
        if keys[pygame.K_LEFT]:
            self.current_time -= dt * self.scrub_speed * 0.65
        elif keys[pygame.K_RIGHT]:
            self.current_time += dt * self.scrub_speed
        elif keys[pygame.K_r]:
            self.current_time = 0.0
            self.highest_turn_printed = 0
        else:
            self.current_time += dt * play_speed

        self.current_time = max(0.0, min(float(max_turn), self.current_time))

    def _get_loc(self, drone: Drone, t: int) -> str:
        """
        Determine the string representation of a drone's location at a specific
        integer turn. Formats mid-transit locations as `zone1-zone2`.
        """
        if t >= drone.path[-1][1]:
            return drone.path[-1][0]
        for i in range(len(drone.path) - 1):
            curr_zone, curr_turn = drone.path[i]
            next_zone, next_turn = drone.path[i + 1]
            if t == curr_turn:
                return curr_zone
            elif curr_turn < t < next_turn:
                if curr_zone == next_zone:
                    return curr_zone
                else:
                    return f"{curr_zone}-{next_zone}"
        return drone.path[-1][0]

    def _print_turn_output(self, drones: List[Drone]) -> None:
        """
        Print drone movements to standard output as simulation time advances.
        Only prints when the time scrubs forward past a new integer turn.
        """
        while self.highest_turn_printed < int(self.current_time):
            self.highest_turn_printed += 1
            t = self.highest_turn_printed
            turn_output = []
            for drone in drones:
                loc_now = self._get_loc(drone, t)
                loc_prev = self._get_loc(drone, t - 1)
                if loc_now != loc_prev:
                    turn_output.append(f"{drone.id}-{loc_now}")
            if turn_output:
                print(" ".join(turn_output))

    def _draw_overlays(self) -> None:
        """
        Render the global turn counter and window title.
        """
        self.screen.blit(
            self.large_font.render(
                f"Turn {int(self.current_time)}",
                True,
                Colors.WHITE.value),
            (10, 10))
        # self.screen.blit(
        #     self.large_font.render(
        #         "Fly-in visualizer",
        #         True,
        #         Colors.WHITE.value),
        #     (self.width // 2 - 100, 10))

    def _draw_connections(self) -> None:
        """
        Render the network edges between zones, slightly offset to prevent
        overlapping bidirectional connections.
        """
        for con in self.network.connections:
            z1 = self.network.zones.get(con.name1)
            z2 = self.network.zones.get(con.name2)
            if z1 and z2:
                p1 = self._get_pixel_coords(z1.x, z1.y)
                p2 = self._get_pixel_coords(z2.x, z2.y)
                pygame.draw.line(
                    self.screen, Colors.WHITE.value, p1, p2, 11)
                pygame.draw.line(
                    self.screen, (100, 100, 100), p1, p2, 8)
                mlc = self.small_font.render(f"{con.max_link_capacity}",
                                             True, Colors.WHITE.value)
                z_x = (p1[0] + p2[0]) // 2
                z_y = (p1[1] + p2[1]) // 2
                self.screen.blit(
                        mlc,
                        (z_x - mlc.get_width() // 2,
                         z_y - mlc.get_height() // 2))

    def _draw_zones(self) -> None:
        """
        Render the network nodes (hubs) along with their metadata, capacity,
        and type abbreviations (e.g. 'Start', 'End', 'R', 'P').
        """
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

            if (self.network.parser.start_hub and
                    zone.name == self.network.parser.start_hub["name"]):
                lbl: Optional[pygame.Surface] = self.font.render(
                    "Start", True, Colors.BLACK.value)
            elif (self.network.parser.end_hub and
                    zone.name == self.network.parser.end_hub["name"]):
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

    def _draw_drones(self, drones: List[Drone]) -> None:
        """
        Calculate interpolated drone positions based on the current time and
        render their markers. Groups overlapping drones visually.
        """
        drone_groups: Dict[Tuple[int, int], List[Drone]] = {}
        drone_transits: Dict[Tuple[int, int], bool] = {}
        self.active_drones = 0

        for drone in drones:
            t_current = self.current_time
            if t_current >= drone.path[-1][1]:
                zone = self.network.zones[drone.path[-1][0]]
                px, py = self._get_pixel_coords(zone.x, zone.y)
                transit = False
            elif t_current <= drone.path[0][1]:
                zone = self.network.zones[drone.path[0][0]]
                px, py = self._get_pixel_coords(zone.x, zone.y)
                transit = False
            else:
                for i in range(len(drone.path) - 1):
                    curr_zone_name, curr_turn = drone.path[i]
                    next_zone_name, next_turn = drone.path[i + 1]
                    if curr_turn <= t_current < next_turn:
                        t_frac = (t_current - curr_turn) / (
                            next_turn - curr_turn)
                        t_smooth = t_frac * t_frac * (3.0 - 2.0 * t_frac)
                        z1 = self.network.zones[curr_zone_name]
                        z2 = self.network.zones[next_zone_name]
                        start_x, start_y = self._get_pixel_coords(
                            z1.x, z1.y)
                        end_x, end_y = self._get_pixel_coords(z2.x, z2.y)
                        px_f = start_x + (end_x - start_x) * t_smooth
                        py_f = start_y + (end_y - start_y) * t_smooth
                        dist_start = math.hypot(
                            px_f - start_x, py_f - start_y)
                        dist_end = math.hypot(end_x - px_f, end_y - py_f)
                        transit = (curr_zone_name != next_zone_name) and \
                            (dist_start > 5) and (dist_end > 5)
                        px, py = int(px_f), int(py_f)
                        break

            if transit:
                self.active_drones += 1

            coord = (int(px), int(py))
            if coord not in drone_groups:
                drone_groups[coord] = []
            drone_groups[coord].append(drone)
            drone_transits[coord] = transit

        for coord, d_list in drone_groups.items():
            self._draw_drone_marker(
                coord[0], coord[1], d_list, drone_transits[coord])

    def _draw_hud(self) -> None:
        """
        Render the analytics panel and keyboard controls at the bottom of the
        visualizer window.
        """
        panel_rect = pygame.Rect(
            0, self.height - self.panel_height, self.width, self.panel_height)
        pygame.draw.rect(self.screen, (20, 10, 10), panel_rect)
        pygame.draw.line(self.screen, (100, 100, 100),
                         (0, self.height - self.panel_height),
                         (self.width, self.height - self.panel_height), 2)

        metrics = [
            ("Total Drones:", str(self.total_drones)),
            ("Active Drones:", str(getattr(self, 'active_drones', 0))),
            ("Avg Turns per drone:", f"{self.avg_turns:.1f}"),
            ("Total Cost:", f"{self.total_cost}")
        ]

        start_x = 40
        start_y = self.height - self.panel_height + 40

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
            ("[ESC]", "Quit")
        ]

        ctrl_x = self.width - 320
        for i, (key, desc) in enumerate(controls):
            key_surf = self.hud_font.render(key, True, Colors.YELLOW.value)
            desc_surf = self.hud_font.render(desc, True, Colors.WHITE.value)

            y_pos = start_y + (i * 35)
            self.screen.blit(key_surf, (ctrl_x, y_pos))
            self.screen.blit(desc_surf, (ctrl_x + 180, y_pos))
