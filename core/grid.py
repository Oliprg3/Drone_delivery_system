import numpy as np
import random
from typing import List, Tuple, Set
from config import settings

class Grid:
    def __init__(self):
        self.rows, self.cols = settings.GRID_SIZE
        self.grid = np.zeros((self.rows, self.cols), dtype=np.int8)
        self.dynamic_obstacles: Set[Tuple[int, int]] = set()
        self._generate_static_obstacles()

    def _generate_static_obstacles(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) in [(0,0), (self.rows-1, self.cols-1)]:
                    continue
                if random.random() < settings.OBSTACLE_DENSITY:
                    self.grid[r, c] = 1  # obstacle

    def add_dynamic_obstacle(self, pos: Tuple[int, int]):
        if self.is_free(pos):
            self.dynamic_obstacles.add(pos)

    def remove_dynamic_obstacle(self, pos: Tuple[int, int]):
        self.dynamic_obstacles.discard(pos)

    def is_free(self, pos: Tuple[int, int]) -> bool:
        r, c = pos
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return False
        if self.grid[r, c] == 1:
            return False
        if pos in self.dynamic_obstacles:
            return False
        return True

    def get_neighbors(self, pos: Tuple[int, int], allow_diagonal: bool = True) -> List[Tuple[int, int]]:
        r, c = pos
        dirs = [(-1,0),(1,0),(0,-1),(0,1)]
        if allow_diagonal:
            dirs += [(-1,-1),(-1,1),(1,-1),(1,1)]
        return [ (r+dr, c+dc) for dr, dc in dirs if self.is_free((r+dr, c+dc)) ]
