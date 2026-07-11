import pytest
from services.simulation import Simulation

@pytest.fixture
def sim():
    return Simulation()
