"""Tests for the drone policies."""

from __future__ import annotations

from drone_delivery.agents.heuristic import HeuristicAgent
from drone_delivery.agents.random_walk import RandomAgent
from drone_delivery.core.order import Order
from drone_delivery.services.simulation import Simulation


def _run(sim: Simulation, agent, steps: int) -> None:
    for _ in range(steps):
        agent.act(sim.get_observation())
        sim.step()


def test_heuristic_agent_completes_deliveries(sim: Simulation):
    agent = HeuristicAgent(0, sim)

    _run(sim, agent, 300)

    assert len(sim.world.completed_orders) >= 1


def test_heuristic_agent_targets_the_nearest_pending_order(sim: Simulation):
    sim.world.clear_orders()
    near = Order(pickup=(0, 0), delivery=(5, 5))
    far = Order(pickup=(29, 29), delivery=(1, 1))
    sim.world.add_order(near)
    sim.world.add_order(far)
    sim.world.drones[0].position = (0, 0)

    HeuristicAgent(0, sim).act(sim.get_observation())

    assert sim.world.drones[0].target == near.pickup


def test_heuristic_agent_finishes_an_in_flight_delivery(sim: Simulation):
    sim.world.clear_orders()
    order = Order(pickup=(0, 0), delivery=(4, 0))
    sim.world.add_order(order)
    agent = HeuristicAgent(0, sim)

    _run(sim, agent, 40)

    assert order.delivered is True
    assert order in sim.world.completed_orders
    assert order not in sim.world.orders
    assert sim.world.drones[0].cargo is not order


def test_agents_ignore_a_drone_that_is_already_moving(sim: Simulation):
    drone = sim.world.drones[0]
    sim.assign_task_to_drone(0, (10, 10), [(1, 0)] * 5)
    drone.status = "moving"
    drone.target = None

    HeuristicAgent(0, sim).act(sim.get_observation())

    assert drone.target is None


def test_random_agent_never_assigns_a_job(sim: Simulation):
    sim.world.clear_orders()
    sim.world.add_order(Order(pickup=(0, 0), delivery=(5, 5)))
    agent = RandomAgent(0, sim)

    _run(sim, agent, 20)

    assert sim.world.completed_orders == []
    assert all(o.assigned_drone is None for o in sim.world.orders)


def test_heuristic_agent_is_idempotent_when_no_orders_exist(sim: Simulation):
    sim.world.clear_orders()
    drone = sim.world.drones[0]

    HeuristicAgent(0, sim).act(sim.get_observation())

    assert drone.target is None
    assert drone.status == "idle"
