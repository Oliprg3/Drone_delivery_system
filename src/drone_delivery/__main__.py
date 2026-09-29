"""``python -m drone_delivery`` - start the API or a simulation run.

Dispatches on the ``API_ENABLED`` setting: run uvicorn when it is true,
otherwise run a headless simulation. This replaces the old top-level
``main.py``.
"""

from __future__ import annotations

import sys

from drone_delivery.config import settings


def main() -> int:
    if settings.API_ENABLED:
        import uvicorn

        from drone_delivery.api.server import app

        uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
        return 0

    from drone_delivery.cli.run_simulation import main as run_simulation

    return run_simulation()


if __name__ == "__main__":
    sys.exit(main())
