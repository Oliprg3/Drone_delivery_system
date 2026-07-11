from .base import BaseAgent
from typing import Dict
from core.order import Order

class HeuristicAgent(BaseAgent):
    def act(self, observation: Dict) -> None:
        drone = self.sim.world.drones[self.drone_id]
        if not drone.is_active():
            return
        if drone.status == "idle":
            if drone.cargo:
                path = self.sim.get_path(drone.position, drone.cargo.delivery)
                if path:
                    self.sim.assign_task_to_drone(self.drone_id, drone.cargo.delivery, path)
            else:
                available = [o for o in self.sim.world.orders if not o.picked_up and not o.delivered]
                if available:
                    nearest = min(available, key=lambda o: abs(o.pickup[0]-drone.position[0]) + abs(o.pickup[1]-drone.position[1]))
                    path = self.sim.get_path(drone.position, nearest.pickup)
                    if path:
                        self.sim.assign_task_to_drone(self.drone_id, nearest.pickup, path)
