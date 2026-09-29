"""A delivery order moving through the system."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, Tuple

if TYPE_CHECKING:  # pragma: no cover - import cycle guard
    from drone_delivery.core.drone import Drone

Position = Tuple[int, int]


def _new_order_id() -> str:
    return uuid.uuid4().hex[:8]


@dataclass
class Order:
    """A parcel that has to be picked up at ``pickup`` and dropped at ``delivery``.

    The identifier is produced by a factory rather than a plain default so that
    every instance receives a unique value (a plain default is evaluated once,
    at class definition time, and would be shared by all orders).
    """

    pickup: Position
    delivery: Position
    id: str = field(default_factory=_new_order_id)
    picked_up: bool = False
    delivered: bool = False
    assigned_drone: Optional["Drone"] = None
    waiting_steps: int = 0

    def is_pending(self) -> bool:
        """True while the order still waits for a drone."""
        return not self.picked_up and not self.delivered

    def is_in_transit(self) -> bool:
        """True while the order is being carried to its destination."""
        return self.picked_up and not self.delivered
