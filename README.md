*This project has been created as part of the 42 curriculum by vlnikola.*

# Fly-in

## Description

Fly-in is a Python simulation of drones moving through a graph of zones and connections while respecting turn-based movement, zone occupancy, and connection capacity rules.

The project includes:

- a parser for the custom map format,
- a network model that converts parsed data into zones and connections,
- a space-time pathfinding strategy that plans routes for multiple drones,
- a simulation engine that prints each turn of movement,
- an optional live visualizer built with Pygame.

The main goal is to route every drone from the start hub to the end hub in as few turns as possible while avoiding collisions and respecting all capacity constraints.

## Instructions

### Requirements

- make
- mypy & flake8
- Python >= 3.13.1
- `pygame` >= 2.0.0

### Installation

```bash
make install
```

This creates a local virtual environment and installs the project dependencies from `requirements.txt`.

### Run

The `make run` command is configured to automatically generate a comprehensive temporary test map in the background. This map covers all possible zone types, colors, and capacities, and is instantly cleaned up without leaving any trace after the simulation ends.

```bash
make run
```

You can also override the default map or simulation arguments by passing flags to `make`:
```bash
# Run a specific map
make run FILE=maps/hard/02_capacity_hell.txt

# Run with custom arguments (e.g., visualizer enabled, 2.0x playback speed)
make run ARGS="--visual --speed=2.0"

# Override both
make run FILE=maps/hard/02_capacity_hell.txt ARGS="--visual"
```

> [!TIP]
> When running with the visualizer, you can pause and resume the simulation at any time by pressing the **Space** bar.

Or run the simulator manually with specific maps:

```bash
python3 fly_in.py maps/easy/01_linear_path.txt
python3 fly_in.py maps/medium/03_priority_puzzle.txt --visual
python3 fly_in.py maps/hard/02_capacity_hell.txt --visual --speed 2.0
```

### Map format

The parser expects a text file with:

- `nb_drones: <positive_integer>` on the first meaningful line,
- exactly one `start_hub:` entry,
- exactly one `end_hub:` entry,
- any number of `hub:` entries,
- `connection:` entries between previously defined zones.

Supported zone metadata includes:

- `zone=normal|blocked|restricted|priority`,
- `color=<name>`,
- `max_drones=<positive_integer>`.

Supported connection metadata includes:

- `max_link_capacity=<positive_integer>`.

Example:

```text
nb_drones: 4
start_hub: start 0 0 [zone=normal color=green max_drones=4]
end_hub: goal 6 0 [zone=normal color=gold]
hub: a 2 0 [zone=priority color=cyan]
hub: b 4 0 [zone=restricted color=purple]
connection: start-a [max_link_capacity=2]
connection: a-b [max_link_capacity=1]
connection: b-goal [max_link_capacity=1]
```

**Parser Validation Constraints:**
- Exactly one `start_hub` and `end_hub` must be present.
- Zone names cannot contain dashes (`-`), as dashes are reserved for string parsing and connection delimiting.
- Duplicate zone names or connections are strictly rejected.
- Negative capacities or drone counts are rejected.

## Algorithm And Implementation Strategy

The simulator uses a staged approach:

1. The parser reads and validates the input file.
2. The `Network` class turns the parsed dictionaries into `Zone` and `Connection` objects and builds adjacency lists.
3. The `Engine` creates all drones, then plans a route for each drone before the turn-by-turn simulation begins.
4. The pathfinder runs a space-time A* search with a reservation table.

### Pathfinding approach: Cooperative Space-Time A*

The core problem is Multi-Agent Pathfinding (MAPF). To solve this efficiently without the exponential overhead of joint-state searching, the project uses a **Cooperative Space-Time A*** algorithm.

Instead of searching in a standard 2D spatial graph, the algorithm searches in a **3D space-time graph** where the dimensions are `(Zone, Turn)`. 

