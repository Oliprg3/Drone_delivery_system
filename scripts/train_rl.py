import gymnasium as gym
from gymnasium import spaces
import numpy as np
from services.simulation import Simulation
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env

class DroneEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.sim = Simulation()
        self.action_space = spaces.Discrete(5)  
        self.observation_space = spaces.Box(low=0, high=1, shape=(10,), dtype=np.float32)

    def reset(self, seed=None, options=None):
        obs = self.sim.reset()
        return self._flatten(obs), {}

    def step(self, action):
        self.sim.step([action] * len(self.sim.world.drones))
        obs = self.sim._get_observation()
        reward = self.sim.world.total_reward
        done = self.sim.done
        return self._flatten(obs), reward, done, False, {}

    def _flatten(self, obs):
        flat = []
        for d_pos in obs["drones"]:
            flat.extend(d_pos)
        for b in obs["batteries"]:
            flat.append(b/100.0)
        while len(flat) < 10:
            flat.append(0.0)
        return np.array(flat[:10], dtype=np.float32)

if __name__ == "__main__":
    env = DroneEnv()
    check_env(env)
    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=10000)
    model.save("drone_ppo")
