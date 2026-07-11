import random
from .base import BaseAgent
from typing import Dict

class RandomAgent(BaseAgent):
    def act(self, observation: Dict) -> None:
        drone = self.sim.world.drones[self.drone_id]
        if not drone.is_active() or drone.status != "idle":
            return
        free_cells = [ (r,c) for r in range(self.sim.world.grid.rows) for c in range(self.sim.world.grid.cols) if self.sim.world.grid.is_free((r,c)) ]
        if free_cells:
            target = random.choice(free_cells)
            path = self.sim.get_path(drone.position, target)
            if path:
                self.sim.assign_task_to_drone(self.drone_id, target, path)
