from prometheus_client import Counter, Gauge, Histogram
from core.world import World

class Metrics:
    def __init__(self):
        self.deliveries_total = Counter("drone_deliveries_total", "Total deliveries")
        self.active_orders = Gauge("drone_active_orders", "Active orders")
        self.drone_battery = Gauge("drone_battery", "Drone battery", ["drone_id"])
        self.step_duration = Histogram("simulation_step_duration", "Step duration")

    def record(self, world: World):
        self.active_orders.set(len(world.orders))
        for d in world.drones:
            self.drone_battery.labels(drone_id=str(d.id)).set(d.battery)
