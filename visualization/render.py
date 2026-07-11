import pygame
import sys
from config import settings
from core.world import World

class Renderer:
    def __init__(self):
        pygame.init()
        self.cell_size = 20
        self.width = settings.GRID_SIZE[1] * self.cell_size
        self.height = settings.GRID_SIZE[0] * self.cell_size
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Drone Delivery")
        self.clock = pygame.time.Clock()

    def render(self, world: World):
        self.screen.fill((255,255,255))
        grid = world.grid
        for r in range(grid.rows):
            for c in range(grid.cols):
                color = (240,240,240) if grid.is_free((r,c)) else (80,80,80)
                pygame.draw.rect(self.screen, color, (c*self.cell_size, r*self.cell_size, self.cell_size, self.cell_size))
                pygame.draw.rect(self.screen, (180,180,180), (c*self.cell_size, r*self.cell_size, self.cell_size, self.cell_size), 1)

        for o in world.orders:
            if not o.picked_up:
                pygame.draw.circle(self.screen, (0,255,0), (o.pickup[1]*self.cell_size+self.cell_size//2, o.pickup[0]*self.cell_size+self.cell_size//2), 6)
            if o.picked_up and not o.delivered:
                pygame.draw.circle(self.screen, (255,0,0), (o.delivery[1]*self.cell_size+self.cell_size//2, o.delivery[0]*self.cell_size+self.cell_size//2), 6)

        for d in world.drones:
            color = (0,0,255) if d.battery > 30 else (255,165,0)
            pygame.draw.circle(self.screen, color, (d.position[1]*self.cell_size+self.cell_size//2, d.position[0]*self.cell_size+self.cell_size//2), 8)
            if d.cargo:
                pygame.draw.circle(self.screen, (0,0,0), (d.position[1]*self.cell_size+self.cell_size//2-3, d.position[0]*self.cell_size+self.cell_size//2-3), 3)

        pygame.display.flip()
        self.clock.tick(30)

    def close(self):
        pygame.quit()
