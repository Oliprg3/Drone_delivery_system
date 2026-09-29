"""End-to-end tests for the simulation loop."""

from __future__ import annotations

from drone_delivery.config import settings
from drone_delivery.core.order import Order
from drone_delivery.services.simulation import Simulation


def test_drones_spawn_on_distinct_cells(sim: Simulation):
    positions = [d.position for d in sim.world.drones]

    assert len(positions) == settings.NUM_DRONES
    assert len(set(positions)) == settings.NUM_DRONES
    assert all(sim.world.grid.is_free(p) for p in positions)


def test_reset_rebuilds_the_world(sim: Simulation):
    sim.step()
    sim.reset()

    assert sim.step_count == 0
    assert sim.done is False
    assert sim.world.total_reward == 0.0
    assert len(sim.world.drones) == settings.NUM_DRONES


def test_step_advances_and_reports_progress(sim: Simulation):
    _, reward, done, info = sim.step()

    assert sim.step_count == 1
    assert info["step"] == 1
    assert isinstance(reward, float)
    assert done is (sim.step_count >= settings.MAX_STEPS)


def test_step_reward_is_incremental(sim: Simulation):
    sim.world.add_order(Order(pickup=(0, 0), delivery=(2, 0)))
    drone = sim.world.drones[0]
    drone.position = (0, 0)
    sim.assign_task_to_drone(0, (0, 0), [])

    sim.step()  # pickup happens here, no reward yet
    _, reward, _, _ = sim.step()
    _, next_reward, _, _ = sim.step()

    assert sim.world.total_reward == 0.0
    assert reward == 0.0
    assert next_reward == 0.0


def test_a_pickup_then_delivery_scores_and_completes_the_order(sim: Simulation):
    sim.world.clear_orders()
    order = Order(pickup=(0, 0), delivery=(3, 0))
    sim.world.add_order(order)

    drone = sim.world.drones[0]
    drone.position = (0, 0)
    sim.assign_task_to_drone(0, (0, 0), sim.get_path((0, 0), (0, 0)))
    sim.step()

    assert order.picked_up is True
    assert drone.cargo is order

    sim.assign_task_to_drone(0, (3, 0), sim.get_path(drone.position, (3, 0)))
    for _ in range(5):
        sim.step()

    assert order.delivered is True
    assert order in sim.world.completed_orders
    assert order not in sim.world.orders
    assert sim.world.total_reward == settings.DELIVERY_REWARD
    assert drone.target is None
    assert drone.status == "idle"


def test_orders_expire_after_the_configured_wait(sim: Simulation):
    sim.world.clear_orders()
    order = Order(pickup=(10, 10), delivery=(12, 12))
    sim.world.add_order(order)

    for _ in range(settings.ORDER_EXPIRY_STEPS + 1):
        sim.step()

    assert order not in sim.world.orders
    assert sim.world.total_reward < 0


def test_observation_reports_the_whole_fleet(sim: Simulation):
    observation = sim.get_observation()

    assert len(observation["drones"]) == settings.NUM_DRONES
    assert len(observation["batteries"]) == settings.NUM_DRONES
    assert len(observation["cargos"]) == settings.NUM_DRONES
    assert set(observation) == {"drones", "batteries", "cargos", "pickups", "deliveries"}


def test_dead_drones_stop_moving(sim: Simulation):
    drone = sim.world.drones[0]
    drone.battery = 0.0
    drone.status = "dead"
    before = drone.position

    sim.step()

    assert drone.position == before
    assert drone.is_active() is False


def test_max_steps_terminates_the_episode(sim: Simulation, monkeypatch):
    monkeypatch.setattr(settings, "MAX_STEPS", 3)

    for _ in range(3):
        _, _, done, _ = sim.step()

    assert sim.done is True


def test_several_simulations_can_coexist(sim: Simulation):
    """Regression: Prometheus collectors used to clash on the second instance."""
    second = Simulation()

    assert second.get_observation()["drones"]
