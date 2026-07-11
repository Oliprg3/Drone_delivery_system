from core.drone import Drone

def test_drone_move():
    d = Drone(0, (0,0))
    d.assign_task((2,0), [(1,0),(2,0)])
    d.move_along_path()
    assert d.position == (1,0)
    assert d.battery < 100
