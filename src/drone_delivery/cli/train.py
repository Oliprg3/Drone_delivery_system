"""``drone-train`` - train the PPO policy."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Optional, Sequence

from drone_delivery.config import settings


def _load_rl_stack() -> Any:
    """Import gymnasium, the environment and stable-baselines3.

    Raises:
        SystemExit: with installation instructions if the ``rl`` extra is
            missing, instead of a bare ``ModuleNotFoundError``.
    """
    try:
        from stable_baselines3 import PPO
        from stable_baselines3.common.env_checker import check_env

        from drone_delivery.rl.env import DroneEnv
    except ImportError as exc:  # pragma: no cover - depends on the environment
        raise SystemExit(
            "The reinforcement learning extra is not installed.\n"
            'Install it with:  pip install -e ".[rl]"'
        ) from exc
    return PPO, check_env, DroneEnv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="drone-train",
        description="Train a PPO policy on the drone delivery environment.",
    )
    parser.add_argument(
        "--timesteps",
        type=int,
        default=settings.RL_TOTAL_TIMESTEPS,
        help="total training timesteps (default: %(default)s)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(settings.RL_MODEL_PATH),
        help="path to save the model without extension (default: %(default)s)",
    )
    parser.add_argument("--seed", type=int, default=0, help="training seed")
    parser.add_argument(
        "--check-env",
        action="store_true",
        help="run the stable-baselines3 environment checker and exit",
    )
    return parser


def train(
    timesteps: int = settings.RL_TOTAL_TIMESTEPS,
    output: Optional[Path] = None,
    seed: int = 0,
) -> Path:
    """Train PPO and save the checkpoint, returning its path."""
    PPO, check_env, DroneEnv = _load_rl_stack()

    env = DroneEnv()
    check_env(env, warn=True)

    model = PPO("MlpPolicy", env, verbose=1, seed=seed)
    model.learn(total_timesteps=timesteps)

    destination = Path(output or settings.RL_MODEL_PATH)
    destination.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(destination))
    return destination


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    if args.check_env:
        _, check_env, DroneEnv = _load_rl_stack()

        check_env(DroneEnv(), warn=True)
        print("environment check passed")
        return 0

    saved = train(timesteps=args.timesteps, output=args.output, seed=args.seed)
    print(f"model saved to {saved}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
