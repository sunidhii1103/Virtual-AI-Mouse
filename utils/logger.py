"""Centralized logging configuration for the Virtual AI Mouse application.

This module provides setup functions to initialize the global logging configuration,
ensuring consistent formatting, stream handlers, and debug level controls across
all modules.
"""

import logging
import sys


def setup_logging(debug_mode: bool = False) -> None:
    """Sets up the root logger configuration with standard formatting.

    Args:
        debug_mode: If True, sets the log level to DEBUG. Otherwise, defaults to INFO.
    """
    log_level = logging.DEBUG if debug_mode else logging.INFO
    log_format = "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"

    # Reset any existing handlers to prevent duplicate logs
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)

    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)
