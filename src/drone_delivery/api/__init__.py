"""FastAPI application exposing the simulation over HTTP."""

from drone_delivery.api.server import app, create_app

__all__ = ["app", "create_app"]
