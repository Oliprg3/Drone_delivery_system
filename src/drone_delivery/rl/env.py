"""Gymnasium wrapper exposing the simulation to stable-baselines3."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from drone_delivery.services.simulation import Simulation
from drone_delivery.utils.helpers import observation_size

#: Discrete action space consumed by the learned policy.
NUM_ACTIONS = 5


class DroneEnv(gym.Env):
    """Single-drone view of :class:`Simulation` for PPO training.

    The observation space is derived from ``NUM_DRONES`` instead of being
    hard-coded to 10 floats, so changing the fleet size no longer makes the
    environment invalid.
    """

    metadata = {"render_modes": []}

    def __init__(self) -> None:
        super().__init__()
        self.sim = Simulation()
        self.action_space = spaces.Discrete(NUM_ACTIONS)
        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(observation_size(),),
            dtype=np.float32,
        )

    def reset(
        self,
        *,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        super().reset(seed=seed)
        observation = self.sim.reset()
        return self._flatten(observation), {}

    def step(
        self, action: Any
    ) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        observation, reward, done, info = self.sim.step([action])
        truncated = False  # the simulation only ever terminates, never truncates
        return self._flatten(observation), reward, done, truncated, info

    def render(self) -> None:  # pragma: no cover - training is headless
        pass

    @staticmethod
    def _flatten(observation: Dict[str, Any]) -> np.ndarray:
        from drone_delivery.utils.helpers import flatten_observation

        return np.asarray(flatten_observation(observation), dtype=np.float32)
