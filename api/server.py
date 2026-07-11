from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Tuple
import threading
import time
from services.simulation import Simulation
from agents.heuristic_agent import HeuristicAgent

app = FastAPI()
sim = Simulation()
agent = HeuristicAgent(0, sim)  

class OrderCreate(BaseModel):
    pickup: Tuple[int, int]
    delivery: Tuple[int, int]

@app.get("/state")
def get_state():
    return sim._get_observation()

@app.post("/order")
def add_order(order: OrderCreate):
    sim.world.add_order(Order(order.pickup, order.delivery))
    return {"status": "added"}

@app.post("/step")
def step():
    sim.step([None]*sim.world.drones)  
    return {"step": sim.step_count}

@app.post("/reset")
def reset():
    sim.reset()
    return {"status": "reset"}

@app.get("/metrics")
def get_metrics():
    return {"deliveries": len(sim.world.completed_orders)}
