# Fly-in Implementation Plan

This project requires an efficient pathfinding simulation to move multiple drones through a network graph with node and edge capacities, time-delayed moves, and varying zone costs.

## User Review Required

> [!IMPORTANT]
> The pathfinding algorithm uses Prioritized Time-Space A*. This routes drones sequentially while avoiding collisions using a space-time reservation table. I would like to confirm this approach is agreeable as it offers a strong trade-off between performance and shortest turns.

> [!TIP]
> Since we cannot use `networkx` or graph libraries, we will build a custom graph dictionary linking zones and connections.

## Proposed Changes

---

### Core Data Structures & Models

#### [MODIFY] [Zone.py](file:///home/nikolaev/fly-in/src/Zone.py)
Expand `Zone` to handle current occupancy checking over space-time:
- Instead of just `current_drones`, it needs to be aware of the simulation engine, or we decouple spatial data from temporal data. We will keep `Zone` minimal and store temporal capacity in the Pathfinding Engine.
- Keep `Zone` as a static representation of a node.

#### [MODIFY] [Connection.py](file:///home/nikolaev/fly-in/src/Connection.py)
Expand `Connection` to serve as graph edges joining two zones. 
- Ensure `max_capacity` is easily accessible.
- We will link `Zone` objects after parsing.

#### [MODIFY] [drone.py](file:///home/nikolaev/fly-in/src/drone.py)
Create a `Drone` class:
- `id`: Unique identifier (e.g., `D1`, `D2`).
- `path`: List of tuples scheduled actions `(time, action, destination_or_None)`.
- `current_location`: Initially `start_hub`.

#### [MODIFY] [network.py](file:///home/nikolaev/fly-in/src/network.py)
Create a `Network` class to manage graph topology:
- Load parser data into `Network` mapping names to `Zone` and `Connection`.
- Function `get_neighbors(zone_name)` returns connected zones and the connecting edge.
- Centralize metadata parsing here.

---

### Pathfinding and Algorithm

#### [MODIFY] [algorithm.py](file:///home/nikolaev/fly-in/src/algorithm.py)
Create `TimeSpaceAStar` class for routing drones systematically.
- **Reservation Table:** Mappings of `(location, time) -> int` to track how much capacity is taken at particular time steps by already routed drones.
- **Cost calculation:**
  - `normal`, `blocked` (ignored), `restricted` (2 turns), `priority` (1 turn).
  - Priority zones will have a slightly lighter heuristic weight to prioritize them.
  - Multi-turn restricted moves will reserve both the edge at `t` and the destination at `t+1, t+2`.
- Plan each drone one by one (Prioritized Planning) or batch-based.
- Re-run planning iteratively if bottlenecked, but strict chronological prioritized planning should easily conquer < 60 turns for 15 drones due to low graph branching.

---

### Simulation Engine and Output

#### [NEW] [simulator.py](file:///home/nikolaev/fly-in/src/simulator.py)
Create a simulation loop engine that executes the planned paths:
- Takes the planned `path` of each drone and executes it turn-by-turn.
- Validate occupancy constraints per turn safely.
- Output string strings per turn following required output: `D<ID>-<zone>` or `D<ID>-<connection>` if in transit.

#### [NEW] [visualizer.py](file:///home/nikolaev/fly-in/src/visualizer.py)
Terminal-based Visualizer that reads network structure and drone positions each turn.
- Prints a textual summary, dynamically formatting zone text with the specified color.
- Prints Drone movements over turns visually by tracking mapping positions.

---

### Entrypoint

#### [MODIFY] [fly_in.py](file:///home/nikolaev/fly-in/fly_in.py)
Orchestrate the flow:
1. Parse using `Parser`.
2. Build network from parsed dicts using `Network`.
3. Feed into pathfinding `algorithm.py`.
4. Pass outputs to `simulator.py` to evaluate step-by-step logic.
5. Provide visual feedback optional logs.

## Open Questions

> [!WARNING]
> Regarding Visual Representation: Would you like a real-time ASCII plotting based on the X, Y coordinates of the Zones clearing the terminal each turn, or simply colored text logs per turn indicating movements?
> Regarding Prioritization rule `priority`: is it okay if we use A* path cost `0.8` instead of `1` internally for those, enforcing preference over `normal` while consuming exactly `1` simulation turn?

## Verification Plan

### Automated Tests
- Run simulation on `01_linear_path.txt` and ensure exactly <= 6 turns with valid capacity steps.
- Use mypy strictly: `mypy . --strict` to ensure complete type safety.
- Use `flake8` to detect styling deviations.

### Manual Verification
- Visual inspection of the printed drone movement to ensure they follow `D<ID>-<zone>` per turn accurately.
- Ensure restricted zones precisely block the connection for exactly 2 turns.
