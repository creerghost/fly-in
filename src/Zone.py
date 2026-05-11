class Zone:
    def __init__(self, name: str, x: int, y: int,
                 zone_type: str = "normal",
                 color: str | None = None,
                 max_drones: int = 1) -> None:
        """
        Initialize a Zone with coordinates, type, color, and capacity.
        """
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones

        self.current_drones: int = 0

    def __repr__(self) -> str:
        """
        Return a string representation of the Zone.
        """
        return (f"zone name: {self.name}")
