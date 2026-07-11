from dataclasses import dataclass
from typing import Optional, Tuple
import uuid

@dataclass
class Order:
    pickup: Tuple[int, int]
    delivery: Tuple[int, int]
    id: str = uuid.uuid4().hex[:8]
    picked_up: bool = False
    delivered: bool = False
    assigned_drone: Optional["Drone"] = None
    waiting_steps: int = 0
