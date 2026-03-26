from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from api.sse import sse_stream
from mortals.memory import MemoryStream
from simulation import SimulationRuntime, create_runtime, execute_divine_action, run_ticks

runtime: SimulationRuntime | None = None


def set_runtime(new_runtime: SimulationRuntime) -> None:
    global runtime
    runtime = new_runtime


@asynccontextmanager
async def lifespan(app: FastAPI):
    global runtime
    if runtime is None:
        runtime = create_runtime(str(Path(__file__).resolve().parent.parent))
    yield


app = FastAPI(title="Divinity Sim", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).resolve().parent.parent / "dashboard" / "static"


class TickBody(BaseModel):
    n: int = Field(default=1, ge=0)


class ActionBody(BaseModel):
    deity: str
    action: str
    target: str = ""
    message: str = ""


def require_runtime() -> SimulationRuntime:
    if runtime is None:
        raise HTTPException(status_code=500, detail="Simulation runtime not initialized.")
    return runtime


@app.get("/api/world")
def get_world():
    rt = require_runtime()
    return {
        "world_name": rt.world.get_prop("world_name", "Evershade"),
        "current_era": rt.world.get_prop("current_era", "Age of Embers"),
        "clock": str(rt.clock),
        "tick": rt.clock.tick,
    }


@app.get("/api/mortals")
def get_mortals():
    rt = require_runtime()
    return rt.world.get_all_mortals(alive_only=True)


@app.get("/api/mortals/{name}/memories")
def get_mortal_memories(name: str):
    rt = require_runtime()
    mortal = rt.world.get_mortal(name)
    if mortal is None:
        raise HTTPException(status_code=404, detail="Mortal not found.")
    return MemoryStream(rt.db_path, name).recent(limit=20)


@app.get("/api/deities")
def get_deities():
    rt = require_runtime()
    return [
        {
            "name": deity.name,
            "title": deity.title,
            "domain": deity.domain,
            "divine_energy": deity.divine_energy,
            "max_energy": deity.max_energy,
            "color": deity.color,
        }
        for deity in rt.pantheon.list_deities()
    ]


@app.get("/api/lore")
def get_lore():
    rt = require_runtime()
    recent = rt.events.get_recent(limit=50)
    return [
        {
            "tick": event.tick,
            "source_name": event.source_name,
            "description": event.description,
            "event_type": event.event_type,
        }
        for event in recent
    ]


@app.post("/api/tick")
def tick_world(body: TickBody):
    rt = require_runtime()
    actions = run_ticks(rt, body.n)
    return {"tick": rt.clock.tick, "actions": actions}


@app.post("/api/action")
def deity_action(body: ActionBody):
    rt = require_runtime()
    try:
        result = execute_divine_action(
            rt,
            deity_name=body.deity,
            action_name=body.action,
            target=body.target,
            message=body.message,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": result}


@app.get("/api/stream")
async def stream():
    return StreamingResponse(sse_stream(), media_type="text/event-stream")


app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
