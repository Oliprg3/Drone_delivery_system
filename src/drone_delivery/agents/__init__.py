"""Drone policies.

All three policies are importable without stable-baselines3: the PPO policy
loads its checkpoint lazily, on the first tick that needs it.
"""

from drone_delivery.agents.base import BaseAgent
from drone_delivery.agents.heuristic import HeuristicAgent
from drone_delivery.agents.ppo import RLAgent
from drone_delivery.agents.random_walk import RandomAgent

#: Policies selectable from the command line, keyed by ``--agent``.
POLICIES = {
    "heuristic": HeuristicAgent,
    "random": RandomAgent,
    "rl": RLAgent,
}

__all__ = ["BaseAgent", "HeuristicAgent", "POLICIES", "RLAgent", "RandomAgent"]
