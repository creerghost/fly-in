from typing import List, Dict, Tuple, Self, Set
from src.parser import Parser
from pydantic import BaseModel, Field, model_validator, ConfigDict
from enum import StrEnum


class ZoneType(StrEnum):
    """
    Enumeration of valid zone types for the drone network.
    """
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Zone(BaseModel):
    """
    Represents a specific geographic location in the network
    that drones can travel between.
    """
    model_config = ConfigDict(extra='forbid', populate_by_name=True)

    name: str
    x: int
    y: int
    zone_type: ZoneType = Field(default=ZoneType.NORMAL, alias="zone")
    color: str | None = Field(default=None)
    max_drones: int = Field(default=1, gt=0)
    current_drones: int = Field(default=0)

    @model_validator(mode="after")
    def check_zone(self) -> Self:
        """
        Ensure the zone name does not contain any dashes,
        as they are reserved for connection names.
        """
        if "-" in self.name:
            raise ValueError("Zone name should not contain dashes: "
                             f"{self.name}")
        return self


class Connection(BaseModel):
    """
    Represents a navigable path or link between two zones
    with a specific traffic capacity.
    """
    model_config = ConfigDict(extra='forbid')

    name1: str
    name2: str
    max_link_capacity: int = Field(default=1, gt=0)
    current_drones: int = Field(default=0)


class NetworkConfig(BaseModel):
    """
    Top-level configuration model that validates the entire
    network topology including zones and their connections.
    """
    nb_drones: int = Field(gt=0)
    start_hub: Zone
    end_hub: Zone
    hubs: List[Zone] | None = Field(default=None)
    connections: List[Connection] = Field(..., min_length=1)

    @model_validator(mode="after")
    def check_dublicate_zones(self) -> Self:
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


class Network:
    """
    Topology manager. Uses the validated NetworkConfig to build
    searchable adjacency lists and graph structures for pathfinding.
    """
    def __init__(self, parser: Parser) -> None:
        """
        Initialize the Network by validating parser data via NetworkConfig,
        then populate internal zones and connections.
        """
        self.parser = parser
        self.config = NetworkConfig.model_validate({
            "nb_drones": parser.nb_drones,
            "start_hub": parser.start_hub,
            "end_hub": parser.end_hub,
            "hubs": parser.hubs,
            "connections": parser.connections
        })
        self.zones: Dict[str, Zone] = {}
        self.connections: List[Connection] = []
        self.neighboring_zones: Dict[str, List[Tuple[Zone, Connection]]] = {}
        self._assign_zones_and_connections()
        self._assign_neighboring_zones()

    def _assign_zones_and_connections(self) -> None:
        """
        Extract Zone and Connection objects from the validated configuration
        and store them for quick lookup.
        """
        self.zones[self.config.start_hub.name] = self.config.start_hub

        if self.config.hubs:
            for hub in self.config.hubs:
                self.zones[hub.name] = hub

        self.zones[self.config.end_hub.name] = self.config.end_hub

        for connection in self.config.connections:
            self.connections.append(connection)

    def _assign_neighboring_zones(self) -> None:
        """
        Build an adjacency list mapping each zone to its
        connected neighbors and their corresponding connection.
        """
        for zone_name in self.zones:
            self.neighboring_zones[zone_name] = []

        for con in self.connections:
            self.neighboring_zones[con.name1].append((self.zones[con.name2],
                                                      con))
            self.neighboring_zones[con.name2].append((self.zones[con.name1],
                                                      con))
