"""
Structured logging configuration.
"""

import logging
import sys
from typing import Optional

from app.core.config import settings


def setup_logging(module_name: str) -> logging.Logger:
    """
    Configure structured logging for a module.

    Args:
        module_name: Name of the module to log for

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(module_name)

    # Only configure root logger once
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt=(
                "%(asctime)s - %(name)s - %(levelname)s - "
                "%(funcName)s:%(lineno)d - %(message)s"
            ),
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name (defaults to caller module)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name or __name__)
