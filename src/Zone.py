class Zone:
    def __init__(self, name: str, x: int, y: int,
                 zone_type: str = "normal",
                 color: str | None = None,
                 max_drones: int = 1):
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones

        self.current_drones: int = 0

    def __repr__(self) -> str:
        return (f"zone name: {self.name}")
                # f"x: {self.x}, y: {self.y}, "
                # f"zone type: {self.zone_type}, "
                # f"color: {self.color}, "
                # f"max_drones: {self.max_drones}")