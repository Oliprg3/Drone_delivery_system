"""Pygame renderer for the simulated world."""

from __future__ import annotations

import pygame

from drone_delivery.config import settings
from drone_delivery.core.world import World

CELL_SIZE = 20

COLOR_BACKDROP = (255, 255, 255)
COLOR_FREE = (240, 240, 240)
COLOR_BLOCKED = (80, 80, 80)
COLOR_GRID_LINE = (180, 180, 180)
COLOR_PICKUP = (0, 200, 0)
COLOR_DELIVERY = (220, 0, 0)
COLOR_DRONE = (0, 0, 255)
COLOR_DRONE_LOW_BATTERY = (255, 165, 0)
COLOR_CARGO = (0, 0, 0)


class Renderer:
    """Draws the grid, the open orders and the fleet.

    The previous implementation never pumped the event queue, so the window
    could not be closed; :meth:`render` now returns ``False`` once the user
    asks to quit and callers are expected to stop their loop.
    """

    def __init__(self, cell_size: int = CELL_SIZE) -> None:
        pygame.init()
        self.cell_size = cell_size
        self.width = settings.GRID_SIZE[1] * cell_size
        self.height = settings.GRID_SIZE[0] * cell_size
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Drone Delivery System")
        self.clock = pygame.time.Clock()
        self.running = True

    def render(self, world: World) -> bool:
        """Draw one frame.

        Returns:
            ``False`` when the user asked to quit, ``True`` otherwise.
        """
        if not self.running:
            return False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False

        self.screen.fill(COLOR_BACKDROP)
        self._draw_grid(world)
        self._draw_orders(world)
        self._draw_drones(world)

        pygame.display.flip()
        self.clock.tick(settings.RENDER_FPS)
        return True

    def _draw_grid(self, world: World) -> None:
        grid = world.grid
        for r in range(grid.rows):
            for c in range(grid.cols):
                rect = pygame.Rect(
                    c * self.cell_size, r * self.cell_size, self.cell_size, self.cell_size
                )
                color = COLOR_FREE if grid.is_free((r, c)) else COLOR_BLOCKED
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, COLOR_GRID_LINE, rect, 1)

    def _draw_orders(self, world: World) -> None:
        for order in world.orders:
            if order.is_pending():
                self._draw_marker(order.pickup, COLOR_PICKUP, radius=6)
            elif order.is_in_transit():
                self._draw_marker(order.delivery, COLOR_DELIVERY, radius=6)

    def _draw_drones(self, world: World) -> None:
        for drone in world.drones:
            color = COLOR_DRONE_LOW_BATTERY if drone.has_low_battery() else COLOR_DRONE
            self._draw_marker(drone.position, color, radius=8)
            if drone.cargo is not None:
                centre = self._to_pixels(drone.position)
                pygame.draw.circle(
                    self.screen, COLOR_CARGO, (centre[0] - 3, centre[1] - 3), 3
                )

    def _draw_marker(self, position, color: tuple, radius: int) -> None:
        pygame.draw.circle(self.screen, color, self._to_pixels(position), radius)

    def _to_pixels(self, position) -> tuple:
        row, col = position
        return (
            col * self.cell_size + self.cell_size // 2,
            row * self.cell_size + self.cell_size // 2,
        )

    def close(self) -> None:
        self.running = False
        pygame.quit()
