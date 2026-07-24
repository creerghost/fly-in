from pydantic import BaseModel, ConfigDict, model_validator, Field
from typing import Self
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
