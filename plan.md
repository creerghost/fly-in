# OOP Pro Max — Advanced Refactoring Plan

Full review of the codebase against OOP principles (Encapsulation, Inheritance, Polymorphism, Abstraction) with concrete improvements using every advanced Python technique that fits.

## Current State Assessment

The project already has a solid foundation: interfaces via ABC, Template Method pattern in `AStarAlgorithm`, Dependency Injection in `Application`, and clean package separation. The improvements below push every remaining seam toward proper OOP.

---

## Proposed Changes

### 1. Models — Encapsulation & Type Safety

#### [MODIFY] [drone.py](file:///home/vlnikola/fly-in/src/models/drone.py)

**Problem:** `Drone` is a raw class with fully public mutable state — `status` is a bare string (`"waiting"/"in_flight"/"finished"`), `path`/`draw_pos`/`current_location` are freely mutated from outside. No encapsulation at all.

**Changes:**

- Convert `status` from raw strings to a `DroneStatus(StrEnum)` — type safety + eliminates magic string comparisons scattered across `engine.py` and `renderer.py`
- Use `@dataclass(slots=True)` for memory efficiency and `__slots__` enforcement
- Make rendering-specific fields (`draw_pos`, `prev_pos`, `next_pos`, `animation_ready`) private with `_` prefix — they are renderer internals, not part of the drone's domain identity

#### [MODIFY] [zone.py](file:///home/vlnikola/fly-in/src/models/zone.py)

**Problem:** `zone_type` is compared as string literals (`"blocked"`, `"normal"`, etc.) throughout `cooperative_a_star.py`, `a_star_algorithm.py`, and `renderer.py` even though `ZoneType(StrEnum)` already exists.

**Changes:**

- Replace all `zone.zone_type == "blocked"` with `zone.zone_type == ZoneType.BLOCKED` across the codebase — use the enum properly
- Add a `@property` `is_traversable` to `Zone` to encapsulate the "blocked" check: `return self.zone_type != ZoneType.BLOCKED`
- Add `@property` `movement_cost` and `transit_time` to `Zone` that return the step cost and turn duration for each zone type — eliminates the repeated if/elif chains in both `a_star_algorithm.py` and `cooperative_a_star.py`

#### [MODIFY] [connection.py](file:///home/vlnikola/fly-in/src/models/connection.py)

**Problem:** `current_drones` field exists but is never used anywhere. Dead state.

**Changes:**

- Remove unused `current_drones` field (same for `Zone.current_drones`)

---

### 2. Algorithm — Encapsulation & Eliminating Code Duplication

#### [MODIFY] [a_star_algorithm.py](file:///home/vlnikola/fly-in/src/algorithm/mapf_a_star/a_star_algorithm.py)

**Problem:** The `generate_valid_neighbors` method contains a step-cost/turn-duration if/elif chain that duplicates logic. The `TemporalState` dataclass is in the algorithm file rather than in models.

**Changes:**

- Replace the if/elif chain with `Zone.movement_cost` and `Zone.transit_time` properties (from the Zone changes above)
- Move `TemporalState` to its own file `src/models/temporal_state.py` — it is a pure data structure, not algorithm logic
- Use `__slots__` on `TemporalState` for performance (it creates many instances during search)

#### [MODIFY] [cooperative_a_star.py](file:///home/vlnikola/fly-in/src/algorithm/mapf_a_star/cooperative_a_star.py)

**Problem:** Same duplicated step-cost/turn-duration if/elif chain as the parent class.

**Changes:**

- Replace if/elif chain with `Zone.movement_cost` and `Zone.transit_time` properties
- Use `ZoneType` enum comparisons instead of string literals

#### [MODIFY] [collision_manager.py](file:///home/vlnikola/fly-in/src/algorithm/mapf_a_star/collision_manager.py)

**Problem:** Indentation is inconsistent inside `register_path` — comments at loop-body level look like they're outside the loop. No encapsulation of the link-key normalization logic (duplicated between `is_link_available` and `register_path`).

**Changes:**

- Extract `_normalize_link(zone1, zone2) -> Tuple[str, str]` as a `@staticmethod` — DRY principle, used in both `is_link_available` and `register_path`
- Fix indentation inside `register_path`
- Use `collections.defaultdict(int)` instead of manual `.get(..., 0)` pattern — idiomatic Python, removes boilerplate