1. **Sequential Planning**: Drones are routed one by one. The path found for the current drone is fixed in time and space.
2. **Reservation Table**: Once a drone's path is found, it "reserves" the zones and connections it uses at specific turns.
3. **Space-Time A* Search**: When the next drone plans its route, it runs standard A*, but its movement is constrained by the reservation table. If moving to `Zone B` at `Turn T` exceeds the zone's capacity, that space-time node is treated as an obstacle.
4. **Waiting**: Because time always advances, a drone can "wait" at its current zone (moving from `(Zone A, Turn T)` to `(Zone A, Turn T+1)`), provided it doesn't violate the zone's capacity. This is critical for letting earlier drones pass through chokepoints.

The search state explicitly includes:

- the current zone,
- the current turn (which acts as the "depth" in the space-time graph),
- the accumulated path cost,
- a parent pointer used to rebuild the route.

The reservation table acts as a fast 3D collision map, storing:

- zone occupancy counts by `(zone, turn)`, checked against `max_drones`,
- link usage counts by `(connection, turn)`, checked against `max_link_capacity`,
- edge-swap checks to prevent drones from crossing the same connection in opposite directions simultaneously.

This strategy guarantees collision-free routing, makes conflict checks `O(1)`, and keeps the simulation deterministic.

### Movement rules and Heuristics

**A* Search Theory:**
A* is a best-first search algorithm that finds the least-cost path by maintaining a priority queue based on the cost function `f(n) = g(n) + h(n)`:
- `g(n)` represents the exact accumulated cost from the start node to the current node `n`.
- `h(n)` represents the heuristic function, an estimated cost from node `n` to the goal.

