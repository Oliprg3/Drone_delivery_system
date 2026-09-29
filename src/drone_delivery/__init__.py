"""Drone delivery system: a multi-agent drone delivery simulator.

The public API intentionally stays light so that importing the package does not
pull in optional heavy dependencies (FastAPI, pygame, stable-baselines3).
Those live in the :mod:`drone_delivery.api`, :mod:`drone_delivery.rendering` and
:mod:`drone_delivery.rl` subpackages and are imported on demand.
"""

__version__ = "1.0.0"

from drone_delivery.config import Settings, settings
from drone_delivery.core import Drone, Grid, Order, World
from drone_delivery.services import Simulation

__all__ = [
    "__version__",
    "Drone",
    "Grid",
    "Order",
    "Settings",
    "Simulation",
    "World",
    "settings",
]
