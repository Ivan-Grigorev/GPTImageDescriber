"""Provides centralized logging configuration for Python applications."""

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
detailed_formatter = ColoredFormatter(
    '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S',
    log_colors=log_colors,
)

# Custom formatter with colored output for simple messages
simple_formatter = ColoredFormatter('%(log_color)s%(message)s', log_colors=log_colors)


def setup_logger(logger_name, use_simple_formatter=False):
    """
    Set up a logger instance with the specified name using the configured ColoredFormatter.

    Args:
        logger_name (str): The name of the logger instance.
        use_simple_formatter (bool): Whether to use the simple formatter.

    Returns:
        logging.Logger: The configured logger instance.
    """
    handler = logging.StreamHandler()

    if use_simple_formatter:
        handler.setFormatter(simple_formatter)
    else:
        handler.setFormatter(detailed_formatter)

    logger = logging.getLogger(logger_name)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)  # set the desired logging level here

    return logger