To guarantee that A* finds the mathematically optimal path, the heuristic must be **admissible**. An admissible heuristic never overestimates the true cost to reach the goal. If it overestimates, A* might settle for a sub-optimal path. If it underestimates (or is `0`, effectively turning A* into Dijkstra's Algorithm), it will explore unnecessary nodes, heavily impacting performance.

**Space-Time Implementation:**
In this project, the traditional A* algorithm is adapted into a **Cooperative Space-Time A***. The search state (`TemporalState`) expands across both physical locations and time (turns). Instead of just generating spatial neighbors, the algorithm generates space-time neighbors, checking a global `ReservationTable`. If a `(zone, turn)` or `(link, turn)` exceeds capacity (`max_drones` or `max_link_capacity`), it is treated as a dynamic obstacle. The search also allows "wait" actions, meaning a drone can physically stay still to avoid a collision while time advances.

### Generating Space-Time Neighbors

The core engine of this adaptation is the `generate_valid_neighbors` function. In standard pathfinding, a "neighbor" is just a physically connected node. In **Space-Time pathfinding**, a "neighbor" is a combination of **Where you are going** and **When you will be there**. 

This function evaluates valid moves by breaking them down into two categories:

1. **The "Wait" Action:** Sometimes the fastest path is currently blocked by another drone. Instead of moving away, the drone can wait. The function checks the `ReservationTable` to see if the current zone will still have capacity (i.e., not exceeding `max_drones`) during the `next_turn`. If it does, it generates a "Wait State" where the physical location remains the same, but the time (`turn`) advances by 1 and the cost increases by 1.0.

2. **Moving to Adjacent Zones:** The algorithm loops through every physically connected zone and evaluates it as a potential move:
   - **Zone Types & Costs:** It checks the `zone_type` to calculate the arrival time (`next_turn`) and the A* penalty (`step_cost`). Normal zones take 1 turn (cost 1.0), Priority zones take 1 turn (cost 0.8), and Restricted zones take 2 entire turns to cross (cost 2.0). Blocked zones are completely pruned.
   - **Collision Prevention:** Before committing, the `ReservationTable` must confirm that the **link** connecting the two zones is not fully occupied during transit, and that the **destination zone** has an open slot exactly on the turn of arrival.
   - **State Creation:** If the path is clear, it calculates the new `g_cost` (total time elapsed) and `h_cost` (estimated time to goal), bundling it into a new `TemporalState` for the priority queue.


The search algorithm must balance finding the shortest path with obeying strict map constraints. It uses a heuristic function to guide the search efficiently.

**Manhattan Distance Heuristic:**
Manhattan Distance (or Taxicab geometry) is the distance between two points measured along axes at right angles. Unlike Euclidean distance (the "as the crow flies" straight line), Manhattan distance calculates the sum of the absolute differences of their Cartesian coordinates. On a grid-like map where diagonal movement is impossible, Manhattan distance provides a highly accurate estimate of the minimum steps required.

**Code-Specific Detail (The Final Formula):** 
Because passing through a `priority` zone costs `0.8` (instead of `1.0`), an unscaled Manhattan distance could technically overestimate the true cost to the goal if a path uses priority zones, making the heuristic inadmissible. To guarantee A* always finds the mathematically optimal path without violating admissibility, the raw Manhattan distance is artificially scaled down by a factor of `0.25`.

The **FINAL formula** calculated inside `_calculate_h` is:
```python
h(n) = ( |x_current - x_goal| + |y_current - y_goal| ) * 0.25
```
- **Normal zones** cost 1.0 turn to traverse.
- **Priority zones** cost 0.8 turns (with a structural +1 turn advancement). This lower accumulation cost naturally pulls the A* search toward these zones when breaking ties.
- **Restricted zones** cost 2 turns to cross. In the space-time graph, this is represented as an in-transit state across turns (e.g., reserving the zone for `Turn T` and `Turn T+1`).
- **Blocked zones** are treated as static obstacles and are completely pruned from the search tree.
- **Wait actions** (costing 1 turn) are injected as valid neighbors in the A* expansion, allowing a drone to stall at its current zone if the path ahead is blocked, provided its current zone still has capacity at `Turn T+1`.

### Priority Queue (heapq)

The algorithm leverages Python's `heapq` module to maintain an efficient priority queue (min-heap) for the A* `open_set`.
- **Always Picking the Best Path:** A* must constantly evaluate the most promising path first—the state with the lowest total estimated cost (`f_cost`).
- **Performance:** Searching a standard list to find the minimum cost node takes **O(N)** time, which would bottleneck the algorithm on large maps. `heapq` automatically keeps the best node at the front. `heappop()` grabs the lowest `f_cost` instantly, and `heappush()` sorts new nodes in **O(log N)** time, keeping the algorithm extremely fast.
- **Dataclass Integration:** The `TemporalState` dataclass explicitly places `f_cost` as its first attribute and uses `@dataclass(order=True)`. This allows `heapq` to automatically compare and mathematically organize the states inside the heap without any custom sorting functions.

### Complexity

Let `S` be the number of explored space-time states for a drone.

- Route planning is approximately `O(S log S)` because the implementation uses a heap-based A* open set.
- Neighbor generation is proportional to the degree of the current zone.
- Reservation lookups are `O(1)` on average thanks to dictionaries.

For the full simulation, the cost scales with the number of drones because a route is planned for each drone.

### Caching and recalculation

Routes are not globally cached and reused between drones. Instead, each drone gets one planned path, and the reservation table caches the occupied turns and links for the already planned drones. This keeps the implementation simple and avoids invalidating a large shared cache when later drones change the available space-time slots.

### Memory usage

Memory use is mainly driven by:

- the parsed graph structure,
- the reservation table,
- the open set and visited states during A*,
- one stored path per drone.

In practice, the reservation table grows with the number of scheduled zone-turn and link-turn usages, not with every possible turn in the map.

## Simulation Output

The engine prints one line per turn when drones move.

Example output:

```text
D1-a D2-b
D1-a-b D2-goal
D1-b
D1-goal
```

**In-Transit Output:** Notice the `D1-a-b` output. When a drone travels through a `restricted` zone (which takes 2 turns), it is considered "mid-transit." The engine dynamically formats its location as `current_zone-next_zone` to visually indicate that it is crossing between two points over multiple turns.

When the visualizer is enabled, the same turn log is still printed in the terminal.

## Visual Representation

The optional visualizer opens a live Pygame window that brings the simulation to life. 

### Key Features and Renderer Logic

- **Connection Overlap Prevention:** To avoid drawing parallel connections perfectly on top of each other, the renderer mathematically offsets nodes using a "chessboard-like" coordinate shift (`px += 30 if y % 2 == 0 else -10`). This guarantees all edges remain visible.
- **Node Data & Identifiers:** 
  - The exact `x,y` coordinates of each node are printed directly underneath it.
  - A descriptive letter (`Start`, `End`, `R` for restricted, `B` for blocked, `P` for priority) is stamped in the absolute center of the node circle for quick identification.
- **Animated Drone Motion:** The renderer now interpolates drone positions between turns at 60 FPS, so movement looks smooth instead of jumping from one node to the next.
- **Drone State Visualization:**
  - **In Node:** When a drone is resting or acting inside a zone, its marker is drawn hovering slightly above the node (`py - 25`), wrapped in a bright red rectangle.
  - **In Transit:** When a drone is moving between two zones, its position is animated along the segment and rendered in gray while the move is in progress.
- **Drone Graphics:** Each marker uses a custom loaded image bitmap (`imgs/drone.bmp`), scaled to 45x45 pixels and layered underneath dynamically grouped text labels (e.g. `2D` if two drones occupy the same spot).
- **Interactive Scrubbing & Playback:** You can pause the simulation at any time using `Space`, physically scrub time forward and backward using the `Left` and `Right` arrow keys, or instantly reset back to the beginning using the `R` key.
- **Heads-Up Display (HUD):** A dedicated panel at the bottom of the screen displays real-time analytics, including the total number of drones, average turns per drone, total path cost, and exactly how many drones are actively moving at the current moment in time.
- **Responsive Window Loop:** The visualizer handles interaction events on every frame so the animation stays completely smooth while playing at custom speeds configured by `--speed`.

### Advantages

This level of visual feedback improves understanding in three main ways:
- It makes congestion visible immediately when several drones compete for the same area.
- It shows where restricted zones delay movement and how transit spans multiple turns through the gray midpoint markers.
- It makes it easier to visually explain why a pathing algorithm's solution is valid or why a specific bottleneck appears.

The animated renderer also makes short moves easier to follow, since each drone eases into and out of a turn instead of snapping instantly to the next location.

The visualizer also supports pause and resume with the `Space` bar, resetting with `R`, and quitting with `Escape` or the window close button.

### Disadvantages

- **Static Window Scaling:** The visualizer's window dimensions are calculated directly from the map's coordinate extremes using a fixed tile size. As a result, very large maps or maps with widely spaced nodes (such as the Challenger maps) can generate a window that exceeds standard screen resolutions. Since there is no dynamic zooming, panning, or responsive scaling implemented, parts of these massive grids may overflow off-screen and become impossible to view completely.

## Resources

- Python documentation: https://docs.python.org/3/
- `heapq` documentation: https://www.geeksforgeeks.org/python/heap-queue-or-heapq-in-python/
- Pygame documentation: https://www.pygame.org/docs/
- A* search overview: https://www.datacamp.com/tutorial/a-star-algorithm
- Cooperative A*:
`David Silver. 2005. Cooperative pathfinding. In Proceedings of the First AAAI Conference on Artificial Intelligence and Interactive Digital Entertainment (AIIDE'05). AAAI Press, 117–122.
`
- 42 project subject and map files included in this repository

### AI Usage

AI assistance was utilized during the development of this project for the following tasks:
- **Algorithm Comprehension:** AI helped me better understand the algorithm, especially the space-time pathfinding part.
- **Debugging and Refactoring:** Assisting in identifying edge cases within the space-time A* pathfinding implementation.
- **Documentation & Testing:** Helping structure and proofread this `README.md` to ensure it meets all curriculum requirements, and generating PEP 257 compliant docstrings for classes and methods across the codebase.

The core logical design, algorithmic choices, and constraints enforcement were driven by the developer, with AI acting as a supportive peer-programming tool.

## Useful Commands

```bash
make debug # runs the simulator with Python's pdb debugger
make lint # flake8 and mypy type hint checking
make lint-strict # strict version of mypy checker
make clean # cleans the python caches and removes the virtual environment
```

These are helpful for checking the codebase and removing generated Python cache files.