"""Tests for the :class:`Drone` entity."""

from __future__ import annotations

from drone_delivery.config import settings
from drone_delivery.core.drone import Drone
from drone_delivery.core.order import Order


def test_move_along_path_advances_and_drains_battery():
    drone = Drone(id=0, position=(0, 0))
    drone.assign_task(target=(2, 0), path=[(1, 0), (2, 0)])

    drone.move_along_path()

    assert drone.position == (1, 0)
    assert drone.battery < settings.MAX_BATTERY
    assert drone.status == "moving"


def test_status_returns_to_idle_when_route_finishes():
    drone = Drone(id=0, position=(0, 0))
    drone.assign_task(target=(1, 0), path=[(1, 0)])

    drone.move_along_path()

    assert drone.status == "idle"
    assert drone.path == []


def test_battery_exhaustion_marks_drone_dead():
    drone = Drone(id=0, position=(0, 0), battery=settings.BATTERY_DRAIN_PER_STEP)
    drone.assign_task(target=(1, 0), path=[(1, 0)])

    drone.move_along_path()

    assert drone.battery == 0.0
    assert drone.status == "dead"
    assert not drone.is_active()


def test_pickup_then_delivery_updates_the_order():
    drone = Drone(id=0, position=(0, 0))
    order = Order(pickup=(0, 0), delivery=(5, 5))

    drone.pick_cargo(order)
    assert order.picked_up is True
    assert order.assigned_drone is drone
    assert drone.status == "delivering"

    drone.deliver_cargo()
    assert order.delivered is True
    assert drone.cargo is None
    assert drone.status == "idle"


def test_assign_task_copies_the_route():
    drone = Drone(id=0, position=(0, 0))
    route = [(1, 0), (2, 0)]

    drone.assign_task(target=(2, 0), path=route)
    drone.path.clear()

    assert drone.path == []
    assert route == [(1, 0), (2, 0)]


def test_a_delivering_drone_can_still_be_replanned():
    drone = Drone(id=0, position=(2, 0))
    order = Order(pickup=(2, 0), delivery=(5, 0))
    drone.pick_cargo(order)

    assert drone.status == "delivering"
    assert drone.is_available() is True

    drone.assign_task(target=(5, 0), path=[(3, 0)])
    assert drone.status == "moving"
    assert drone.is_available() is False


def test_empty_route_does_not_leave_the_drone_stuck_moving():
    drone = Drone(id=0, position=(1, 1))

    drone.assign_task(target=(1, 1), path=[])

    assert drone.status == "idle"
    assert drone.is_available() is True


def test_moving_with_an_empty_path_returns_to_rest():
    drone = Drone(id=0, position=(1, 1))
    drone.status = "moving"

    drone.move_along_path()

    assert drone.status == "idle"
