from typing import List, Dict, Any
import unittest
import tempfile
import os


class Parser:
    def __init__(self, filepath: str):
        self.filepath = filepath

        self.nb_drones: int = 0
        self.start_hub: Dict[str, Any] | None = None
        self.end_hub: Dict[str, Any] | None = None
        self.hubs: List[Dict[str, Any]] = []
        self.connections: List[Dict[str, Any]] = []
        self._start_hub_count = 0
        self._end_hub_count = 0

    def parse(self) -> None:
        try:
            with open(self.filepath, 'r') as f:
                for l_num, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    self._parse_line(line, l_num)
            self._validate()
        except FileNotFoundError:
            raise FileNotFoundError(f"File '{self.filepath}' not found")
        except ValueError as e:
            raise ValueError(f"Line {l_num}: {e}")

    def _parse_line(self, line: str, line_num: int) -> None:
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
        elif line.startswith("end_hub:"):
            self._end_hub_count += 1
            self.end_hub = self._parse_zone_line(
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
            "name1": names[0],
            "name2": names[1],
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
        if self._start_hub_count != 1:
            raise ValueError("Only one start_hub is allowed")
        if self._end_hub_count != 1:
            raise ValueError("Only one end_hub is allowed")

        zone_names = set()
        valid_types = {"normal", "blocked", "restricted", "priority"}
        all_hubs = [self.start_hub, self.end_hub] + self.hubs
        for hub in all_hubs:
            if "-" in hub["name"]:
                raise ValueError(f"Zone name should not contain dashes"
                                 f": {hub["name"]}")
            if hub["max_drones"] <= 0:
                raise ValueError("max_drones must be a positive integer")
            if hub["name"] in zone_names:
                raise ValueError(f"Duplicate zone name found: {hub["name"]}")
            zone_names.add(hub["name"])
            if hub["zone_type"] not in valid_types:
                raise ValueError(f"Invalid zone type: for"
                                 f" {hub["name"]}: {hub["zone_type"]}")

        seen_connections = set()
        for con in self.connections:
            if con["max_link_capacity"] <= 0:
                raise ValueError("max_link_capacity must be "
                                 "a positive integer")
            z1, z2 = con["name1"], con["name2"]
            if z1 not in zone_names or z2 not in zone_names:
                raise ValueError(f"Connection {z1}-{z2} links "
                                 f"to undefined zone(s)")
            conn_tuple = tuple(sorted([z1, z2]))
            if conn_tuple in seen_connections:
                raise ValueError(f"Duplicate connection found: {z1}-{z2}")
            seen_connections.add(conn_tuple)


class TestParser(unittest.TestCase):
    """
    Parser tester. Created by generative AI, but the logic
    was verified
    """
    def setUp(self):
        self.temp_files = []

    def tearDown(self):
        # Clean up temporary files after each test
        for path in self.temp_files:
            if os.path.exists(path):
                os.remove(path)

    def create_temp_map(self, content: str) -> str:
        fd, path = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        self.temp_files.append(path)
        return path

    def test_valid_map(self):
        content = """# Valid map test
nb_drones: 5
start_hub: start 0 0 [color=green max_drones=5]
end_hub: goal 10 10 [color=yellow]
hub: A 1 1 [zone=priority max_drones=2]
hub: B 2 2 [zone=restricted]
connection: start-A [max_link_capacity=3]
connection: A-B
connection: B-goal
"""
        path = self.create_temp_map(content)
        parser = Parser(path)
        parser.parse()

        self.assertEqual(parser.nb_drones, 5)
        self.assertEqual(parser.start_hub["name"], "start")
        self.assertEqual(parser.end_hub["name"], "goal")
        self.assertEqual(len(parser.hubs), 2)
        self.assertEqual(len(parser.connections), 3)
        self.assertEqual(parser.hubs[0]["zone_type"], "priority")

    def test_missing_file(self):
        parser = Parser("non_existent_file.txt")
        with self.assertRaises(FileNotFoundError):
            parser.parse()

    def test_missing_start_or_end(self):
        content = """nb_drones: 5\nend_hub: goal 10 10\n"""
        path = self.create_temp_map(content)
        parser = Parser(path)
        with self.assertRaises(ValueError, msg="Should fail on "
                               "missing start_hub"):
            parser.parse()

    def test_dashes_in_names(self):
        content = """nb_drones: 5\nstart_hub: st-art 0 0\nend_hub: goal 10 10\n"""  # noqa
        path = self.create_temp_map(content)
        parser = Parser(path)
        with self.assertRaises(ValueError, msg="Should fail on "
                               "dashes in zone name"):
            parser.parse()

    def test_invalid_nb_drones(self):
        content = """nb_drones: 0\nstart_hub: start 0 0\nend_hub: goal 1 1\n"""
        path = self.create_temp_map(content)
        parser = Parser(path)
        with self.assertRaises(ValueError, msg="Should fail on 0 drones"):
            parser.parse()

    def test_duplicate_zone_name(self):
        content = """nb_drones: 2
start_hub: A 0 0
end_hub: B 1 1
hub: A 2 2
"""
        path = self.create_temp_map(content)
        parser = Parser(path)
        with self.assertRaises(ValueError, msg="Should fail on"
                               "duplicate zone name A"):
            parser.parse()

    def test_invalid_zone_type(self):
        content = """nb_drones: 2
start_hub: A 0 0
end_hub: B 1 1
hub: C 2 2 [zone=magic]
"""
        path = self.create_temp_map(content)
        parser = Parser(path)
        with self.assertRaises(ValueError, msg="Should fail on "
                               "invalid zone type 'magic'"):
            parser.parse()

    def test_negative_capacity(self):
        content = """nb_drones: 2\nstart_hub: A 0 0\nend_hub: B 1 1 [max_drones=-1]\n""" # noqa
        path = self.create_temp_map(content)
        parser = Parser(path)
        with self.assertRaises(ValueError, msg="Should fail on negative capacity"): # noqa
            parser.parse()

    def test_undefined_connection(self):
        content = """nb_drones: 2\nstart_hub: A 0 0\nend_hub: B 1 1\nconnection: A-C\n""" # noqa
        path = self.create_temp_map(content)
        parser = Parser(path)
        with self.assertRaises(ValueError, msg="Should fail connecting to undefined zone C"): # noqa
            parser.parse()

    def test_duplicate_connection(self):
        content = """nb_drones: 2
start_hub: A 0 0
end_hub: B 1 1
connection: A-B
connection: B-A
"""
        path = self.create_temp_map(content)
        parser = Parser(path)
        with self.assertRaises(ValueError, msg="Should fail on"
                               " duplicate connection B-A"):
            parser.parse()


if __name__ == '__main__':
    unittest.main()
