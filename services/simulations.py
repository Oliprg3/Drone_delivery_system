import random
from typing import List, Dict, Any, Optional
from core.world import World
from core.drone import Drone
from core.order import Order
from services.pathfinder import Pathfinder
from services.collision_avoidance import CollisionAvoidance
from services.order_generator import OrderGenerator
from services.metrics import Metrics
from config import settings

class Simulation:
    def __init__(self):
        self.world = World()
        self.pathfinder = Pathfinder(self.world.grid)
        self.collision = CollisionAvoidance(self.world.grid)
        self.order_gen = OrderGenerator(self.world.grid)
        self.metrics = Metrics()
        self._init_drones()
        self.step_count = 0
        self.done = False

    def _init_drones(self):
        for i in range(settings.NUM_DRONES):
            start = (0,0)  # all start at base
            drone = Drone(i, start)
            self.world.add_drone(drone)

    def reset(self) -> Dict:
        self.world = World()
        self.pathfinder = Pathfinder(self.world.grid)
        self.collision = CollisionAvoidance(self.world.grid)
        self.order_gen = OrderGenerator(self.world.grid)
        self._init_drones()
        self.step_count = 0
        self.done = False
        return self._get_observation()

    def step(self, actions: List[Any]) -> tuple:
        self.step_count += 1
        self._spawn_orders()
        self._apply_weather()
        self._move_drones(actions)
        self.collision.resolve_conflicts(self.world.drones)
        self._check_deliveries()
        self._update_metrics()

        if self.step_count >= settings.MAX_STEPS:
            self.done = True

        return self._get_observation(), self.world.total_reward, self.done, {}

    def _spawn_orders(self):
        if len(self.world.orders) < settings.MAX_ACTIVE_ORDERS and random.random() < settings.ORDER_FREQUENCY:
            order = self.order_gen.generate_order()
            self.world.add_order(order)

    def _apply_weather(self):
        # Simulate wind affecting movement: randomly change drone position? simpler: drain extra battery
        if random.random() < 0.1:  # 10% chance of strong wind
            for drone in self.world.drones:
                if drone.is_active():
                    drone.battery = max(0, drone.battery - 0.5)

    def _move_drones(self, actions):
        for idx, drone in enumerate(self.world.drones):
            if not drone.is_active():
                continue
            # If drone has no task, assign one based on agent action (or heuristic)
            # Here we assume actions are provided by agents (could be None for heuristic)
            # For RL, action might be index of order to pick? For simplicity, we handle inside agents.
            # The simulation doesn't directly use actions; agents set drone's target/path via services.
            # So we just move along existing path.
            if drone.status == "moving":
                drone.move_along_path()
                if drone.status == "idle":
                    # Arrived at target: check if it's pickup or delivery
                    if drone.target and any(o.pickup == drone.target and not o.picked_up for o in self.world.orders):
                        for o in self.world.orders:
                            if not o.picked_up and o.pickup == drone.target:
                                drone.pick_cargo(o)
                                break
                    elif drone.target and any(o.delivery == drone.target and o.picked_up and not o.delivered and o.assigned_drone == drone for o in self.world.orders):
                        for o in self.world.orders:
                            if o.delivery == drone.target and o.picked_up and not o.delivered and o.assigned_drone == drone:
                                drone.deliver_cargo()
                                self.world.completed_orders.append(o)
                                self.world.orders.remove(o)
                                self.world.total_reward += 10.0
                                break

    def _check_deliveries(self):
        # Timeout penalty for waiting orders
        for o in self.world.orders[:]:
            o.waiting_steps += 1
            if o.waiting_steps > 200:
                self.world.total_reward -= 2.0
                self.world.orders.remove(o)

    def _update_metrics(self):
        self.metrics.record(self.world)

    def _get_observation(self) -> Dict:
        return {
            "drones": [d.position for d in self.world.drones],
            "batteries": [d.battery for d in self.world.drones],
            "cargos": [1 if d.cargo else 0 for d in self.world.drones],
            "pickups": [o.pickup for o in self.world.orders if not o.picked_up],
            "deliveries": [o.delivery for o in self.world.orders if o.picked_up and not o.delivered]
        }

    def get_path(self, start, goal):
        return self.pathfinder.find_path(start, goal)

    def assign_task_to_drone(self, drone_id: int, target: tuple, path: list):
        drone = self.world.drones[drone_id]
        if drone.is_active():
            drone.assign_task(target, path)
