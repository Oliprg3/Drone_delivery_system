from core.grid import Grid
from services.pathfinder import Pathfinder

def test_pathfinder():
    grid = Grid()
    pf = Pathfinder(grid)
    path = pf.find_path((0,0), (5,5))
    assert path is not None
