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
