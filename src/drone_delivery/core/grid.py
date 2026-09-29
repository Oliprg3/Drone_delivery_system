"""The delivery grid and its static / dynamic obstacles."""

from __future__ import annotations

import random
from typing import List, Set, Tuple

import numpy as np

from drone_delivery.config import settings

Position = Tuple[int, int]

_ORTHOGONAL: Tuple[Position, ...] = ((-1, 0), (1, 0), (0, -1), (0, 1))
_DIAGONAL: Tuple[Position, ...] = ((-1, -1), (-1, 1), (1, -1), (1, 1))


class Grid:
    """A 2D grid where ``0`` marks free cells and ``1`` marks static obstacles.

    Dynamic obstacles are tracked separately in a set so that they can be added
    and removed without touching the numpy array.
    """

    def __init__(self) -> None:
        self.rows, self.cols = settings.GRID_SIZE
        self.grid = np.zeros((self.rows, self.cols), dtype=np.int8)
        self.dynamic_obstacles: Set[Position] = set()
        self.depot: Position = (0, 0)
        self._generate_static_obstacles()

    def _generate_static_obstacles(self) -> None:
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) == self.depot:
                    continue
                if random.random() < settings.OBSTACLE_DENSITY:
                    self.grid[r, c] = 1

    def add_dynamic_obstacle(self, pos: Position) -> None:
        if self.is_free(pos):
            self.dynamic_obstacles.add(pos)

    def remove_dynamic_obstacle(self, pos: Position) -> None:
        self.dynamic_obstacles.discard(pos)

    def is_free(self, pos: Position) -> bool:
        r, c = pos
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return False
        if self.grid[r, c] == 1:
            return False
        return pos not in self.dynamic_obstacles

    def get_neighbors(
        self, pos: Position, allow_diagonal: bool = True
    ) -> List[Position]:
        r, c = pos
        offsets = _ORTHOGONAL + _DIAGONAL if allow_diagonal else _ORTHOGONAL
        return [
            (r + dr, c + dc)
            for dr, dc in offsets
            if self.is_free((r + dr, c + dc))
        ]

    def free_cells(self) -> List[Position]:
        """All currently traversable cells, in row-major order."""
        return [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if self.is_free((r, c))
        ]

    def free_neighbours_of(self, pos: Position) -> List[Position]:
        """Free cells reachable in one orthogonal step, ordered closest first."""
        return self.get_neighbors(pos, allow_diagonal=False)
