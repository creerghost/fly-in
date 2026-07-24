from pydantic import BaseModel, ConfigDict, Field


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
