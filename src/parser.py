from typing import List, Dict, Any


class Parser:
    """
    Parses and validates the map configuration file.
    """
    def __init__(self, filepath: str) -> None:
        """
        Initialize the parser with the target file path.
        """
        self.filepath = filepath

        self.nb_drones: int = 0
        self.start_hub: Dict[str, Any] | None = None
        self.end_hub: Dict[str, Any] | None = None
        self.hubs: List[Dict[str, Any]] = []
        self.connections: List[Dict[str, Any]] = []
        self._start_hub_count = 0
        self._end_hub_count = 0
        self.zone_names: set[str] = set()

    def parse(self) -> None:
        """
        Read and parse the file line by line, then validate constraints.
        """
        try:
            with open(self.filepath, 'r') as f:
                for l_num, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if not line.startswith("nb_drones") and not self.nb_drones:
                        raise ValueError(f"Line {l_num}: "
                                         f"nb_drones must be defined "
                                         f"before any zones")
                    self._parse_line(line, l_num)
            # self._validate()
            if self._start_hub_count != 1:
                raise ValueError("Only one start_hub is allowed")
            if self._end_hub_count != 1:
                raise ValueError("Only one end_hub is allowed")
        except FileNotFoundError:
            raise FileNotFoundError(f"File '{self.filepath}' not found")
        except ValueError as e:
            raise ValueError(f"Line {l_num}: {e}")

    def _parse_line(self, line: str, line_num: int) -> None:
        """
        Parse an individual line from the configuration file.
        """
        if line.startswith("nb_drones"):
            drones = line.split(":")
            if len(drones) != 2 or not drones[1].strip().isdigit():
                raise ValueError(f"Line {line_num}: "
                                 f"Invalid nb_drones format")
            self.nb_drones = int(drones[1].strip())
        elif line.startswith("start_hub:"):
            self._start_hub_count += 1
            self.start_hub = self._parse_zone_line(
                line.replace("start_hub:", "").strip())
            self.zone_names.add(self.start_hub["name"])
        elif line.startswith("end_hub:"):
            self._end_hub_count += 1
            self.end_hub = self._parse_zone_line(
                line.replace("end_hub:", "").strip())
            self.zone_names.add(self.end_hub["name"])
        elif line.startswith("hub:"):
            hub_data = self._parse_zone_line(
                line.replace("hub:", "").strip())
            self.hubs.append(hub_data)
            self.zone_names.add(hub_data["name"])
        elif line.startswith("connection:"):
            self.connections.append(self._parse_connection_line(
                line.replace("connection:", "").strip()))
        else:
            raise ValueError(f"Line {line_num}: "
                             f"Unknown syntax on line '{line}'")

    def _parse_zone_line(self, line: str) -> Dict[str, Any]:
        """
        Extract node data and metadata attributes from a zone string.
        """
        if "[" in line or "]" in line:
            if (line.count("[") != 1 or
                    line.count("]") != 1 or
                    not line.endswith("]")):
                raise ValueError("Invalid metadata block syntax")

        parts = line.split("[")
        base_info = parts[0].strip().split()
        if len(base_info) != 3:
            raise ValueError("Invalid syntax for zone line")
        data: Dict[str, Any] = {
            "name": base_info[0],
            "x": int(base_info[1]),
            "y": int(base_info[2]),  # catch errors when wrong imputs later
            "zone_type": "normal",
            "color": None,
            "max_drones": 1
        }

        if len(parts) > 1:
            meta_str = parts[1].replace("]", "").strip()
            if not meta_str:
                raise ValueError("Empty metadata block inside brackets")
            meta_items = meta_str.split()
            seen_keys = set()
            allowed_keys = {"zone", "color", "max_drones"}
            for item in meta_items:
                if "=" not in item or item.count("=") != 1:
                    raise ValueError(f"Invalid metadata item syntax: "
                                     f"'{item}'")
                k, v = item.split("=")
                k = k.strip()
                v = v.strip()
                if not k or not v:
                    raise ValueError(f"Invalid metadata item: '{item}'")
                if k in seen_keys:
                    raise ValueError(f"Duplicate metadata key: '{k}'")
                seen_keys.add(k)
                if k not in allowed_keys:
                    raise ValueError(f"Unknown zone metadata key: '{k}'")

                if k == "zone":
                    data["zone_type"] = v
                elif k == "color":
                    data["color"] = v
                elif k == "max_drones":
                    try:
                        max_d = int(v)
                        if max_d <= 0:
                            raise ValueError(f"max_drones must be a "
                                             f"positive integer, got: {v}")
                        data["max_drones"] = max_d
                    except ValueError:
                        raise ValueError(f"max_drones must be an "
                                         f"integer, got: {v}")
        return data

    def _parse_connection_line(self, line: str) -> Dict[str, Any]:
        """
        Extract edge data and link capacity metadata from a connection string.
        """
        if "[" in line or "]" in line:
            if (line.count("[") != 1 or
                    line.count("]") != 1 or
                    not line.endswith("]")):
                raise ValueError("Invalid metadata block syntax")

        parts = line.split("[")
        names = parts[0].strip().split("-")

        if len(names) != 2:
            raise ValueError(f"Invalid connection syntax: {line}")

        z1 = names[0].strip()
        z2 = names[1].strip()

        if not z1 or not z2:
            raise ValueError("Connection zone names cannot be empty")

        if z1 not in self.zone_names or z2 not in self.zone_names:
            raise ValueError(f"Connection {z1}-{z2} links to "
                             f"undefined zone(s)")

        data: Dict[str, Any] = {
            "name1": z1,
            "name2": z2,
            "max_link_capacity": 1
        }

        if len(parts) > 1:
            meta_str = parts[1].replace("]", "").strip()
            if not meta_str:
                raise ValueError("Empty metadata block inside brackets")
            meta_items = meta_str.split()
            seen_keys = set()
            allowed_keys = {"max_link_capacity"}
            for item in meta_items:
                if "=" not in item or item.count("=") != 1:
                    raise ValueError(f"Invalid metadata item syntax: "
                                     f"'{item}'")
                k, v = item.split("=")
                k = k.strip()
                v = v.strip()
                if not k or not v:
                    raise ValueError(f"Invalid metadata item: '{item}'")
                if k in seen_keys:
                    raise ValueError(f"Duplicate metadata key: '{k}'")
                seen_keys.add(k)
                if k not in allowed_keys:
                    raise ValueError(f"Unknown connection metadata key: '{k}'")

                if k == "max_link_capacity":
                    try:
                        max_c = int(v)
                        if max_c <= 0:
                            raise ValueError(f"max_link_capacity must be "
                                             f"a positive integer, got: {v}")
                        data["max_link_capacity"] = max_c
                    except ValueError:
                        raise ValueError(f"max_link_capacity must be "
                                         f"an integer, got: {v}")
        return data

    # def _validate(self) -> None:
    #     """
    #     Validate all parsed data against project constraints
    #     (unique hubs, capacities, etc).
    #     """
    #     if self.nb_drones <= 0:
    #         raise ValueError("nb_drones must be a positive integer")
    #     if self.start_hub is None:
    #         raise ValueError("Missing start_hub")
    #     if self.end_hub is None:
    #         raise ValueError("Missing end_hub")
    #     if self._start_hub_count != 1:
    #         raise ValueError("Only one start_hub is allowed")
    #     if self._end_hub_count != 1:
    #         raise ValueError("Only one end_hub is allowed")

    #     zone_names = set()
    #     valid_types = {"normal", "blocked", "restricted", "priority"}
    #     all_hubs = [self.start_hub, self.end_hub] + self.hubs
    #     for hub in all_hubs:
    #         if "-" in hub["name"]:
    #             raise ValueError(f"Zone name should not contain dashes"
    #                              f": {hub["name"]}")
    #         if hub["max_drones"] <= 0:
    #             raise ValueError("max_drones must be a positive integer")
    #         if hub["name"] in zone_names:
    #             raise ValueError(f"Duplicate zone name found: {hub["name"]}")
    #         zone_names.add(hub["name"])
    #         if hub["zone_type"] not in valid_types:
    #             raise ValueError(f"Invalid zone type: for"
    #                              f" {hub["name"]}: {hub["zone_type"]}")

    #     seen_connections = set()
    #     for con in self.connections:
    #         if con["max_link_capacity"] <= 0:
    #             raise ValueError("max_link_capacity must be "
    #                              "a positive integer")
    #         z1, z2 = con["name1"], con["name2"]
    #         if z1 not in zone_names or z2 not in zone_names:
    #             raise ValueError(f"Connection {z1}-{z2} links "
    #                              f"to undefined zone(s)")
    #         conn_tuple = tuple(sorted([z1, z2]))
    #         if conn_tuple in seen_connections:
    #             raise ValueError(f"Duplicate connection found: {z1}-{z2}")
    #         seen_connections.add(conn_tuple)
