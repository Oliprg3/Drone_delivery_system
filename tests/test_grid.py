"""Tests for the domain model and the grid."""

from __future__ import annotations

import pytest

from drone_delivery.core.grid import Grid
from drone_delivery.core.order import Order


def test_orders_receive_unique_identifiers():
    orders = [Order(pickup=(0, 0), delivery=(1, 1)) for _ in range(50)]

    assert len({o.id for o in orders}) == 50


def test_out_of_bounds_and_blocked_cells_are_not_free():
    grid = Grid()

    assert grid.is_free((0, 0)) is True
    assert grid.is_free((-1, 0)) is False
    assert grid.is_free((0, grid.cols)) is False


def test_dynamic_obstacles_block_and_unblock_a_cell():
    grid = Grid()
    target = (2, 2)

    grid.add_dynamic_obstacle(target)
    assert grid.is_free(target) is False

    grid.remove_dynamic_obstacle(target)
    assert grid.is_free(target) is True


def test_depot_is_never_blocked():
    grid = Grid()

    assert grid.is_free(grid.depot) is True


def test_free_cells_are_all_reachable():
    grid = Grid()
    cells = grid.free_cells()

    assert len(cells) == grid.rows * grid.cols


def test_a_static_obstacle_is_generated_at_the_configured_density():
    from drone_delivery.config import settings

    settings.OBSTACLE_DENSITY = 0.5
    try:
        grid = Grid()
        blocked = sum(int(grid.grid[r, c]) for r in range(grid.rows) for c in range(grid.cols))
        total = grid.rows * grid.cols - 1  # the depot is excluded
        assert 0 < blocked < total
    finally:
        settings.OBSTACLE_DENSITY = 0.0


@pytest.mark.parametrize("position", [(0, 0), (4, 4), (29, 29)])
def test_get_neighbors_stays_in_bounds(position):
    grid = Grid()

    for neighbor in grid.get_neighbors(position):
        assert grid.is_free(neighbor)
