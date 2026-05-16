from src.drone import Drone
from src.algorithm import ReservationTable, SpaceTimePathfinder
from src.network import Network


class Engine:
    """
    Core simulation engine that handles drone lifecycle, routing,
    and turn-by-turn execution.
    """
    def __init__(self, network: Network, visualize: bool = False,
                 delay: float = 0.5) -> None:
        self.network = network
        self.reservations = ReservationTable()
        self.pathfinder = SpaceTimePathfinder(network, self.reservations)
        self.drones: list[Drone] = []
        self.visualize = visualize
        self.delay = delay
        if self.visualize:
            from src.renderer import Renderer
            self.renderer = Renderer(self.network, self.delay)

    def _init_drones(self) -> None:
        """
        Instantiate the drone objects based on network specifications.
        """
        assert self.network.parser.start_hub is not None
        for i in range(self.network.parser.nb_drones):
            drone = Drone(f"D{i}", self.network.parser.start_hub["name"])
            self.drones.append(drone)

    def _plan_routes(self) -> None:
        """
        Execute pathfinding for all drones and register their reserved paths.
        """
        assert self.network.parser.end_hub is not None
        for drone in self.drones:
            path = self.pathfinder.find_routes(
                drone.current_location,
                self.network.parser.end_hub["name"])
            if path is None:
                raise ValueError(f"No valid path found for drone {drone.id}")
            self.reservations.register_path(path)
            drone.path = path

    def run(self) -> None:
        """
        Run the main simulation loop turn-by-turn until all drones reach their
        destination.
        """
        self._init_drones()
        self._plan_routes()

        turn = 1

        if self.visualize:
            self.renderer.animate_turn(turn, self.drones, [])

        while True:
            all_finished = True
            turn_output = []

            for drone in self.drones:
                prev_location = drone.current_location

                if turn > drone.path[-1][1]:
                    continue

                if turn == drone.path[-1][1]:
                    drone.current_location = drone.path[-1][0]
                    drone.status = "finished"
                    if drone.current_location != prev_location:
                        turn_output.append(f"{drone.id}-"
                                           f"{drone.current_location}")
                    continue

                all_finished = False
                drone.status = "in_flight"

                # Find where the drone is at the turn
                for i in range(len(drone.path) - 1):
                    curr_zone_name, curr_turn = drone.path[i]
                    next_zone_name, next_turn = drone.path[i + 1]

                    if turn == next_turn:
                        drone.current_location = next_zone_name
                        if drone.current_location != prev_location:
                            turn_output.append(f"{drone.id}-{next_zone_name}")
                        break
                    elif curr_turn < turn < next_turn:
                        # The drone is mid-transit (taking a multi-turn action)
                        if curr_zone_name == next_zone_name:
                            drone.current_location = curr_zone_name
                        else:
                            drone.current_location = f"{curr_zone_name}-" \
                                f"{next_zone_name}"
                            if drone.current_location != prev_location:
                                turn_output.append(f"{drone.id}-"
                                                   f"{curr_zone_name}"
                                                   f"-{next_zone_name}")
                        break

            if turn_output:
                if self.visualize:
                    self.renderer.animate_turn(turn, self.drones, turn_output)
                else:
                    print(" ".join(turn_output))

            if all_finished:
                break
            turn += 1
