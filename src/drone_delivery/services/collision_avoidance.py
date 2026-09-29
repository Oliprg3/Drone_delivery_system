"""Cooperative separation between drones sharing a cell."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from drone_delivery.core.drone import Drone
from drone_delivery.core.grid import Grid, Position


class CollisionAvoidance:
    """Resolves overlapping drones by nudging them to a free neighbour cell.

    The low-id drone of a colliding pair keeps its cell; the others are moved,
    which keeps the outcome deterministic and prevents two drones from being
    pushed into the same escape cell.
    """

    def __init__(self, grid: Grid) -> None:
        self.grid = grid

    def resolve_conflicts(self, drones: List[Drone]) -> int:
        """Separate every group of drones standing on the same cell.

        Returns:
            The number of drones that had to be relocated.
        """
        by_position: Dict[Position, List[Drone]] = defaultdict(list)
        for drone in drones:
            if drone.is_active():
                by_position[drone.position].append(drone)

        moved = 0
        for group in by_position.values():
            if len(group) < 2:
                continue
            occupied = {d.position for d in drones if d.is_active()}
            for drone in group[1:]:
                escape = self._find_escape(drone, occupied)
                if escape is not None:
                    occupied.discard(drone.position)
                    occupied.add(escape)
                    drone.position = escape
                    moved += 1
        return moved

    def _find_escape(
        self, drone: Drone, occupied: set
    ) -> Position | None:
        for candidate in self.grid.free_neighbours_of(drone.position):
            if candidate not in occupied:
                return candidate
        return None
