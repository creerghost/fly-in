from typing import List, Dict, Any, Iterable


class Parser:
    """
    Parses and validates the map configuration file.
    """
    def __init__(self, filepath: str = "") -> None:
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
                self._parse_lines(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"File '{self.filepath}' not found")
        except IsADirectoryError:
            raise IsADirectoryError(f"'{self.filepath}' is a directory")

    def parse_from_string(self, content: str) -> None:
        """
        Parse map content directly from a string instead of a file.
        """
        self._parse_lines(content.splitlines())

    def _parse_lines(self, lines: Iterable[str]) -> None:
        """
        Core line-by-line parsing and validation logic.
        """
        l_num = 0
        try:
            for l_num, line in enumerate(lines, start=1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if not line.startswith("nb_drones") and not self.nb_drones:
                    raise ValueError(f"Line {l_num}: "
                                     f"nb_drones must be defined "
                                     f"before any zones")
                self._parse_line(line, l_num)
            if self._start_hub_count != 1:
                raise ValueError("Only one start_hub is allowed")
            if self._end_hub_count != 1:
                raise ValueError("Only one end_hub is allowed")
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
            "x": base_info[1],
            "y": base_info[2],
        }

        if len(parts) > 1:
            meta_str = parts[1].replace("]", "").strip()
            if not meta_str:
                raise ValueError("Empty metadata block inside brackets")
            meta_items = meta_str.split()
            for item in meta_items:
                if "=" not in item or item.count("=") != 1:
                    raise ValueError(f"Invalid metadata item syntax: "
                                     f"'{item}'")
                k, v = item.split("=")
                data[k.strip()] = v.strip()
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
        }

        if len(parts) > 1:
            meta_str = parts[1].replace("]", "").strip()
            if not meta_str:
                raise ValueError("Empty metadata block inside brackets")
            meta_items = meta_str.split()
            for item in meta_items:
                if "=" not in item or item.count("=") != 1:
                    raise ValueError(f"Invalid metadata item syntax: "
                                     f"'{item}'")
                k, v = item.split("=")
                data[k.strip()] = v.strip()
        return data
