"""HTTP interface for observing and driving the simulation."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field

from drone_delivery.core.order import Order
from drone_delivery.services.metrics import render_latest
from drone_delivery.services.simulation import Simulation


class OrderCreate(BaseModel):
    """Payload for a manually injected order."""

    pickup: Tuple[int, int] = Field(..., examples=[(0, 3)])
    delivery: Tuple[int, int] = Field(..., examples=[(7, 7)])


class SimulationState(BaseModel):
    """Snapshot of the world returned by ``GET /state``."""

    step: int
    done: bool
    total_reward: float
    drones: List[Dict[str, Any]]
    orders: List[Dict[str, Any]]


def create_app(sim: Optional[Simulation] = None) -> FastAPI:
    """Build the FastAPI application around an optional simulation.

    Passing ``sim`` makes the app fully injectable, which is what the tests
    use; the module-level :data:`app` below is the default uvicorn target.
    """
    application = FastAPI(
        title="Drone Delivery System",
        version="1.0.0",
        description="HTTP control plane for the multi-agent drone delivery simulator.",
    )
    state: Dict[str, Simulation] = {"sim": sim if sim is not None else Simulation()}

    def current() -> Simulation:
        return state["sim"]

    @application.get("/health", tags=["ops"])
    def health() -> Dict[str, Any]:
        return {"status": "ok", "step": current().step_count}

    @application.get("/state", response_model=SimulationState, tags=["simulation"])
    def get_state() -> Dict[str, Any]:
        sim = current()
        return {
            "step": sim.step_count,
            "done": sim.done,
            "total_reward": sim.world.total_reward,
            "drones": [
                {
                    "id": d.id,
                    "position": list(d.position),
                    "battery": d.battery,
                    "status": d.status,
                    "cargo": d.cargo.id if d.cargo else None,
                }
                for d in sim.world.drones
            ],
            "orders": [
                {
                    "id": o.id,
                    "pickup": list(o.pickup),
                    "delivery": list(o.delivery),
                    "picked_up": o.picked_up,
                    "waiting_steps": o.waiting_steps,
                }
                for o in sim.world.orders
            ],
        }

    @application.post("/order", status_code=201, tags=["simulation"])
    def add_order(order: OrderCreate) -> Dict[str, Any]:
        sim = current()
        if not sim.world.grid.is_free(order.pickup) or not sim.world.grid.is_free(
            order.delivery
        ):
            raise HTTPException(
                status_code=422, detail="pickup and delivery must be on free cells"
            )
        new_order = Order(pickup=order.pickup, delivery=order.delivery)
        sim.world.add_order(new_order)
        return {"status": "added", "id": new_order.id}

    @application.post("/step", tags=["simulation"])
    def step() -> Dict[str, Any]:
        sim = current()
        _, reward, done, info = sim.step()
        return {"step": sim.step_count, "reward": reward, "done": done, **info}

    @application.post("/reset", tags=["simulation"])
    def reset() -> Dict[str, Any]:
        sim = current()
        sim.reset()
        return {"status": "reset", "step": sim.step_count}

    @application.get("/metrics", tags=["ops"])
    def prometheus_metrics() -> Response:
        return Response(content=render_latest(), media_type="text/plain")

    return application


app = create_app()

__all__ = ["OrderCreate", "SimulationState", "app", "create_app"]
