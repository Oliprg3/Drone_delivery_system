"""Prometheus instrumentation for the simulation.

The collectors are module-level singletons backed by a private registry. This
matters: ``prometheus_client`` raises ``Duplicated timeseries`` when the same
metric name is registered twice, so building several :class:`Simulation`
objects (as the test suite does) would crash if the collectors were created in
``Metrics.__init__``.
"""

from __future__ import annotations

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

from drone_delivery.core.world import World

REGISTRY = CollectorRegistry()

deliveries_total = Counter(
    "drone_deliveries_total",
    "Total number of completed deliveries.",
    registry=REGISTRY,
)
active_orders = Gauge(
    "drone_active_orders",
    "Number of orders currently in the order book.",
    registry=REGISTRY,
)
orders_expired_total = Counter(
    "drone_orders_expired_total",
    "Total number of orders dropped after expiring.",
    registry=REGISTRY,
)
drone_battery = Gauge(
    "drone_battery",
    "Remaining battery of a drone.",
    ["drone_id"],
    registry=REGISTRY,
)
active_drones = Gauge(
    "drone_active_drones",
    "Number of drones still able to fly.",
    registry=REGISTRY,
)
step_duration = Histogram(
    "simulation_step_duration",
    "Wall-clock duration of a simulation step in seconds.",
    registry=REGISTRY,
)


class Metrics:
    """Records world state into the Prometheus collectors above."""

    def record_delivery(self, order_id: str) -> None:
        deliveries_total.inc()
        active_orders.dec()

    def record_expiry(self) -> None:
        orders_expired_total.inc()
        active_orders.dec()

    def record(self, world: World) -> None:
        active_orders.set(len(world.orders))
        active_drones.set(len(world.active_drones()))
        for drone in world.drones:
            drone_battery.labels(drone_id=str(drone.id)).set(drone.battery)

    def observe_step(self, seconds: float) -> None:
        step_duration.observe(seconds)


def render_latest() -> bytes:
    """Serialise the registry in the Prometheus text exposition format."""
    from prometheus_client import generate_latest

    return generate_latest(REGISTRY)
