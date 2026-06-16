from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Any

from src.parser import Parser
from src.network import Network
from src.engine import Engine

app = FastAPI(title="fly-in API")


class RunRequest(BaseModel):
    """Request body for creating a simulation run."""
    map_content: str  # the raw text of a .txt map file


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "service": "fly-in API"}


@app.post("/runs")
def create_run(body: RunRequest) -> dict[str, Any]:
    """
    Run a drone simulation from map content.
    Returns the turn-by-turn results as JSON with map topology.
    """
    try:
        parser = Parser()
        parser.parse_from_string(body.map_content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Parse error: {e}")

    try:
        network = Network(parser)
        engine = Engine(network)
        turns = engine.run_and_collect()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Simulation error: {e}")

    # Build zone data for the frontend canvas
    zones_data = []
    for name, zone in network.zones.items():
        zone_info: dict[str, Any] = {
            "name": name,
            "x": zone.x,
            "y": zone.y,
            "type": zone.zone_type.value,
            "max_drones": zone.max_drones,
        }
        assert parser.start_hub is not None
        assert parser.end_hub is not None
        if name == parser.start_hub["name"]:
            zone_info["role"] = "start"
        elif name == parser.end_hub["name"]:
            zone_info["role"] = "end"
        else:
            zone_info["role"] = "hub"
        zones_data.append(zone_info)

    connections_data = [
        {"from": c.name1, "to": c.name2, "capacity": c.max_link_capacity}
        for c in network.connections
    ]

    return {
        "nb_drones": parser.nb_drones,
        "turns_total": len(turns),
        "zones": zones_data,
        "connections": connections_data,
        "turns": turns,
    }


# Serve frontend at root
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def serve_frontend() -> FileResponse:
    """Serve the frontend."""
    return FileResponse("static/index.html")
