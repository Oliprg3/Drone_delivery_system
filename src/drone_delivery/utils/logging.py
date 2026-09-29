"""Logging configuration."""

from __future__ import annotations

import logging
import sys

from drone_delivery.config import settings

LOG_FORMAT = "%(asctime)s | %(name)-18s | %(levelname)-8s | %(message)s"


def setup_logger(name: str = "drone_delivery") -> logging.Logger:
    """Return a configured logger with a single stdout handler.

    Safe to call repeatedly: the handler is only attached once, so calling this
    on every access does not duplicate log lines.
    """
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL.upper())
    logger.propagate = False

    if not any(getattr(h, "_drone_delivery", False) for h in logger.handlers):
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        handler._drone_delivery = True  # type: ignore[attr-defined]
        logger.addHandler(handler)

    return logger


def get_logger(name: str = "drone_delivery") -> logging.Logger:
    """Return a child logger of the package root logger."""
    return logging.getLogger(name)
