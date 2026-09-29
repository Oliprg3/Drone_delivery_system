"""``drone-sim`` - run the simulator from the command line."""

from __future__ import annotations

import argparse
import random
import sys
from typing import List, Optional, Sequence

from drone_delivery.agents.base import BaseAgent
from drone_delivery.config import settings
from drone_delivery.services.simulation import Simulation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="drone-sim",
        description="Run the multi-agent drone delivery simulation.",
    )
    parser.add_argument(
        "--agent",
        choices=("heuristic", "random", "rl"),
        default="heuristic",
        help="policy driving the fleet (default: heuristic)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="run without opening a window",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=settings.MAX_STEPS,
        help="maximum number of simulation steps (default: %(default)s)",
    )
    parser.add_argument(
        "--seed", type=int, default=None, help="seed the RNG for reproducible runs"
    )
    return parser


def run(
    policy: str = "heuristic",
    headless: bool = True,
    max_steps: Optional[int] = None,
    seed: Optional[int] = None,
) -> dict:
    """Execute a full simulation and return a summary dict.

    The policy modules are imported lazily because ``rl`` pulls in
    stable-baselines3, which is not needed for the other two policies.
    """
    if seed is not None:
        random.seed(seed)

    sim = Simulation()
    agents: List[BaseAgent] = []
    for drone_id in range(len(sim.world.drones)):
        agents.append(_make_agent(policy, drone_id, sim))

    renderer = None
    if not headless:
        from drone_delivery.rendering import Renderer

        renderer = Renderer()

    limit = max_steps if max_steps is not None else settings.MAX_STEPS
    observation = sim.get_observation()
    for _ in range(limit):
        for agent in agents:
            agent.act(observation)
        observation, _, done, _ = sim.step()
        if renderer is not None and not renderer.render(sim.world):
            break
        if done:
            break

    if renderer is not None:
        renderer.close()

    return {
        "policy": policy,
        "steps": sim.step_count,
        "deliveries": len(sim.world.completed_orders),
        "total_reward": sim.world.total_reward,
        "alive": len(sim.world.active_drones()),
    }


def _make_agent(policy: str, drone_id: int, sim: Simulation) -> BaseAgent:
    if policy == "heuristic":
        from drone_delivery.agents.heuristic import HeuristicAgent

        return HeuristicAgent(drone_id, sim)
    if policy == "random":
        from drone_delivery.agents.random_walk import RandomAgent

        return RandomAgent(drone_id, sim)
    from drone_delivery.agents.ppo import RLAgent

    return RLAgent(drone_id, sim)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    summary = run(
        policy=args.agent,
        headless=args.headless,
        max_steps=args.max_steps,
        seed=args.seed,
    )
    print(
        f"policy={summary['policy']} steps={summary['steps']} "
        f"deliveries={summary['deliveries']} reward={summary['total_reward']:.1f} "
        f"alive={summary['alive']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
