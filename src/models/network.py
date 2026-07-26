"""Network topology and graph representations."""

import sys
from typing import Any

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self

from .connection import Connection
from .zone import Zone


class Network(BaseModel):
    """
    Top-level configuration model that validates the entire network topology.

    Validates zones, connections, and builds searchable adjacency lists.
    """

    nb_drones: int = Field(gt=0)
    start_hub: Zone
    end_hub: Zone
    hubs: list[Zone] | None = Field(default=None)
    connections: list[Connection] = Field(..., min_length=1)

    zones: dict[str, Zone] = Field(default_factory=dict, init=False)
    neighboring_zones: dict[str, list[tuple[Zone, Connection]]] = Field(
        default_factory=dict, init=False
    )

    @model_validator(mode="after")
    def check_duplicate_zones(self) -> Self:
        """Validate that all zone names and coordinates are strictly unique."""
        zones: list[Zone] = [self.start_hub, self.end_hub]
        if self.hubs:
            zones.extend(self.hubs)
        seen_names: set[str] = set()
        seen_zones: set[tuple[int, int]] = set()
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
        Validate that all connections reference valid existing zones.

        Also checks that no duplicate connections exist.
        """
        zones: list[str] = [self.start_hub.name, self.end_hub.name]
        if self.hubs:
            zones.extend([h.name for h in self.hubs])
        seen_cons: set[tuple[str, str]] = set()
        for con in self.connections:
            s = sorted((con.name1, con.name2))
            pair: tuple[str, str] = (s[0], s[1])
            if pair in seen_cons:
                raise ValueError(
                    f"Connection already exists: {con.name1}-{con.name2}")
            seen_cons.add(pair)
            if con.name1 not in zones or con.name2 not in zones:
                raise ValueError(
                    f"Connection to non-existent zone: {con.name1}-{con.name2}"
                )
            if con.name1 == con.name2:
                raise ValueError(
                    f"Connection to same zone: {con.name1}-{con.name2}")
        return self

    def model_post_init(self, __context: Any) -> None:
        """
        Extract Zone and Connection objects from the validated configuration.

        Stores them for quick lookup and builds adjacency lists.
        """
        self.start_hub.max_drones = sys.maxsize
        self.end_hub.max_drones = sys.maxsize

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

    def __len__(self) -> int:
        """Return the number of zones in the network."""
        return len(self.zones)

    def __contains__(self, zone_name: str) -> bool:
        """Check if a zone exists in the network by name."""
        return zone_name in self.zones

    def __getitem__(self, zone_name: str) -> Zone:
        """Get a zone from the network by its name."""
        return self.zones[zone_name]

    def __str__(self) -> str:
        """Return a string representation of the network topology."""
        return (
            f"Network({len(self.zones)} zones, "
            f"{len(self.connections)} connections, "
            f"{self.nb_drones} drones)"
        )
