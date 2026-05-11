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
- Python 3.13.1
- `pygame` >= 2.0.0

### Installation

```bash
make install
```

This creates a local virtual environment and installs the project dependencies from `requirements.txt`.

### Run

```bash
make run
```

Or run the simulator directly:

```bash
python3 fly_in.py maps/easy/01_linear_path.txt
python3 fly_in.py maps/medium/03_priority_puzzle.txt --visual
python3 fly_in.py maps/hard/02_capacity_hell.txt --visual --delay 0.2
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

## Algorithm And Implementation Strategy

The simulator uses a staged approach:

1. The parser reads and validates the input file.
2. The `Network` class turns the parsed dictionaries into `Zone` and `Connection` objects and builds adjacency lists.
3. The `Engine` creates all drones, then plans a route for each drone before the turn-by-turn simulation begins.
4. The pathfinder runs a space-time A* search with a reservation table.

### Pathfinding approach

Each drone is routed independently, but later drones search against the reservations already taken by earlier drones. This is how the implementation prevents overlapping zone occupancy and link conflicts without recalculating the entire schedule from scratch on every turn.

The search state includes:

- the current zone,
- the current turn,
- the accumulated path cost,
- a parent pointer used to rebuild the route.

The reservation table stores:

- zone occupancy by `(zone, turn)`,
- link usage by `(connection, turn)`.

This makes conflict checks fast and keeps the simulation deterministic.

### Movement rules handled by the search

- Normal zones cost 1 turn.
- Priority zones also cost 1 turn, but they receive a lower heuristic cost so they are preferred by the search.
- Restricted zones cost 2 turns and are represented as in-transit states across turns.
- Blocked zones are ignored by the pathfinder.
- Wait actions are allowed when the current zone still has capacity.

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
D1-b D2-goal
D1-goal
```

When the visualizer is enabled, the same turn log is still printed in the terminal.

## Visual Representation

The optional visualizer opens a live Pygame window and displays:

- the full map geometry,
- colored zones based on metadata,
- labels for start, end, restricted, blocked, and priority zones,
- drone markers on zones,
- mid-transit drone markers for multi-turn movement,
- the current turn number.

This improves understanding in three ways:

- It makes congestion visible immediately when several drones compete for the same area.
- It shows where restricted zones delay movement and how transit spans multiple turns.
- It makes it easier to explain why a solution is valid or why a bottleneck appears.

The visualizer also supports pause and resume with the space bar, and quitting with Escape or the window close button.

## Resources

- Python documentation: https://docs.python.org/3/
- `heapq` documentation: https://docs.python.org/3/library/heapq.html
- Pygame documentation: https://www.pygame.org/docs/
- A* search overview: https://en.wikipedia.org/wiki/A*_search_algorithm
- 42 project subject and map files included in this repository

### AI Usage

tba

## Useful Commands

```bash
make lint # flake8 and mypy type hint checking
make lint-strict # strict version of mypy checker
make clean # cleans the python caches and removes the virtual environment
```

These are helpful for checking the codebase and removing generated Python cache files.