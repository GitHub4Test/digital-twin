"""
Package initialization
"""
import logging
import os

log_level = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=log_level,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler()          # only stdout/stderr
    ]
)

logger = logging.getLogger("digital_twin_app")
logger.info("Digital Twin App package initialized")
