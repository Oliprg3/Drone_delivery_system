from typing import List, Dict, Tuple
from core.drone import Drone
from core.order import Order
from core.grid import Grid

class World:
    def __init__(self):
        self.grid = Grid()
        self.drones: List[Drone] = []
        self.orders: List[Order] = []
        self.completed_orders: List[Order] = []
        self.step_count = 0
        self.total_reward = 0.0

    def add_drone(self, drone: Drone):
        self.drones.append(drone)

    def add_order(self, order: Order):
        self.orders.append(order)
