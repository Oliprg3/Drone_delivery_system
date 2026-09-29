"""Tests for A* pathfinding and the supporting services."""

from __future__ import annotations

from drone_delivery.core.drone import Drone
from drone_delivery.core.grid import Grid
from drone_delivery.services.collision_avoidance import CollisionAvoidance
from drone_delivery.services.order_generator import OrderGenerator
from drone_delivery.services.pathfinder import Pathfinder


def test_pathfinder_finds_a_route_on_an_open_grid():
    grid = Grid()
    path = Pathfinder(grid).find_path((0, 0), (5, 5))

    assert path is not None
    assert path  # non-empty
    assert path[-1] == (5, 5)
    assert (0, 0) not in path  # the start cell is excluded


def test_path_to_self_is_empty():
    grid = Grid()

    assert Pathfinder(grid).find_path((3, 3), (3, 3)) == []


def test_pathfinder_returns_none_for_a_blocked_goal():
    grid = Grid()
    grid.add_dynamic_obstacle((5, 5))

    assert Pathfinder(grid).find_path((0, 0), (5, 5)) is None


def test_pathfinder_returns_none_when_the_goal_is_unreachable():
    grid = Grid()
    # Wall off the goal completely.
    for neighbor in [(4, 5), (6, 5), (5, 4), (5, 6)]:
        grid.add_dynamic_obstacle(neighbor)

    assert Pathfinder(grid).find_path((0, 0), (5, 5)) is None


def test_path_is_contiguous():
    grid = Grid()
    path = Pathfinder(grid).find_path((0, 0), (6, 4))

    assert path is not None
    cursor = (0, 0)
    for cell in path:
        assert abs(cell[0] - cursor[0]) + abs(cell[1] - cursor[1]) == 1
        cursor = cell


def test_order_generator_endpoints_are_free_and_distinct():
    grid = Grid()

    order = OrderGenerator(grid).generate_order()

    assert grid.is_free(order.pickup)
    assert grid.is_free(order.delivery)
    assert order.pickup != order.delivery
    assert order.is_pending()


def test_collision_avoidance_separates_overlapping_drones():
    grid = Grid()
    drones = [Drone(id=i, position=(4, 4)) for i in range(3)]

    moved = CollisionAvoidance(grid).resolve_conflicts(drones)

    assert moved == 2
    assert len({d.position for d in drones}) == 3


def test_collision_avoidance_leaves_unique_drones_alone():
    grid = Grid()
    drones = [Drone(id=0, position=(0, 0)), Drone(id=1, position=(0, 1))]

    assert CollisionAvoidance(grid).resolve_conflicts(drones) == 0
    assert [d.position for d in drones] == [(0, 0), (0, 1)]
