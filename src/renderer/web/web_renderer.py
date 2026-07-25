import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Any, List, Dict
from ...interfaces import Renderer
from ...models import Network, Drone


class WebRenderer(Renderer):
    """Host a local web server to serve simulation data to the browser"""

    def __init__(self, network: Network) -> None:
        self.network = network
        self.app = FastAPI(title="Fly-in Simulator API")

        # CORS is needed so Vite React dev server (port 5173)
        # is allowed to fetch data from FastAPI server (port 8000)
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )

    def _serialize_data(self, drones: List[Drone]) -> Dict[str, Any]:
        """Convert Pydantic models into a clean dictionaries."""
        zones_data = []
        for zone in self.network.zones.values():
            zones_data.append({
                "name": zone.name,
                "x": zone.x,
                "y": zone.y,
                "type": zone.zone_type.value,
                "color": zone.color,
                "max_drones": None
                if zone.max_drones > 90000000
                else zone.max_drones
            })

        conns_data = []
        for conn in self.network.connections:
            conns_data.append({
                "name1": conn.name1,
                "name2": conn.name2,
                "capacity": conn.max_link_capacity
            })

        drones_data = []
        for drone in drones:
            # path is a list of tuples: [("start", 0), ("a", 1), ("goal", 2)]
            drones_data.append({
                "id": drone.id,
                "path": [{"zone": step[0], "turn": step[1]}
                         for step in drone.path]
            })

        return {
            "network": {
                "zones": zones_data,
                "connections": conns_data,
            },
            "drones": drones_data
        }

    def run(self, drones: List[Drone]) -> None:
        data = self._serialize_data(drones)

        @self.app.get("/api/simulation")
        def get_data() -> Dict[str, Any]:
            return data

        print("\n" + "=" * 50)
        print("Web renderer started.")
        print("Data API available at : "
              "http://127.0.0.1:8000/api/simulation")

        uvicorn.run(
            self.app,
            host="127.0.0.1",
            port=8000,
            log_level="error"
            )
