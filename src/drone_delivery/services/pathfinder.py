"""A* pathfinding over the delivery grid."""

from __future__ import annotations

import heapq
from typing import Dict, List, Optional

from drone_delivery.core.grid import Grid, Position


def manhattan(a: Position, b: Position) -> int:
    """Admissible heuristic for 4-connected grid movement."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


class Pathfinder:
    """Orthogonal A* planner."""

    def __init__(self, grid: Grid) -> None:
        self.grid = grid

    def find_path(
        self, start: Position, goal: Position
    ) -> Optional[List[Position]]:
        """Return the cells to walk from ``start`` to ``goal`` (exclusive).

        ``None`` is returned when either endpoint is blocked or no route
        exists. The start cell itself is not part of the result, so a drone
        already standing on the goal gets an empty list.
        """
        if not self.grid.is_free(start) or not self.grid.is_free(goal):
            return None
        if start == goal:
            return []

        open_set: List[tuple[int, Position]] = [(manhattan(start, goal), start)]
        came_from: Dict[Position, Position] = {}
        g_score: Dict[Position, int] = {start: 0}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                return self._reconstruct_path(came_from, current)

            for neighbor in self.grid.get_neighbors(
                current, allow_diagonal=False
            ):
                tentative_g = g_score[current] + 1
                if tentative_g < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    priority = tentative_g + manhattan(neighbor, goal)
                    heapq.heappush(open_set, (priority, neighbor))

        return None

    @staticmethod
    def _reconstruct_path(
        came_from: Dict[Position, Position], current: Position
    ) -> List[Position]:
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path[1:]
