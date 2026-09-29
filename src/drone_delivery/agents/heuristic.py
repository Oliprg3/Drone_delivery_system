"""Distance-greedy policy: finish the current job, otherwise take the nearest order."""

from __future__ import annotations

from typing import Any, Dict

from drone_delivery.agents.base import BaseAgent
from drone_delivery.core.order import Position


def manhattan(a: Position, b: Position) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


class HeuristicAgent(BaseAgent):
    """Prioritises an in-flight delivery, otherwise grabs the closest pickup.

    This is the default policy and the baseline the learned policy is compared
    against.
    """

    def act(self, observation: Dict[str, Any]) -> None:
        drone = self.drone
        if not drone.is_available():
            return

        if drone.cargo is not None:
            self.plan_to(drone.cargo.delivery)
            return

        candidates = self.sim.world.pending_orders()
        if not candidates:
            return

        nearest = min(candidates, key=lambda o: manhattan(drone.position, o.pickup))
        self.plan_to(nearest.pickup)
