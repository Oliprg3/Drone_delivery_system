import logging
import sys
from config import settings

def setup_logger(name: str = "drone_sim") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    return logger
