"""Small, dependency-free helpers shared across the package."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Sequence

from drone_delivery.config import settings

# Number of features emitted per drone by :func:`flatten_observation`.
FEATURES_PER_DRONE = 4


def flatten(lists: Iterable[Sequence[Any]]) -> List[Any]:
    """Flatten one level of nesting: ``[[1, 2], [3]]`` -> ``[1, 2, 3]``."""
    return [item for sublist in lists for item in sublist]


def observation_size(num_drones: int | None = None) -> int:
    """Size of the flat vector produced by :func:`flatten_observation`."""
    return (num_drones or settings.NUM_DRONES) * FEATURES_PER_DRONE


def flatten_observation(observation: Dict[str, Any]) -> List[float]:
    """Turn a simulation observation into a fixed-length numeric vector.

    Every value is normalised to roughly ``[0, 1]`` so it can be fed straight
    into a neural network. The layout is, per drone:
    ``row``, ``col``, ``battery fraction``, ``carrying flag``.

    Unlike the previous implementation this never truncates: the vector always
    has exactly :func:`observation_size` entries, so changing ``NUM_DRONES``
    no longer silently drops the tail of the state.
    """
    rows = float(settings.GRID_SIZE[0] or 1)
    cols = float(settings.GRID_SIZE[1] or 1)
    max_battery = float(settings.MAX_BATTERY or 1)

    vector: List[float] = []
    for position, battery, carrying in zip(
        observation["drones"],
        observation["batteries"],
        observation["cargos"],
    ):
        vector.extend(
            [
                position[0] / rows,
                position[1] / cols,
                battery / max_battery,
                float(carrying),
            ]
        )

    expected = observation_size()
    if len(vector) < expected:
        vector.extend([0.0] * (expected - len(vector)))
    return vector[:expected]
