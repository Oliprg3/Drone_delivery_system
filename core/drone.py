from dataclasses import dataclass
from typing import Optional, Tuple, List
from core.order import Order
from config import settings

@dataclass
class Drone:
    id: int
    position: Tuple[int, int]
    battery: float = settings.MAX_BATTERY
    cargo: Optional[Order] = None
    path: List[Tuple[int, int]] = None
    target: Optional[Tuple[int, int]] = None
    status: str = "idle"  

    def move_along_path(self):
        if not self.path:
            return
        next_pos = self.path.pop(0)
        dist = abs(next_pos[0] - self.position[0]) + abs(next_pos[1] - self.position[1])
        self.battery = max(0, self.battery - dist * settings.BATTERY_DRAIN_PER_STEP)
        self.position = next_pos
        if self.battery <= 0:
            self.status = "dead"
        if not self.path and self.status != "dead":
            self.status = "idle"

    def assign_task(self, target: Tuple[int, int], path: List[Tuple[int, int]]):
        self.target = target
        self.path = path
        self.status = "moving"

    def pick_cargo(self, order: Order):
        self.cargo = order
        order.picked_up = True
        order.assigned_drone = self
        self.status = "delivering"

    def deliver_cargo(self):
        if self.cargo:
            self.cargo.delivered = True
            self.cargo = None
            self.status = "idle"

    def is_active(self) -> bool:
        return self.battery > 0 and self.status != "dead"