---

### 3. Engine — Single Responsibility & Encapsulation

#### [MODIFY] [engine.py](file:///home/vlnikola/fly-in/src/engine.py)

**Problem:** The `run()` method is 60 lines doing two completely different things: (1) planning routes, (2) running a turn-by-turn console simulation with output formatting. The console simulation loop has complex drone-location-resolution logic that is duplicated in `renderer.py`'s `_get_loc`. Uses `assert` for validation (crashes silently in optimized mode). Uses raw `range(len(...))` iteration.

**Changes:**

- Replace `assert` statements with proper `ValueError` raises — `assert` is stripped in `-O` mode
- Use `enumerate` and direct iteration instead of `range(len(drone.path))`
- Use `DroneStatus` enum instead of string assignments (`drone.status = "finished"`)
- Extract the drone-location-at-turn logic into a `@staticmethod` method on `Drone` or a utility — currently duplicated between `engine.py` and `renderer.py`

---

### 4. Renderer — Reducing God-Class Smell

#### [MODIFY] [renderer.py](file:///home/vlnikola/fly-in/src/renderer/renderer.py)

**Problem:** `Renderer` is a 430-line class doing everything: window management, input handling, rendering connections/zones/drones/HUD, drone interpolation math, and console output. Uses `getattr(self, 'active_drones', 0)` which is a code smell — the attribute should always exist.

**Changes:**

- Use `ZoneType` enum comparisons instead of string literals in cost calculation and zone label rendering
- Use `Zone.movement_cost` property to eliminate the if/elif chain in `run()` for cost calculation
- Initialize `self.active_drones = 0` in `__init__` — remove the `getattr` hack
- Replace `range(len(drone.path))` with `enumerate` / `zip` patterns

---

### 5. Application — Proper Exception Handling

#### [MODIFY] [application.py](file:///home/vlnikola/fly-in/src/app/application.py)

**Problem:** The `args` variable is referenced in `except` blocks but may not be defined if parsing failed. The `# type: ignore` comments suppress real type mismatches. Catches `Exception` (too broad).

**Changes:**

- Move `args` initialization before the `try` block or use a flag to track visualization state
- Keep `# type: ignore` — this is a Pydantic dict→model coercion pattern that mypy can't follow

---

### 6. New Files

#### [NEW] [temporal_state.py](file:///home/vlnikola/fly-in/src/models/temporal_state.py)

Move `TemporalState` dataclass from `a_star_algorithm.py` to models — it is a pure data object.

---

## Summary of OOP Techniques Applied

| Technique                                 | Where                                                        |
| ----------------------------------------- | ------------------------------------------------------------ |
| **StrEnum** for type safety               | `DroneStatus`, `ZoneType` usage enforcement                  |
| **@property** for encapsulation           | `Zone.is_traversable`, `Zone.movement_cost`, `Zone.transit_time` |
| **@dataclass(slots=True)**                | `Drone`, `TemporalState`                                     |
| **@staticmethod**                         | `CollisionManager._normalize_link`                           |
| **defaultdict**                           | `CollisionManager` schedules                                 |
| **Template Method** (already exists)      | `AStarAlgorithm.find_routes`                                 |
| **Dependency Injection** (already exists) | `Engine(network, pathfinder)`                                |
| **Enum over strings**                     | All zone_type and status comparisons                         |
| **DRY / Extract Method**                  | Link normalization, movement cost logic, location resolution |
| **Private convention `_`**                | Renderer-specific drone fields                               |

---

## Open Questions

> [!IMPORTANT]
> `Zone.current_drones` and `Connection.current_drones` are never read or written anywhere in the codebase. Should they be removed, or are they planned for future use?

> [!IMPORTANT]
> The `Drone` class currently mixes domain state (`id`, `path`, `status`, `current_location`) with rendering state (`draw_pos`, `prev_pos`, `next_pos`, `animation_ready`). An alternative to `_` prefixing would be to split into `Drone` (domain) and `DroneRenderState` (renderer). Preference?

---

## Verification Plan

### Automated Tests

```bash
make run file=maps/medium/01_dead_end_trap.txt
make lint-strict
```

### Manual Verification

- Visual renderer still works with `--visual` flag
- Console output matches previous behavior