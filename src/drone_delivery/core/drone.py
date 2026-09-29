"""A single drone: position, battery, cargo and planned route."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from drone_delivery.config import settings
from drone_delivery.core.order import Order, Position


@dataclass
class Drone:
    """One agent in the fleet.

    ``status`` moves through ``idle`` -> ``moving`` -> ``delivering`` ->
    ``idle``, and becomes ``dead`` once the battery is exhausted.
    """

    id: int
    position: Position
    battery: float = field(default_factory=lambda: settings.MAX_BATTERY)
    cargo: Optional[Order] = None
    path: List[Position] = field(default_factory=list)
    target: Optional[Position] = None
    status: str = "idle"

    def move_along_path(self) -> None:
        """Advance one cell along the planned route and drain the battery."""
        if not self.path:
            if self.status == "moving":
                self.status = self._resting_status()
            return
        next_pos = self.path.pop(0)
        distance = abs(next_pos[0] - self.position[0]) + abs(
            next_pos[1] - self.position[1]
        )
        self.battery = max(0.0, self.battery - distance * settings.BATTERY_DRAIN_PER_STEP)
        self.position = next_pos
        if self.battery <= 0:
            self.status = "dead"
        elif not self.path:
            self.status = self._resting_status()

    def _resting_status(self) -> str:
        return "delivering" if self.cargo is not None else "idle"

    def assign_task(self, target: Position, path: List[Position]) -> None:
        self.target = target
        self.path = list(path)
        self.status = "moving" if self.path else self._resting_status()

    def pick_cargo(self, order: Order) -> None:
        self.cargo = order
        order.picked_up = True
        order.assigned_drone = self
        self.status = "delivering"

    def deliver_cargo(self) -> None:
        if self.cargo is not None:
            self.cargo.delivered = True
            self.cargo = None
            self.target = None
            self.status = "idle"

    def is_active(self) -> bool:
        return self.battery > 0 and self.status != "dead"

    def is_moving(self) -> bool:
        """True while the drone is following a planned route."""
        return self.status == "moving"

    def is_available(self) -> bool:
        """True when the drone can be given a new task."""
        return self.is_active() and not self.is_moving()

    def has_low_battery(self) -> bool:
        return self.battery <= settings.LOW_BATTERY_THRESHOLD
