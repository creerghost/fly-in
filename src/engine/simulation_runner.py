from typing import List
from ..models import Drone
from ..models.drone import DroneStatus
from ..interfaces import Runnable


class SimulationRunner(Runnable):
    """
    Executes a turn-by-turn console simulation.
    Updates drone status and location, printing movements to stdout.
    """
    def __init__(self, drones: List[Drone]) -> None:
        self.drones = drones

    def run(self) -> None:
        turn = 1

        while True:
            all_finished = True
            turn_output = []

            for drone in self.drones:
                prev_location = drone.current_location

                if turn > drone.path[-1][1]:
                    continue

                drone.current_location = drone.location_at_turn(turn)

                if turn >= drone.path[-1][1]:
                    drone.status = DroneStatus.FINISHED
                else:
                    drone.status = DroneStatus.IN_FLIGHT
                    all_finished = False

                if drone.current_location != prev_location:
                    turn_output.append(f"{drone.id}-{drone.current_location}")

            if turn_output:
                print(" ".join(turn_output))

            if all_finished:
                break
            turn += 1
