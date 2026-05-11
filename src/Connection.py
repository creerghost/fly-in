class Connection:
    def __init__(self, name1: str, name2: str,
                 max_link_capacity: int = 1) -> None:
        """
        Initialize a Connection between two zones with a specified link
        capacity.
        """
        self.name1 = name1
        self.name2 = name2
        self.max_capacity = max_link_capacity

        self.current_drones: int = 0

    def __repr__(self) -> str:
        """
        Return a string representation of the Connection.
        """
        return f"connection name: {self.name1}-{self.name2}"
