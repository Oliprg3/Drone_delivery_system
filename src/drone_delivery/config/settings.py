"""Application settings, loaded from the environment or a local ``.env`` file."""

from __future__ import annotations

from typing import Tuple

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the drone delivery simulator.

    Every field can be overridden through an environment variable of the same
    name or an entry in a local ``.env`` file. See ``.env.example``.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # -- World ---------------------------------------------------------------
    GRID_SIZE: Tuple[int, int] = (30, 30)
    OBSTACLE_DENSITY: float = 0.15

    # -- Fleet ---------------------------------------------------------------
    NUM_DRONES: int = 5
    MAX_BATTERY: float = 100.0
    BATTERY_DRAIN_PER_STEP: float = 0.5
    LOW_BATTERY_THRESHOLD: float = 30.0

    # -- Orders --------------------------------------------------------------
    ORDER_FREQUENCY: float = 0.3
    MAX_ACTIVE_ORDERS: int = 30
    ORDER_EXPIRY_STEPS: int = 200

    # -- Weather -------------------------------------------------------------
    WEATHER_EVENT_PROBABILITY: float = 0.1
    WEATHER_BATTERY_PENALTY: float = 0.5

    # -- Rewards -------------------------------------------------------------
    DELIVERY_REWARD: float = 10.0
    ORDER_TIMEOUT_PENALTY: float = -2.0

    # -- Simulation ----------------------------------------------------------
    MAX_STEPS: int = 10_000
    VISUALIZE: bool = False
    API_ENABLED: bool = False
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # -- Reinforcement learning ---------------------------------------------
    RL_MODEL_PATH: str = "artifacts/drone_ppo"
    RL_TOTAL_TIMESTEPS: int = 10_000
    RL_OBSERVATION_SIZE: int = 0  # 0 = derive from the fleet size

    # -- Observability -------------------------------------------------------
    LOG_LEVEL: str = "INFO"
    RENDER_FPS: int = Field(default=30, ge=1)


settings = Settings()

__all__ = ["Settings", "settings"]
