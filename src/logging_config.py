"""
This module provides centralized configuration for logging in Python applications.
It includes a custom colored formatter and a function to setup and retrieve logger instances.
"""

import logging
from colorlog import ColoredFormatter

# Define colors for different log levels
log_colors = {
    'DEBUG': 'white',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}

# Custom formatter with colored output
formatter = ColoredFormatter(
    '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S',
    log_colors=log_colors,
)


def setup_logger(logger_name):
    """
    Setup a logger instance with the specified name using the configured ColoredFormatter.

    Args:
        logger_name (str): Name of the logger instance.

    Returns:
        logging.Logger: Configured logger instance.
    """

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(logger_name)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)  # set the desired logging level here

    return logger
