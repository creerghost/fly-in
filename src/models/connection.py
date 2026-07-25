"""Connection models representing edges in the drone network."""

from pydantic import BaseModel, ConfigDict, Field


class Connection(BaseModel):
    """
    Represent a navigable path or link between two zones.

    Contains a specific traffic capacity.
    """

    model_config = ConfigDict(extra='forbid')

    name1: str
    name2: str
    max_link_capacity: int = Field(default=1, gt=0)
