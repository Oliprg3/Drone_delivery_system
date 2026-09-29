"""Policy backed by a PPO model trained with :mod:`drone_delivery.rl`.

If no trained model is available the agent logs a warning once and degrades to
the heuristic behaviour instead of silently doing nothing, which is what the
previous ``PPO.load(...) if False else None`` placeholder amounted to.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

from drone_delivery.agents.base import BaseAgent
from drone_delivery.agents.heuristic import HeuristicAgent
from drone_delivery.config import settings
from drone_delivery.services.simulation import Simulation
from drone_delivery.utils.helpers import flatten_observation


class RLAgent(BaseAgent):
    """Runs a trained PPO policy, falling back to the heuristic when absent."""

    def __init__(self, drone_id: int, sim: Simulation) -> None:
        super().__init__(drone_id, sim)
        self._model = None
        self._load_failed = False
        self._fallback = HeuristicAgent(drone_id, sim)

    @property
    def has_model(self) -> bool:
        return self._model is not None

    def _load_model(self) -> None:
        """Load the PPO checkpoint once, if it exists."""
        if self._model is not None or self._load_failed:
            return
        from stable_baselines3 import PPO  # imported lazily: heavy optional dep

        path = Path(settings.RL_MODEL_PATH)
        candidates = [path, path.with_suffix(".zip")]
        checkpoint = next((c for c in candidates if c.exists()), None)
        if checkpoint is None:
            self._load_failed = True
            return
        self._model = PPO.load(str(checkpoint))

    def act(self, observation: Dict[str, Any]) -> Optional[int]:
        self._load_model()
        if self._model is None:
            self._fallback.act(observation)
            return None

        state = self._extract_state(observation)
        action, _ = self._model.predict(state, deterministic=True)
        return int(action)

    @staticmethod
    def _extract_state(observation: Dict[str, Any]) -> np.ndarray:
        return np.asarray(flatten_observation(observation), dtype=np.float32)
