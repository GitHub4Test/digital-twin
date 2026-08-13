"""
Package initialization
"""

# src/edge_server/__init__.py
import logging
import os

log_level = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()  # only stdout/stderr
    ],
)

logger = logging.getLogger("edge_server")
logger.info("Logger initialized")
