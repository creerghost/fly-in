from typing import List, Dict, Any


class Parser:
    def __init__(self, filepath: str):
        self.filepath = filepath

        self.nb_drones: int = 0
        self.start_hub: Dict[str, Any] | None = None
        self.end_hub: Dict[str, Any] | None = None
        self.hubs: List[Dict[str, Any]] = []
        self.connections: List[Dict[str, Any]] = []

    def parse(self) -> None:
        try:
            with open(self.filepath, 'r') as f:
                for l_num, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                self._parse_line(line, l_num)
        except FileNotFoundError:
            raise FileNotFoundError(f"File '{self.filepath}' not found")

        self._validate()

    def _parse_line(self, line: str, line_num: int) -> None:
        if line.startswith("nb_drones"):
            drones = line.split(":")
            if len(drones) != 2 or not drones[1].strip().isdigit():
                raise ValueError(f"Line {line_num}: "
                                 f"Invalid nb_drones format")
            self.nb_drones = int(drones[1].strip())
        elif line.startswith("start_hub:"):
            self.start_hub = self.parse_zone_line(
                line.replace("start_hub:", "").strip())
        elif line.startswith("end_hub:"):
            self.end_hub = self.parse_zone_line(
                line.replace("end_hub:", "").strip())
        elif line.startswith("hub:"):
            self.hubs.append(self._parse_zone_line(
                line.replace("hub:", "").strip()))
        elif line.startswith("connection:"):
            self.connections.append(self._parse_connection_line(
                line.replace("connection:", "").strip()))
        else:
            raise ValueError(f"Line {line_num}: "
                             f"Unknown syntax on line '{line}'")

    def _parse_zone_line(self, line: str) -> Dict[str, Any]:
        parts = line.split("[")
        base_info = parts[0].strip().split()

        data: Dict[str, Any] = {
            "name": base_info[0],
            "x": int(base_info[1]),
            "y": int(base_info[2]),  # catch errors when wrong imputs later
            "zone_type": "normal",
            "color": None,
            "max_drones": 1
        }

        if len(parts) > 1:
            meta_items = parts[1].replace("]", "").strip().split()

            for item in meta_items:
                if "=" in item:
                    k, v = item.split("=", 1)
                    if k == "zone":
                        data["zone_type"] = v
                    elif k == "color":
                        data["color"] = v
                    elif k == "max_drones":
                        data["max_drones"] = int(v)
            return data

    def _parse_connection_line(self, line: str) -> Dict[str, Any]:
        parts = line.split("[")
        names = parts[0].strip().split("-")

        data: Dict[str, Any] = {
            "zone1_name": names[0],
            "zone2_name": names[1],
            "max_link_capacity": 1
        }

        if len(parts) > 1:
            meta_items = parts[1].replace("]", "").strip().split()

            for item in meta_items:
                if "=" in item:
                    k, v = item.split("=", 1)
                    if k == "max_link_capacity":
                        data["max_link_capacity"] = int(v)
        return data

    def _validate(self) -> None:
        if self.nb_drones <= 0:
            raise ValueError("nb_drones must be a positive integer")
        if self.start_hub is None:
            raise ValueError("Missing start_hub")
        if self.end_hub is None:
            raise ValueError("Missing end_hub")
