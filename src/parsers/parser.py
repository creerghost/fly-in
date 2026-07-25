"""Parser module for reading and validating map configuration files."""

from typing import List, Dict, Any, Tuple
from ..models import Network
from ..models.zone import Zone
from ..models.connection import Connection


class Parser:
    """Parser for reading and validating the map configuration file."""

    def __init__(self, filepath: str) -> None:
        """Initialize the parser with the target file path."""
        self.filepath = filepath

        self.nb_drones: int = 0
        self._start_hub: Zone | None = None
        self._end_hub: Zone | None = None
        self._hubs: List[Zone] = []
        self._connections: List[Connection] = []
        self._start_hub_count = 0
        self._end_hub_count = 0

    def parse(self) -> Network:
        """
        Read and parse the file line by line, then validate constraints.

        Returns a fully constructed Network domain object.
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
        except IsADirectoryError:
            raise IsADirectoryError(f"'{self.filepath}' is a directory")
        except ValueError as e:
            raise ValueError(f"Line {l_num}: {e}")

        if self._start_hub is None or self._end_hub is None:
            raise ValueError("start_hub and end_hub must be defined")

        return Network(
            nb_drones=self.nb_drones,
            start_hub=self._start_hub,
            end_hub=self._end_hub,
            hubs=self._hubs if self._hubs else None,
            connections=self._connections
        )

    def _parse_line(self, line: str, line_num: int) -> None:
        """Parse an individual line from the configuration file."""
        if line.startswith("nb_drones"):
            drones = line.split(":")
            if len(drones) != 2 or not drones[1].strip().isdigit():
                raise ValueError(f"Line {line_num}: "
                                 f"Invalid nb_drones format")
            self.nb_drones = int(drones[1].strip())
        elif line.startswith("start_hub:"):
            self._start_hub_count += 1
            self._start_hub = self._parse_zone_line(
                line.replace("start_hub:", "").strip())
        elif line.startswith("end_hub:"):
            self._end_hub_count += 1
            self._end_hub = self._parse_zone_line(
                line.replace("end_hub:", "").strip())
        elif line.startswith("hub:"):
            hub = self._parse_zone_line(
                line.replace("hub:", "").strip())
            self._hubs.append(hub)
        elif line.startswith("connection:"):
            conn = self._parse_connection_line(
                line.replace("connection:", "").strip())

            defined_zones = {h.name for h in self._hubs}
            if self._start_hub:
                defined_zones.add(self._start_hub.name)
            if self._end_hub:
                defined_zones.add(self._end_hub.name)

            if (conn.name1 not in defined_zones or
                    conn.name2 not in defined_zones):
                raise ValueError("Connection links to undefined zone")

            self._connections.append(conn)
        else:
            raise ValueError(f"Line {line_num}: "
                             f"Unknown syntax on line '{line}'")

    @staticmethod
    def _parse_metadata(line: str) -> Tuple[str, Dict[str, str]]:
        """Extract metadata tags from brackets inside a line string."""
        if "[" in line or "]" in line:
            if (line.count("[") != 1 or
                    line.count("]") != 1 or
                    not line.endswith("]")):
                raise ValueError("Invalid metadata block syntax")

        parts = line.split("[")
        base_info = parts[0].strip()
        data: Dict[str, str] = {}

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
        return base_info, data

    def _parse_zone_line(self, line: str) -> Zone:
        """Extract node data and metadata attributes from a zone string."""
        base_info_str, meta_data = self._parse_metadata(line)
        base_info = base_info_str.split()

        if len(base_info) != 3:
            raise ValueError("Invalid syntax for zone line")

        zone_data: Dict[str, Any] = {
            "name": base_info[0],
            "x": base_info[1],
            "y": base_info[2],
        }
        zone_data.update(meta_data)

        return Zone(**zone_data)

    def _parse_connection_line(self, line: str) -> Connection:
        """Extract edge data and link capacity from a connection string."""
        base_info_str, meta_data = self._parse_metadata(line)
        names = base_info_str.split("-")

        if len(names) != 2:
            raise ValueError(f"Invalid connection syntax: {line}")

        z1 = names[0].strip()
        z2 = names[1].strip()

        if not z1 or not z2:
            raise ValueError("Connection zone names cannot be empty")

        conn_data: Dict[str, Any] = {
            "name1": z1,
            "name2": z2,
        }
        conn_data.update(meta_data)

        return Connection(**conn_data)
