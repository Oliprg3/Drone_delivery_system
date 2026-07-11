from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Tuple

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    GRID_SIZE: Tuple[int, int] = (30, 30)
    OBSTACLE_DENSITY: float = 0.15
    NUM_DRONES: int = 5
    MAX_BATTERY: float = 100.0
    BATTERY_DRAIN_PER_STEP: float = 0.5
    ORDER_FREQUENCY: float = 0.3
    MAX_ACTIVE_ORDERS: int = 30
    MAX_STEPS: int = 10000
    VISUALIZE: bool = False
    API_ENABLED: bool = False
    LOG_LEVEL: str = "INFO"

settings = Settings()
