from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Any
from pathlib import Path

from src.parser import Parser
from src.network import Network
from src.engine import Engine

app = FastAPI(title="fly-in API")

MAPS_DIR = Path("maps")


@app.get("/maps")
def list_maps() -> dict[str, Any]:
    """List all available map files grouped by category."""
    maps: list[dict[str, str]] = []
    if MAPS_DIR.is_dir():
        for category_dir in sorted(MAPS_DIR.iterdir()):
            if not category_dir.is_dir():
                continue
            for map_file in sorted(category_dir.glob("*.txt")):
                maps.append({
                    "category": category_dir.name,
                    "name": map_file.stem.replace("_", " ").title(),
                    "filename": map_file.name,
                    "path": f"{category_dir.name}/{map_file.name}",
                })
    return {"maps": maps}


@app.get("/maps/{category}/{filename}")
def get_map(category: str, filename: str) -> dict[str, str]:
    """Return the content of a specific map file."""
    map_path = MAPS_DIR / category / filename
    if not map_path.is_file():
        raise HTTPException(404, "Map not found")
    # Prevent path traversal
    if not map_path.resolve().is_relative_to(MAPS_DIR.resolve()):
        raise HTTPException(403, "Access denied")
    return {"content": map_path.read_text()}


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
