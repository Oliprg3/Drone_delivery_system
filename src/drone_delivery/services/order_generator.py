"""Random generation of delivery orders on free cells."""

from __future__ import annotations

import random
from typing import Optional

from drone_delivery.core.grid import Grid, Position
from drone_delivery.core.order import Order

_MAX_ATTEMPTS = 1_000


class OrderGenerator:
    """Creates orders whose pickup and delivery points are both reachable."""

    def __init__(self, grid: Grid) -> None:
        self.grid = grid

    def generate_order(self) -> Order:
        """Build a new order.

        Raises:
            RuntimeError: if the grid is so congested that a free pickup and
                delivery point could not be found after many attempts.
        """
        pickup = self._random_free_pos()
        if pickup is None:
            raise RuntimeError("No free cell available for a pickup point")

        delivery = pickup
        for _ in range(_MAX_ATTEMPTS):
            candidate = self._random_free_pos()
            if candidate is not None and candidate != pickup:
                delivery = candidate
                break
        else:
            raise RuntimeError("No distinct free cell available for a delivery point")

        return Order(pickup=pickup, delivery=delivery)

    def _random_free_pos(self) -> Optional[Position]:
        free = self.grid.free_cells()
        if not free:
            return None
        return random.choice(free)
