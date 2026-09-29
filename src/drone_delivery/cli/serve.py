"""``drone-api`` - serve the HTTP API with uvicorn."""

from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence

from drone_delivery.config import settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="drone-api",
        description="Run the drone delivery HTTP API.",
    )
    parser.add_argument(
        "--host", default=settings.API_HOST, help="bind address (default: %(default)s)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=settings.API_PORT,
        help="bind port (default: %(default)s)",
    )
    parser.add_argument("--reload", action="store_true", help="enable auto-reload")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    import uvicorn

    if args.reload:
        uvicorn.run("drone_delivery.api.server:app", host=args.host, port=args.port, reload=True)
    else:
        from drone_delivery.api.server import app

        uvicorn.run(app, host=args.host, port=args.port)

    return 0


if __name__ == "__main__":
    sys.exit(main())
