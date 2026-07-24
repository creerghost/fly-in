from typing import List, Dict, Tuple, Self, Set, Any
from pydantic import BaseModel, Field, model_validator
from .zone import Zone
from .connection import Connection


class Network(BaseModel):
    """
    Top-level configuration model that validates the entire
    network topology including zones and their connections.
    Builds searchable adjacency lists and graph structures for pathfinding.
    """
    nb_drones: int = Field(gt=0)
    start_hub: Zone
    end_hub: Zone
    hubs: List[Zone] | None = Field(default=None)
    connections: List[Connection] = Field(..., min_length=1)

    zones: Dict[str, Zone] = Field(default_factory=dict, init=False)
    neighboring_zones: Dict[str, List[Tuple[Zone, Connection]]] = Field(
        default_factory=dict, init=False
    )

    @model_validator(mode="after")
    def check_duplicate_zones(self) -> Self:
        """
        Validate that all zone names and coordinates are strictly unique.
        """
        zones: List[Zone] = [self.start_hub, self.end_hub]
        if self.hubs:
            zones.extend(self.hubs)
        seen_names: Set[str] = set()
        seen_zones: Set[Tuple[int, int]] = set()
        for zone in zones:
            if zone.name in seen_names:
                raise ValueError("Zone name already exists")
            seen_names.add(zone.name)
            if (zone.x, zone.y) in seen_zones:
                raise ValueError("Zone coordinates already exist")
            seen_zones.add((zone.x, zone.y))
        return self

    @model_validator(mode="after")
    def check_connections(self) -> Self:
        """
        Validate that all connections reference valid existing zones
        and that no duplicate connections exist.
        """
        zones: List[str] = [self.start_hub.name, self.end_hub.name]
        if self.hubs:
            zones.extend([h.name for h in self.hubs])
        seen_cons: Set[Tuple[str, str]] = set()
        for con in self.connections:
            s = sorted((con.name1, con.name2))
            pair: Tuple[str, str] = (s[0], s[1])
            if pair in seen_cons:
                raise ValueError(f"Connection already exists: "
                                 f"{con.name1}-{con.name2}")
            seen_cons.add(pair)
            if con.name1 not in zones or con.name2 not in zones:
                raise ValueError(f"Connection to non-existent zone: "
                                 f"{con.name1}-{con.name2}")
            if con.name1 == con.name2:
                raise ValueError(f"Connection to same zone: "
                                 f"{con.name1}-{con.name2}")
        return self

    def model_post_init(self, __context: Any) -> None:
        """
        Extract Zone and Connection objects from the validated configuration
        and store them for quick lookup. Build adjacency lists.
        """
        self.zones[self.start_hub.name] = self.start_hub
        if self.hubs:
            for hub in self.hubs:
                self.zones[hub.name] = hub
        self.zones[self.end_hub.name] = self.end_hub

        for zone_name in self.zones:
            self.neighboring_zones[zone_name] = []

        for con in self.connections:
            self.neighboring_zones[con.name1].append(
                (self.zones[con.name2], con))
            self.neighboring_zones[con.name2].append(
                (self.zones[con.name1], con))
