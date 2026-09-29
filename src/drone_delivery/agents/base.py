"""Common interface shared by every drone policy."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from drone_delivery.core.drone import Drone
from drone_delivery.services.simulation import Simulation


class BaseAgent(ABC):
    """One policy instance per drone.

    A policy is a pure planner: it inspects the world and, when the drone is
    idle, asks the simulation for a route. It never mutates the drone directly,
    which keeps the simulation the single source of truth.
    """

    def __init__(self, drone_id: int, sim: Simulation) -> None:
        self.drone_id = drone_id
        self.sim = sim

    @property
    def drone(self) -> Drone:
        return self.sim.world.get_drone(self.drone_id)

    @abstractmethod
    def act(self, observation: Dict[str, Any]) -> None:
        """Decide what the drone should do for the current tick."""

    # -- helpers shared by concrete policies ---------------------------------

    def plan_to(self, target) -> bool:
        """Route the drone to ``target``.

        Returns:
            False if the drone is busy or no route exists, in which case no task
            is assigned and the drone keeps its current state.
        """
        if not self.drone.is_available():
            return False
        path = self.sim.get_path(self.drone.position, target)
        if path is None:
            return False
        return self.sim.assign_task_to_drone(self.drone_id, target, path)
