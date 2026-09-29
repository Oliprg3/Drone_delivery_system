"""The simulation loop: orders in, drones out, deliveries counted."""

from __future__ import annotations

import random
import time
from typing import Any, Dict, List, Optional, Tuple

from drone_delivery.config import settings
from drone_delivery.core.drone import Drone
from drone_delivery.core.grid import Position
from drone_delivery.core.world import World
from drone_delivery.services.collision_avoidance import CollisionAvoidance
from drone_delivery.services.metrics import Metrics
from drone_delivery.services.order_generator import OrderGenerator
from drone_delivery.services.pathfinder import Pathfinder


class Simulation:
    """Owns the world and advances it one tick at a time.

    Control flow per step: spawn orders, apply weather, let every drone move,
    resolve collisions, then settle pickups and deliveries. Drones are steered
    by the :mod:`drone_delivery.agents` layer, which plans routes through
    :meth:`get_path` and :meth:`assign_task_to_drone`; the ``actions`` argument
    of :meth:`step` is reserved for learned policies and is not consulted here.
    """

    def __init__(self) -> None:
        self.metrics = Metrics()
        self.reset()

    # -- lifecycle -----------------------------------------------------------

    def reset(self) -> Dict[str, Any]:
        """Rebuild the world from scratch and return the first observation."""
        self.world = World()
        self.pathfinder = Pathfinder(self.world.grid)
        self.collision = CollisionAvoidance(self.world.grid)
        self.order_generator = OrderGenerator(self.world.grid)
        self.step_count = 0
        self.done = False
        self._reward_mark = 0.0
        self._spawn_drones()
        return self.get_observation()

    def _spawn_drones(self) -> None:
        """Place each drone on a distinct free cell near the depot.

        The previous implementation started every drone on ``(0, 0)``, so the
        whole fleet was in collision on the very first tick.
        """
        grid = self.world.grid
        free = grid.free_cells()
        if not free:
            raise RuntimeError("Grid is fully blocked; cannot spawn any drone")

        depot_r, depot_c = grid.depot
        free.sort(
            key=lambda cell: abs(cell[0] - depot_r) + abs(cell[1] - depot_c)
        )

        for index in range(settings.NUM_DRONES):
            if index < len(free):
                start = free[index]
            else:  # more drones than free cells: wrap around, de-duplicated later
                start = free[index % len(free)]
            self.world.add_drone(Drone(id=index, position=start))

    # -- stepping ------------------------------------------------------------

    def step(self, actions: Optional[List[Any]] = None) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """Advance the world by one tick.

        Returns:
            ``(observation, step_reward, done, info)`` where ``step_reward`` is
            the reward accumulated during *this* tick only, not the cumulative
            world total.
        """
        started = time.perf_counter()
        self.step_count += 1
        self.world.step_count = self.step_count

        self._spawn_orders()
        self._apply_weather()
        self._move_drones()
        self.collision.resolve_conflicts(self.world.drones)
        self._settle_drones()
        self._expire_stale_orders()

        step_reward = self.world.total_reward - self._reward_mark
        self._reward_mark = self.world.total_reward

        self.metrics.record(self.world)
        self.metrics.observe_step(time.perf_counter() - started)

        if self.step_count >= settings.MAX_STEPS:
            self.done = True

        info = {
            "step": self.step_count,
            "deliveries": len(self.world.completed_orders),
            "active_orders": len(self.world.orders),
            "total_reward": self.world.total_reward,
        }
        return self.get_observation(), step_reward, self.done, info

    # -- simulation phases ---------------------------------------------------

    def _spawn_orders(self) -> None:
        if len(self.world.orders) >= settings.MAX_ACTIVE_ORDERS:
            return
        if random.random() >= settings.ORDER_FREQUENCY:
            return
        try:
            self.world.add_order(self.order_generator.generate_order())
        except RuntimeError:
            pass  # grid too congested for another order right now

    def _apply_weather(self) -> None:
        if random.random() >= settings.WEATHER_EVENT_PROBABILITY:
            return
        for drone in self.world.active_drones():
            drone.battery = max(0.0, drone.battery - settings.WEATHER_BATTERY_PENALTY)
            if drone.battery <= 0:
                drone.status = "dead"

    def _move_drones(self) -> None:
        for drone in self.world.drones:
            if drone.is_active() and drone.status == "moving":
                drone.move_along_path()

    def _settle_drones(self) -> None:
        """Complete pickups and deliveries for drones that reached their target.

        A drone carrying cargo is settled too, otherwise the order book would
        keep growing: the agent is expected to plan the delivery leg as soon as
        the pickup happens, which flips the drone back to ``moving``.
        """
        for drone in self.world.drones:
            if not drone.is_available() or drone.target is None:
                continue

            if drone.cargo is not None:
                self._complete_delivery(drone)
            else:
                self._complete_pickup(drone)

    def _complete_pickup(self, drone: Drone) -> None:
        for order in self.world.orders:
            if order.is_pending() and order.pickup == drone.target:
                drone.pick_cargo(order)
                return

    def _complete_delivery(self, drone: Drone) -> None:
        cargo = drone.cargo
        if cargo.delivery != drone.target:
            return
        drone.deliver_cargo()
        self.world.orders.remove(cargo)
        self.world.completed_orders.append(cargo)
        self.world.total_reward += settings.DELIVERY_REWARD
        self.metrics.record_delivery(cargo.id)

    def _expire_stale_orders(self) -> None:
        for order in self.world.orders[:]:
            order.waiting_steps += 1
            if order.waiting_steps > settings.ORDER_EXPIRY_STEPS:
                self.world.orders.remove(order)
                self.world.total_reward += settings.ORDER_TIMEOUT_PENALTY
                self.metrics.record_expiry()

    # -- agent interface -----------------------------------------------------

    def get_path(
        self, start: Position, goal: Position
    ) -> Optional[List[Position]]:
        return self.pathfinder.find_path(start, goal)

    def assign_task_to_drone(
        self, drone_id: int, target: Position, path: List[Position]
    ) -> bool:
        drone = self.world.get_drone(drone_id)
        if not drone.is_available():
            return False
        drone.assign_task(target, path)
        return True

    def get_observation(self) -> Dict[str, Any]:
        return {
            "drones": [d.position for d in self.world.drones],
            "batteries": [d.battery for d in self.world.drones],
            "cargos": [1 if d.cargo else 0 for d in self.world.drones],
            "pickups": [o.pickup for o in self.world.pending_orders()],
            "deliveries": [o.delivery for o in self.world.transit_orders()],
        }
