"""Baseline policy that wanders to a uniformly random free cell."""

from __future__ import annotations

import random
from typing import Any, Dict

from drone_delivery.agents.base import BaseAgent


class RandomAgent(BaseAgent):
    """Wanderer baseline: it never picks a job, it just moves.

    Useful to measure how much of the score comes from the environment rather
    than from the policy.
    """

    def act(self, observation: Dict[str, Any]) -> None:
        drone = self.drone
        if not drone.is_available():
            return

        free_cells = self.sim.world.grid.free_cells()
        if free_cells:
            self.plan_to(random.choice(free_cells))
