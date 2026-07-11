import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from gymnasium import Env
from .base import BaseAgent
from typing import Dict

class RLAgent(BaseAgent):
    def __init__(self, drone_id: int, sim: "Simulation"):
        super().__init__(drone_id, sim)
        self.model = PPO.load("drone_ppo.zip") if False else None
    def act(self, observation: Dict) -> int:
        state = self._extract_state(observation)
        if self.model:
            action, _ = self.model.predict(state, deterministic=True)
            return int(action)
        else:
            return 0  

    def _extract_state(self, obs: Dict) -> np.ndarray:
        return np.array([0.0]*10)
