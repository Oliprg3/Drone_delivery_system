"""The simulated world: the grid plus the entities living on it."""

from __future__ import annotations

from typing import List

from drone_delivery.core.drone import Drone
from drone_delivery.core.grid import Grid
from drone_delivery.core.order import Order


class World:
    """Container for the grid, the fleet and the order book."""

    def __init__(self) -> None:
        self.grid = Grid()
        self.drones: List[Drone] = []
        self.orders: List[Order] = []
        self.completed_orders: List[Order] = []
        self.step_count = 0
        self.total_reward = 0.0

    def add_drone(self, drone: Drone) -> None:
        self.drones.append(drone)

    def add_order(self, order: Order) -> None:
        self.orders.append(order)

    def get_drone(self, drone_id: int) -> Drone:
        return self.drones[drone_id]

    def pending_orders(self) -> List[Order]:
        return [o for o in self.orders if o.is_pending()]

    def transit_orders(self) -> List[Order]:
        return [o for o in self.orders if o.is_in_transit()]

    def active_drones(self) -> List[Drone]:
        return [d for d in self.drones if d.is_active()]

    def clear_orders(self) -> None:
        self.orders.clear()
