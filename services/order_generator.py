import random
from typing import Tuple, List
from core.grid import Grid
from core.order import Order

class OrderGenerator:
    def __init__(self, grid: Grid):
        self.grid = grid

    def generate_order(self) -> Order:
        pickup = self._random_free_pos()
        delivery = self._random_free_pos()
        while delivery == pickup:
            delivery = self._random_free_pos()
        return Order(pickup, delivery)

    def _random_free_pos(self) -> Tuple[int, int]:
        while True:
            r = random.randint(0, self.grid.rows-1)
            c = random.randint(0, self.grid.cols-1)
            if self.grid.is_free((r,c)):
                return (r,c)
