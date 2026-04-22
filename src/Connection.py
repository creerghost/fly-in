class Connection:
    def __init__(self, name1: str, name2: str, max_link_capacity: int = 1):
        self.name1 = name1
        self.name2 = name2
        self.max_capacity = max_link_capacity

        self.current_drones: int = 0