from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any

from src.parser import Parser
from src.network import Network
from src.engine import Engine

app = FastAPI(title="fly-in API")


class RunRequest(BaseModel):
    """Request body for creating a simulation run."""
    map_content: str  # the raw text of a .txt map file


@app.get("/")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "service": "fly-in API"}


@app.post("/runs")
def create_run(body: RunRequest) -> dict[str, Any]:
    """
    Run a drone simulation from map content.
    Returns the turn-by-turn results as JSON.
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

    return {
        "nb_drones": parser.nb_drones,
        "turns_total": len(turns),
        "turns": turns,
    }
