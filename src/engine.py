from src.drone import Drone
from src.algorithm import ReservationTable, SpaceTimePathfinder
from src.network import Network


class Engine:
    def __init__(self, network: Network) -> None:
        self.network = network
        self.reservations = ReservationTable()
        self.pathfinder = SpaceTimePathfinder(network, self.reservations)
        self.drones: list[Drone] = []

    def _init_drones(self) -> None:
        assert self.network.parser.start_hub is not None
        for i in range(self.network.parser.nb_drones):
            drone = Drone(f"D{i}", self.network.parser.start_hub["name"])
            self.drones.append(drone)

    def _plan_routes(self) -> None:
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
        self._init_drones()
        self._plan_routes()
        turn = 1

        while True:
            all_finished = True
            turn_output = []

            for drone in self.drones:
                if turn >= drone.path[-1][1]:
                    drone.current_location = drone.path[-1][0]
                    drone.status = "finished"
                    turn_output.append(f"{drone.id}-{drone.current_location}")
                    continue

                all_finished = False
                drone.status = "in_flight"

                # Find where the drone is at the turn
                for i in range(len(drone.path) - 1):
                    curr_zone_name, curr_turn = drone.path[i]
                    next_zone_name, next_turn = drone.path[i + 1]

                    if turn == next_turn:
                        drone.current_location = next_zone_name
                        turn_output.append(f"{drone.id}-{next_zone_name}")
                        break
                    elif curr_turn < turn < next_turn:
                        # The drone is mid-transit (taking a multi-turn action)
                        if curr_zone_name == next_zone_name:
                            drone.current_location = curr_zone_name
                            turn_output.append(f"{drone.id}-{curr_zone_name}")
                        else:
                            drone.current_location = f"{curr_zone_name}-" \
                                f"{next_zone_name}"
                            turn_output.append(f"{drone.id}-{curr_zone_name}"
                                               f"-{next_zone_name}")
                        break

            if all_finished:
                break

            print(" ".join(turn_output))
            turn += 1
