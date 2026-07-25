from pydantic import BaseModel, ConfigDict, model_validator, Field
from typing import Optional
from typing_extensions import Self
from enum import Enum


class ZoneType(str, Enum):
    """
    Enumeration of valid zone types for the drone network.
    """
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"

    @property
    def display_label(self) -> Optional[str]:
        if self == ZoneType.RESTRICTED:
            return "R"
        elif self == ZoneType.BLOCKED:
            return "B"
        elif self == ZoneType.PRIORITY:
            return "P"
        return None


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

    @property
    def is_traversable(self) -> bool:
        return self.zone_type != ZoneType.BLOCKED

    @property
    def movement_cost(self) -> float:
        if self.zone_type == ZoneType.RESTRICTED:
            return 2.0
        elif self.zone_type == ZoneType.PRIORITY:
            return 0.8
        return 1.0

    @property
    def transit_time(self) -> int:
        if self.zone_type == ZoneType.RESTRICTED:
            return 2
        return 1
