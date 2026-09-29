"""Shared pytest fixtures."""

from __future__ import annotations

import random

import pytest

from drone_delivery.config import settings
from drone_delivery.services.simulation import Simulation


@pytest.fixture(autouse=True)
def deterministic_world():
    """Seed the RNG and pin the grid so tests never depend on map generation."""
    random.seed(1234)
    previous = (settings.OBSTACLE_DENSITY, settings.NUM_DRONES)
    settings.OBSTACLE_DENSITY = 0.0  # keep the grid empty and fully connected
    settings.NUM_DRONES = 3
    yield
    settings.OBSTACLE_DENSITY, settings.NUM_DRONES = previous


@pytest.fixture
def sim() -> Simulation:
    return Simulation()
