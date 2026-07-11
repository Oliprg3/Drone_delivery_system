from typing import List, Tuple, Set
from core.drone import Drone
from core.grid import Grid

class CollisionAvoidance:
    def __init__(self, grid: Grid):
        self.grid = grid

    def resolve_conflicts(self, drones: List[Drone]) -> None:
        positions = [d.position for d in drones if d.is_active()]
        conflict_positions = {pos for pos in positions if positions.count(pos) > 1}

        for drone in drones:
            if drone.position in conflict_positions:
                # simple evasion: move to a nearby free cell
                for neighbor in self.grid.get_neighbors(drone.position, allow_diagonal=False):
                    if all(d.position != neighbor for d in drones if d is not drone):
                        drone.position = neighbor
                        break
